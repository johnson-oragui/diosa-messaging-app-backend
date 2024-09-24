from fastapi import status, HTTPException, Request
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
import hashlib

from app.core.config import settings
from app.utils.task_logger import create_logger

logger = create_logger("Auth Dpenedencies")

async def generate_idempotency_key(email: str, username: str) -> str:
    """Creates an idempotency key
    
    Keyword arguments:
        email(str) -- user email
        username(str) -- username
    Return: Idempotency_key(str)
    """
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
        expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)
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
    return token


async def verify_access_token(token: str, request: Request) -> str:
    """Verifies/Decodes access token.
    
    Keyword arguments:
        token(str) -- token to verify
        request(Request) -- request object
    Return: user_id
    """
    
    try:
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

async def verify_refresh_token(token: str, request: Request) -> str:
    """Verifies/Decodes refresh token.
    
    Keyword arguments:
        token(str) -- token to verify
        request(Request) -- request object
    Return: user_id
    """
    
    try:
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
