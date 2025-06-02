"""
AuthenticationService module
"""

import typing
from uuid import uuid4
from datetime import datetime, timedelta

from fastapi import status, HTTPException, Request, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from asyncpg.exceptions import IntegrityConstraintViolationError

from app.dto.v1.authentication_dto import (
    RegisterUserRequestDto,
    RegisterOutputResponseDto,
    UserBaseDto,
    AuthenticateUserRequestDto,
    AuthenticationBaseDto,
    AccessTokenDto,
    AuthenticateUserResponseDto,
    LogoutResponseDto,
)
from app.repository.v1.user_repository import (
    user_repository,
)
from app.repository.v1.user_session_repository import (
    user_session_repository,
)
from app.utils.task_logger import create_logger
from app.core.config import settings
from app.core.security import generate_token

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
        token = await generate_token(
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
        refresh_token = await generate_token(
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

    async def logout(
        self, request: Request, session: AsyncSession
    ) -> typing.Union[LogoutResponseDto, None]:
        """
        Logs out a user.
        """
        session_id = request.state.claims.get("session_id")
        await user_session_repository.log_session_out(session_id, session=session)
        return LogoutResponseDto()


authentication_service = AuthenticationService()
