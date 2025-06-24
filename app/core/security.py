"""
COnfig security module
"""

import typing
from datetime import datetime, timezone, timedelta

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, Request, HTTPException, Header, WebSocket
from jose import jwt, JWTError
import sqlalchemy as sa

from app.core.config import settings
from app.utils.task_logger import create_logger
from app.database.session import get_async_session, AsyncSession
from app.models.user_session import UserSession

logger = create_logger(":: SECURITY CONFIG ::")

http_bearer_security = HTTPBearer(
    bearerFormat="JWT",
    scheme_name="BearerAuth",
    description="JWT Bearer authentication",
    auto_error=False,
)

RequestCredentials = typing.Annotated[
    HTTPAuthorizationCredentials, Depends(http_bearer_security)
]

Session = typing.Annotated[AsyncSession, Depends(get_async_session)]


async def set_current_user_claims_from_token(
    credential: RequestCredentials, request: Request
) -> None:
    """
    Uses DI to Validates auth bearer and sets claims to request
    """
    if not credential:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    token = credential.credentials
    scheme = credential.scheme
    if scheme != "Bearer":
        raise HTTPException(
            status_code=401, detail="Authorization Bearer scheme required"
        )

    claims = await verify_jwt_tokens(token, "access")

    request.state.claims = claims
    request.state.current_user = claims.get("user_id")


async def validate_logout_status(
    credential: RequestCredentials, request: Request, session: Session
) -> None:
    """
    Uses DI to Validates auth bearer, log out status and sets claims to request.
    """
    if not credential:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    token = credential.credentials
    scheme = credential.scheme
    if scheme != "Bearer":
        raise HTTPException(
            status_code=401, detail="Authorization Bearer scheme required"
        )

    claims = await verify_jwt_tokens(token, "access")

    is_not_logged_in = (
        await session.execute(
            sa.select(UserSession).where(
                UserSession.session_id == claims.get("session_id"),
                UserSession.is_logged_out.is_(False),
            )
        )
    ).scalar_one_or_none()

    if not is_not_logged_in:
        raise HTTPException(status_code=401, detail="session expired")

    if claims.get("jti") != is_not_logged_in.jti:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    request.state.claims = claims
    request.state.current_user = claims.get("user_id")


async def get_refresh_token_header(
    request: Request,
    x_refresh_token: str = Header(title="X-REFRESH-TOKEN"),
) -> None:
    """
    Retrieves refresh token from header
    """
    # refresh_token_header = request.headers.get("x-refresh-token", None) or ""
    if not x_refresh_token:
        raise HTTPException(status_code=401, detail="Missing X-REFRESH-TOKEN Header")

    claims = await verify_jwt_tokens(x_refresh_token, "refresh")

    request.state.claims = claims
    request.state.current_user = claims.get("user_id")


async def generate_token(
    session_id: str,
    user_id: str,
    jti: str,
    user_agent: str,
    ip_address: str,
    location: str,
    token_type: str = "access",
) -> str:
    """
    Generates jwt token.

    Args:
        session_id(str): The session_id to be addd to claims
        user_id(str): The user id to be addd to claims
        jti(str): The jti to be addd to claims
        user_agent(str): The user agent to be addd to claims
        ip_address(str): The ip address to be addd to claims
        location(str): The current user location to be addd to claims
        token_type(str): The type of token to be generated (access, refresh)
    """
    now = datetime.now(timezone.utc)
    expire = now
    if token_type == "access":
        expire = now + timedelta(days=settings.jwt_access_token_expiry)
    elif token_type == "refresh":
        expire = now + timedelta(days=settings.jwt_refresh_token_expiry)
    else:
        raise TypeError("token type can only be one of access or refresh")
    claims = {
        "user_id": user_id,
        "jti": jti,
        "session_id": session_id,
        "user_agent": user_agent,
        "token_type": token_type,
        "ip_address": ip_address,
        "location": location,
        "exp": expire,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }

    token: str = jwt.encode(
        claims=claims, key=settings.jwt_secrets, algorithm=settings.jwt_algorithm
    )

    return token


async def verify_jwt_tokens(
    token: str, token_type: str = "access"
) -> typing.Dict[str, typing.Any]:
    """
    Verifies jwt tokens.

    Args:
        token(str): the jwt token to verify.
        token_type(str): The type of token to be verified (access, refresh)
    Returns:
        claims (Dict[str, Any]): the claims of the decoded token
    """
    if token_type not in ["access", "refresh"]:
        raise TypeError("token type must be either access or refresh")
    try:
        claims = jwt.decode(
            token=token,
            key=settings.jwt_secrets,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
        )
        if claims.get("token_type", None) != token_type:
            raise HTTPException(status_code=401, detail="Invalid token type")
        return claims
    except JWTError as exc:
        logger.error("Error verifying jwt token: %s", str(exc))
        raise HTTPException(
            status_code=401, detail=f"{token_type} token validation failed"
        ) from exc


async def validate_ws_logout_status(
    session: Session,
    websocket: WebSocket,
    Authorization: str = Header(
        description="Authorization header", title="Authorization"
    ),
) -> None:
    """
    Uses DI to Validates auth bearer, log out status and sets claims to request.
    """
    if not Authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not isinstance(Authorization, str):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    scheme, token = Authorization.split(" ")
    if scheme != "Bearer":
        raise HTTPException(
            status_code=401, detail="Authorization Bearer scheme required"
        )

    claims = await verify_jwt_tokens(token, "access")

    is_not_logged_in = (
        await session.execute(
            sa.select(UserSession).where(
                UserSession.session_id == claims.get("session_id"),
                UserSession.is_logged_out.is_(False),
            )
        )
    ).scalar_one_or_none()

    if not is_not_logged_in:
        raise HTTPException(status_code=401, detail="session expired")

    if claims.get("jti") != is_not_logged_in.jti:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    websocket.state.claims = claims
    websocket.state.current_user = claims.get("user_id")
