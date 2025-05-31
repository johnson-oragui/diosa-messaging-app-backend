import redis
from uuid import uuid4
from typing import Optional, Tuple, Union, Annotated, Dict, Any
import hashlib
import hmac
from datetime import timedelta, datetime, timezone, date
import json
import dns.resolver
import random
import string

from fastapi import Header, status, HTTPException, Request, Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.utils.task_logger import create_logger

oauth2_scheme = HTTPBearer()

logger = create_logger("::AUTH DEPENDENCY::")


async def get_refresh_token(
    request: Request, x_refresh_token: str = Header(...)
) -> Optional[dict]:
    """
    Dependency to fetch and validate x-refresh-token from headers.
    """
    if not x_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="x-refresh-token header missing",
        )

    # Validate the token
    try:
        return await verify_token(x_refresh_token, request, "refresh")
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from exc


async def verify_token(
    token: str, request: Request, token_type: str
) -> Optional[Dict[str, Any]]:
    """Verifies/Decodes jwt token.

    Args:
        token(str): token to verify
        request(Request): request object
        token_type(str): The type of token to be decoded.
    Return:
        claims(dict): the decode token.
    """
    if isinstance(token, HTTPAuthorizationCredentials):
        token = token.credentials

    try:
        claims: dict = jwt.decode(
            token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
        )
        decoded_token_type = claims.get("type")

        # check for token type.
        if token_type == "access":
            if decoded_token_type != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Access Token.",
                )
            try:
                async with get_redis_async() as redis_client:
                    device_id = claims.get("device_id")
                    jti = claims.get("jti")
                    token_data = await redis_client.get(
                        f"token:{device_id}",
                    )
                    if not token_data or token_data != jti:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Access Token",
                        )
            except redis.ConnectionError:
                logger.error("Redis unavailable, decoded token device_id not fetched.")

        # check for token type.
        if token_type == "refresh":
            if decoded_token_type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Refresh Token.",
                )

        # check for token type.
        if token_type == "email_verification":
            if decoded_token_type != "email_verification":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email_verification Token.",
                )

        if token_type != "email_verification":
            request.state.current_user = claims.get("user_id")
            user_agent = request.headers.get("user-agent")
            if user_agent != claims.get("user_agent"):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        return claims
    except JWTError as exc:
        logger.error(msg=f"JWTError: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Invalid or Expired"
        ) from exc
