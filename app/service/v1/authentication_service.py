"""
AuthenticationService module
"""

import typing
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from fastapi import status, HTTPException, Request, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from asyncpg.exceptions import IntegrityConstraintViolationError
from jose import jwt

from app.dto.v1.authentication_dto import (
    RegisterUserRequestDto,
    RegisterOutputResponseDto,
    UserBaseDto,
    AuthenticateUserRequestDto,
    AuthenticationBaseDto,
    AccessTokenDto,
    AuthenticateUserResponseDto,
)
from app.repository.v1.user_repository import (
    user_repository,
)
from app.repository.v1.user_session_repository import (
    user_session_repository,
)
from app.utils.task_logger import create_logger
from app.core.config import settings

logger = create_logger(":: Authentication Service ::")


class AuthenticationService:
    """
    Authentication Service
    """

    async def register_new_user(
        self, schema: RegisterUserRequestDto, session: AsyncSession
    ) -> typing.Optional[RegisterOutputResponseDto]:
        """
        Registers a new User
        """
        user_exists = await user_repository.fetch_by_idempotency_key(
            schema.idempotency_key, session=session
        )

        if user_exists:
            return RegisterOutputResponseDto(
                data=UserBaseDto.model_validate(user_exists, from_attributes=True),
                message="User already Registered",
            )
        try:

            new_user = await user_repository.create(
                None,
                None,
                schema.email,
                schema.password,
                None,
                None,
                schema.idempotency_key,
                False,
                session=session,
            )
            return RegisterOutputResponseDto(
                data=UserBaseDto.model_validate(new_user, from_attributes=True)
            )
        except (IntegrityConstraintViolationError, IntegrityError) as exc:
            logger.error(str(exc.args))
            raise HTTPException(
                status.HTTP_409_CONFLICT, detail="Email already in use"
            ) from exc

    async def authenticate(
        self,
        schema: AuthenticateUserRequestDto,
        request: Request,
        response: Response,
        session: AsyncSession,
    ) -> typing.Union[AuthenticateUserResponseDto, None]:
        """
        Authenticates a user
        """
        user_exists = await user_repository.fetch_by_username_or_email(
            str(schema.email), schema.username, session=session
        )
        if not user_exists:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        if not user_exists.verify_password(schema.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        user_session_exists = await user_session_repository.fetch(
            None, None, schema.session_id, None, session=session
        )
        if user_session_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="session_id must be unique. use a uuidv4",
            )
        # ip address
        ip_address = request.headers.get("x-forwarded-for", None) or (
            request.client and request.client.host or None
        )
        # user_agent
        user_agent = request.headers.get("user-agent", "")
        # location
        location = "unknown"
        # jti
        new_jti = str(uuid4())

        # access token
        token = await self.generate_token(
            user_agent=user_agent,
            user_id=user_exists.id,
            jti=new_jti,
            session_id=schema.session_id,
            location=location,
            ip_address=(ip_address or "Unknown"),
        )
        # expire at
        access_token_dto = AccessTokenDto(
            token=token,
            expire_at=int(
                (
                    datetime.now() + timedelta(days=settings.jwt_access_token_expiry)
                ).timestamp()
            ),
        )

        # refresh token
        refresh_token = await self.generate_token(
            user_agent=user_agent,
            user_id=user_exists.id,
            jti=new_jti,
            session_id=schema.session_id,
            location=location,
            ip_address=(ip_address or "Unknown"),
            token_type="refresh",
        )
        # set header x-refresh-token
        response.headers["X-REFRESH-TOKEN"] = refresh_token

        # new user session record
        await user_session_repository.create(
            user_id=user_exists.id,
            jti=new_jti,
            location=location,
            ip_address=(ip_address or ""),
            session_id=schema.session_id,
            session=session,
        )

        # set current_user for loggin purposes.
        request.state.current_user = user_exists.id

        user_base_dto = UserBaseDto.model_validate(user_exists, from_attributes=True)

        authentication_base_dto = AuthenticationBaseDto(
            access_token=access_token_dto, user_data=user_base_dto
        )

        return AuthenticateUserResponseDto(data=authentication_base_dto)

    async def generate_token(
        self,
        session_id: str,
        user_id: str,
        jti: str,
        user_agent: str,
        ip_address: str,
        location: str,
        token_type: str = "access",
    ) -> str:
        """
        Generates jwt token
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
            "iss": "chat.johnson.com",
            "aud": "1234567890.chat.johnson.com",
        }

        token: str = jwt.encode(
            claims=claims, key=settings.jwt_secrets, algorithm=settings.jwt_algorithm
        )

        return token


authentication_service = AuthenticationService()
