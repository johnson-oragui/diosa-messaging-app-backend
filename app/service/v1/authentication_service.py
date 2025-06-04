"""
AuthenticationService module
"""

import typing
from uuid import uuid4
from datetime import datetime, timedelta
import string
import random

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
    RefreshTokenResponseDto,
    PasswordChangeRequestDto,
    PasswordChangeResponseDto,
    PasswordResetInitRequestDto,
    PasswordResetInitResponseDto,
    PasswordResetResponseDto,
    PasswordResetRequestDto,
    AccountVerificationResponseDto,
    AccountVerificationRequestDto,
    ResendVerificationCodeResponseDto,
    AccountDeletionResponseDto,
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
from app.database.redis_db import get_redis_async
from app.utils.celery_setup.tasks import send_email_in_background

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
            async with get_redis_async() as redis_session:  # type: ignore
                key = f"chat:email-verification:{schema.email}"
                code = await self.generate_six_digit_code()
                await redis_session.set(key, value=code, ex=(5 * 60))
                context = {
                    "token": code,
                    "recipient_email": schema.email,
                    "subject": "Email Verification",
                    "template_name": "email-verification.html",
                }
                await self.send_email(context)
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
        if not user_exists.email_verified:
            raise HTTPException(status_code=403, detail="Email not verified yet")
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
        # TODO: add util function to fetch location
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

        Args:
            request(Request): The request object.
            session (AsyncSession): The database async session
        Returns:
            response
        """
        session_id = request.state.claims.get("session_id")
        await user_session_repository.log_session_out(session_id, session=session)
        return LogoutResponseDto()

    async def refresh_token(
        self, request: Request, session: AsyncSession, response: Response
    ) -> typing.Union[RefreshTokenResponseDto, None]:
        """
        Refreshes user tokens.

        Args:
            request(Request): The request object.
            session (AsyncSession): The database async session
        Returns:
            response
        """
        claims = request.state.claims
        jti = claims.get("jti")
        session_id = claims.get("session_id")
        user_id = claims.get("user_id")
        user_agent = claims.get("user_agent")
        location = claims.get("location")
        ip_address = claims.get("ip_address")

        if user_agent != request.headers.get("user-agent"):
            raise HTTPException(status_code=401, detail="Unauthorized access")

        user_sessio_exists = await user_session_repository.fetch(
            user_id=user_id,
            jti=jti,
            session_id=session_id,
            is_logged_out=False,
            session=session,
        )
        if not user_sessio_exists:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        new_jti = str(uuid4())

        new_access_token = await generate_token(
            session_id=session_id,
            user_id=user_id,
            jti=new_jti,
            user_agent=user_agent,
            token_type="access",
            location=location,
            ip_address=ip_address,
        )
        new_refresh_token = await generate_token(
            session_id=session_id,
            user_id=user_id,
            jti=new_jti,
            user_agent=user_agent,
            token_type="refresh",
            location=location,
            ip_address=ip_address,
        )

        await user_session_repository.update_jti(
            session=session, session_id=session_id, jti=new_jti
        )

        access_token_dto = AccessTokenDto(
            token=new_access_token,
            expire_at=int(
                (
                    datetime.now() + timedelta(days=settings.jwt_access_token_expiry)
                ).timestamp()
            ),
        )
        response.headers["X-REFRESH-TOKEN"] = new_refresh_token
        return RefreshTokenResponseDto(data=access_token_dto)

    async def change_password(
        self, request: Request, schema: PasswordChangeRequestDto, session: AsyncSession
    ) -> typing.Union[PasswordChangeResponseDto, None]:
        """
        Password change.

        Args:
            request(Request): The request object.
            schema(PasswordChangeRequestDto): The request payload
            session(AsyncSession): The database async session object
        Returns:
            PasswordChangeResponseDto: response payload
        """
        claims: dict = request.state.claims

        is_updated = await user_repository.update_password(
            session=session,
            user_id=claims.get("user_id", ""),
            new_password=schema.new_password,
            old_password=schema.old_password,
        )

        if not is_updated:
            raise HTTPException(status_code=400, detail="Invalid credentials")

        return PasswordChangeResponseDto()

    async def initiate_reset_password(
        self, schema: PasswordResetInitRequestDto, session: AsyncSession
    ) -> typing.Union[PasswordResetInitResponseDto, None]:
        """
        Initiates User password reset.

        Args:
            request(Request): The request object.
            schema(PasswordResetInitRequestDto): The request payload
            session(AsyncSession): The database async session object
        Returns:
            PasswordResetInitResponseDto: response payload
        """
        email_exists = await user_repository.fetch_by_email(
            email=schema.email, session=session
        )
        if not email_exists:
            raise HTTPException(status_code=404, detail="Email not found")

        reset_code = await self.generate_six_digit_code()
        key = f"chat:password-reset-code:{schema.email}"
        async with get_redis_async() as redis_async:  # type: ignore
            await redis_async.set(name=key, value=reset_code, ex=(5 * 60))
        context = {
            "token": reset_code,
            "recipient_email": schema.email,
            "subject": "Password Reset",
            "template_name": "password-reset.html",
        }
        await self.send_email(context)

        return PasswordResetInitResponseDto()

    async def reset_password(
        self, schema: PasswordResetRequestDto, session: AsyncSession
    ) -> typing.Union[PasswordResetResponseDto, None]:
        """
        Resets User password.

        Args:
            request(Request): The request object.
            schema(PasswordResetRequestDto): The request payload
            session(AsyncSession): The database async session object
        Returns:
            PasswordResetResponseDto: response payload
        """
        code = None
        key = f"chat:password-reset-code:{schema.email}"
        async with get_redis_async() as redis_async:  # type: ignore

            code = await redis_async.get(key)
            if not code:
                raise HTTPException(status_code=401, detail="code expired or invalid")
            user = await user_repository.fetch_by_email(
                email=schema.email, session=session
            )
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            await user_repository.set_new_password(
                new_password=schema.password, session=session, user=user
            )
            context = {
                "recipient_email": schema.email,
                "subject": "Successful Password Reset",
                "template_name": "password-reset-success.html",
            }
            await self.send_email(context)

            await redis_async.delete(key)

        return PasswordResetResponseDto()

    async def verify_account(
        self, schema: AccountVerificationRequestDto, session: AsyncSession
    ) -> typing.Union[AccountVerificationResponseDto, None]:
        """
        Verifies user accounts.

        Args:
            schema(PasswordResetRequestDto): The request payload
            session(AsyncSession): The database async session object
        Returns:
            AccountVerificationResponseDto: response payload
        """
        key = f"chat:email-verification:{schema.email}"
        async with get_redis_async() as redis_session:  # type: ignore
            code = await redis_session.get(key)

            if code != schema.code:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            user = await user_repository.fetch_by_email(
                email=schema.email, session=session
            )
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            await user_repository.verify_user(session=session, user=user)

            await redis_session.delete(key)

            await session.refresh(user)

        return AccountVerificationResponseDto()

    async def resend_verification_code(
        self, schema: PasswordResetInitRequestDto, session: AsyncSession
    ) -> typing.Union[ResendVerificationCodeResponseDto, None]:
        """
        Resends account verification code after 5 minutes.

        Args:
            schema(PasswordResetRequestDto): The request payload
            session(AsyncSession): The database async session object
        Returns:
            ResendVerificationCodeResponseDto: response payload
        """
        key = f"chat:email-verification:{schema.email}"
        code = None
        async with get_redis_async() as redis_session:  # type: ignore
            code = await redis_session.get(key)
            if code:
                raise HTTPException(
                    status_code=409, detail="Verification code is not expired"
                )
            user = await user_repository.fetch_by_email(schema.email, session=session)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            new_code = await self.generate_six_digit_code()
            await redis_session.set(name=key, value=new_code, ex=(5 * 60))

        return ResendVerificationCodeResponseDto()

    async def account_deletion(
        self, session: AsyncSession, request: Request
    ) -> typing.Union[AccountDeletionResponseDto, None]:
        """
        Deletes User account.

        Args:
            request(Request): The request object.
            session(AsyncSession): The database async session object
        Returns:
            AccountDeletionResponseDto: response payload

        """
        claims: dict = request.state.claims
        user_exists = await user_repository.fetch_by_id(
            user_id=claims.get("user_id", ""), session=session
        )
        if not user_exists:
            raise HTTPException(status_code=404, detail="User not found")
        await user_repository.delete(user=user_exists, session=session)
        return AccountDeletionResponseDto()

    async def send_email(self, context: dict) -> None:
        """
        Sends email.

        Args:
            context(dict): The vars for email sending.
        Returns:
            None
        """
        send_email_in_background.delay(context)  # type: ignore

    async def generate_six_digit_code(self) -> str:
        """
        Generates six digit code
        """
        code_list = [random.choice(string.digits) for _ in range(6)]
        return "".join(code_list)


authentication_service = AuthenticationService()
