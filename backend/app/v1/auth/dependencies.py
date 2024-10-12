from typing import Optional, Tuple, Union
from fastapi import (
    status,
    HTTPException,
    Request,
    Cookie,
    Header,
    WebSocket,
)
from fastapi.responses import RedirectResponse, JSONResponse
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
import hashlib
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.utils.task_logger import create_logger
from app.v1.users.services import user_service
from app.v1.users import User

logger = create_logger("Auth Dpenedencies")

oauth2_scheme: OAuth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

async def generate_idempotency_key(email: str, username: str) -> str:
    """Creates an idempotency key
    
    Keyword arguments:
        email(str) -- user email
        username(str) -- username
    Return: Idempotency_key(str)
    """
    if not email or not username:
        raise Exception("email or username cannot be None")
    key = f"{email}:{username}"
    idempotency_key: str = hashlib.sha256(key.encode()).hexdigest()
    return idempotency_key


async def generate_jwt_token(data: dict, token_type: str = "access") -> str:
    """Generates jwt token.
    
    Keyword arguments:
        data(dict) -- contains user_id, user_agent, user_ip
        token_type(str) -- the token type to generate
    Return: token(str) generated
    """
    
    now = datetime.now(timezone.utc)
    if token_type == "refresh":
        expire = now + timedelta(days=settings.jwt_refresh_token_expire_days)
    elif token_type == "access":
        expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    else:
        raise Exception("token type must only be access or refresh")
    claims = {
        "user_id": data.get("user_id"),
        "user_agent": data.get("user_agent"),
        "user_ip": data.get("user_ip"),
        "exp": expire,
        "type": token_type
    }

    token: str = jwt.encode(
        claims=claims,
        key=settings.secrets,
        algorithm=settings.jwt_algorithm
    )
    logger.info(msg=f"token: {token}")
    return token

async def generate_access_and_refresh(user_id: str, request: Union[WebSocket, Request]) -> Tuple[str, str]:
        """
        Generates both access and refresh tokens.

        Args:
            user_id(str): id of the user.
            request: request object
        Returns:
            tuple(access_token, refresh_token): generated access and refresh tokens
        """
        if isinstance(request, WebSocket):
            pass
        access_token = await generate_jwt_token({
            "user_id": user_id,
            "user_agent": request.headers.get("user-agent"),
            "user_ip": request.client.host
        })

        refresh_token = await generate_jwt_token({
            "user_id": user_id,
            "user_agent": request.headers.get("user-agent"),
            "user_ip": request.client.host
        }, token_type="refresh")

        return access_token, refresh_token

async def verify_access_token(token: str, request: Union[WebSocket, Request]) -> str:
    """Verifies/Decodes access token.
    
    Keyword arguments:
        token(str) -- token to verify
        request(Request) -- request object
    Return: user_id
    """
    try:
        if isinstance(request, WebSocket):
            pass
        claims: dict = jwt.decode(
            token,
            key=settings.secrets,
            algorithms=[settings.jwt_algorithm]
        )
        user_ip = request.client.host
        user_agent = request.headers.get("user-agent")
        user_id: str = claims.get("user_id", '')
        token_type = claims.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cannot Use Refresh Token"
            )

        if user_agent != claims.get("user_agent") or user_ip != claims.get("user_ip"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return user_id
    except JWTError as exc:
        logger.error(
            msg=f"JWTError: {exc}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )

async def verify_refresh_token(token: str, request: Union[WebSocket, Request]) -> str:
    """Verifies/Decodes refresh token.
    
    Keyword arguments:
        token(str) -- token to verify
        request(Request) -- request object
    Return: user_id
    """
    try:
        if isinstance(request, WebSocket):
            pass
        claims: dict = jwt.decode(
            token,
            key=settings.secrets,
            algorithms=[settings.jwt_algorithm]
        )
        user_ip = request.client.host
        user_agent = request.headers.get("user-agent")
        user_id: str = claims.get("user_id", '')
        token_type = claims.get("type")
        if token_type != "refrsh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cannot Use Access Token"
            )
        if user_agent != claims.get("user_agent") or user_ip != claims.get("user_ip"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return user_id
    except JWTError as exc:
        logger.error(
            msg=f"JWTError: {exc}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )

async def check_for_access_token(access_token: Optional[str] = Cookie(None),
                                 Authorization: Optional[str] = Header(None)) -> Optional[str]:
    """
    Checks for token in cookies, if not present, checks for token in header.

    Args:
        access_token(str): token from cookie.
        Authorization(str): token from header.
    Returns:
        token(str): if found, None if not found.
    """
    token = None
    logger.info(msg=f"access_token: {access_token}, authorization: :{Authorization}")
    if access_token:
        token = access_token
        logger.info(msg=f"access_token: {access_token}")
    elif Authorization:
        logger.info(msg=f"Authorization: {Authorization}")
        try:
            token_type, token_value = Authorization.split(" ")
            if token_type.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Token Type"
                )
            if not token_value or token_value.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token Cannot be Null"
                )
            token = token_value
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authentication Header"
            )
    else:
        # If no token is found in both places, raise an exception
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not provided"
        )
    return token

async def check_refresh_token(refresh_token: Optional[str] = Cookie(None),
                              Authorization: Optional[str] = Header(None)) -> Optional[str]:
    """
    Checks for refresh token in the cookies.

    Args:
        refresh_token(str): refresh_token from cookie.
        Authorization(str): refresh_token from header.
    Returns:
        token(str): if found, None if not found.
    """
    token = None
    if refresh_token:
        token = refresh_token
    elif Authorization:
        try:
            token_type, token_value = Authorization.split(" ")
            if token_type.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Refresh-Token Type"
                )
            if not token_value or token_value.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh-Token Cannot be Null"
                )
            token = token_value
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authentication Header"
            )
    else:
        # If no token is found in both places, raise an exception
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh-Token not provided"
        )
    return token

async def authenticate_user(schema: dict, session: AsyncSession) -> Optional[User]:
        """
        Authenticates a user's email/username and password.

        Args:
            schema(dict): username/email and password.
            session: Database session object.
        Returns:
            user(object): The user if authentication is successful
        Raise:
            HTTPException: if authentication is unsuccessful.
        """
        user = await user_service.fetch_by_email_or_user_name({
            "email": schema.get("username", ""),
            "username": schema.get("username", "")
        }, session)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid username/email or password"
            )

        if user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive"
            )
        
        is_valid_password = user.verify_password(schema.get("password"))
        if not is_valid_password:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid username/email or password"
            )
        return user

async def get_current_user(
        access_token: str,
        request: Union[Request, WebSocket],
        session: AsyncSession
    ) -> Optional[User]:
        """
        Retrieves the current user using the access_token.

        Args:
            access_token(str): access_token of the user.
            request(Object): request object.
            session(object): database session object.
        Returns:
            USER(object): if access_token is valid.
        Raises:
            HTTPException: If user not found.
        """
        user_id: str = await verify_access_token(access_token, request)

        user = await user_service.fetch({"id": user_id}, session)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found."
            )
        return user

async def get_current_active_user(
        access_token: str,
        request: Union[Request, WebSocket],
        session: AsyncSession
    ) -> Optional[User]:
        """Retrieves the current-active user using the access_token.

        Args:
            access_token(str): access_token of the user.
            request(Object): request object.
            session(object): database session object.
        Returns:
            USER(object): if access_token is valid.
        Raises:
            HTTPException: If user is not active.

        """
        user: User | None = await get_current_user(access_token, request, session)
        if user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive"
            )
        return user

async def set_cookies(response: Union[JSONResponse, RedirectResponse],
                      access_token: str, refresh_token: str) -> Union[JSONResponse, RedirectResponse]:
    """
    Sets cookies using access and refresh tokens.
    Args:
        response(object): the response object to set the cookies on.
        access_token(str): the access token
        refresh_token(str): the refresh token.
    Returns:
        response(object): response object.
    """
    response.set_cookie(
        key="access_token",
            value=access_token,
            max_age=60 * settings.jwt_access_token_expire_minutes,
            secure=False,
            httponly=True,
            samesite="lax"
        )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.jwt_refresh_token_expire_days * 24 * 60 * 60,
        secure=False,
        httponly=True,
        samesite="strict"
    )
    return response
