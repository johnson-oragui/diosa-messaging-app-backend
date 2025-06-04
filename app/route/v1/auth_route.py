"""
Authentication Route Module
"""

import typing
from fastapi import APIRouter, status, Request, Response, Depends

from app.utils.task_logger import create_logger
from app.utils.responses import responses
from app.service.v1.authentication_service import authentication_service, AsyncSession
from app.dto.v1.authentication_dto import (
    RegisterUserRequestDto,
    RegisterOutputResponseDto,
    AuthenticateUserRequestDto,
    AuthenticateUserResponseDto,
    LogoutResponseDto,
    RefreshTokenResponseDto,
    PasswordChangeRequestDto,
    PasswordChangeResponseDto,
    PasswordResetInitRequestDto,
    PasswordResetInitResponseDto,
    PasswordResetRequestDto,
    PasswordResetResponseDto,
    AccountVerificationRequestDto,
    AccountVerificationResponseDto,
    ResendVerificationCodeResponseDto,
)
from app.database.session import get_async_session
from app.core.security import validate_logout_status, get_refresh_token_header

logger = create_logger("Auth Route")

auth_router = APIRouter(prefix="/auth", tags=["AUTHENTICATION"])


@auth_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses=responses,
    response_model=RegisterOutputResponseDto,
)
async def register_new_user(
    _: Request,
    schema: RegisterUserRequestDto,
    session: typing.Annotated[AsyncSession, Depends(get_async_session)],
) -> typing.Optional[RegisterOutputResponseDto]:
    """
    Endpoint for user registration with email and password.

    Args:
        schema: Request body containing email, password, and confirm_password
    Return:
        Success message upon successful registration
    Raises:
        422
        500
        409
    """
    return await authentication_service.register_new_user(
        schema=schema, session=session
    )


@auth_router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    responses=responses,
    response_model=AuthenticateUserResponseDto,
)
async def authenticate(
    request: Request,
    response: Response,
    schema: AuthenticateUserRequestDto,
    session: typing.Annotated[AsyncSession, Depends(get_async_session)],
) -> typing.Optional[AuthenticateUserResponseDto]:
    """
    Endpoint for authenticating users with email/username and password.

    Return:
        Success message upon successful registration
    Raises:
        422
        500
        409
    """
    return await authentication_service.authenticate(
        schema=schema, request=request, response=response, session=session
    )


@auth_router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    responses=responses,
    response_model=LogoutResponseDto,
    dependencies=[Depends(validate_logout_status)],
)
async def logout(
    request: Request,
    session: typing.Annotated[AsyncSession, Depends(get_async_session)],
) -> typing.Union[LogoutResponseDto, None]:
    """
    Logs out a user.

    Return:
        Success message upon successful logout
    Raises:
        401 Unauthorized.
        422 Validation Error.
        500 Internal server error
        409 conflict
    """
    return await authentication_service.logout(request=request, session=session)


@auth_router.post(
    "/refresh-tokens",
    status_code=status.HTTP_200_OK,
    responses=responses,
    response_model=RefreshTokenResponseDto,
    dependencies=[Depends(get_refresh_token_header)],
)
async def refresh_tokens(
    request: Request,
    response: Response,
    session: typing.Annotated[AsyncSession, Depends(get_async_session)],
) -> typing.Union[RefreshTokenResponseDto, None]:
    """
    Refreshes tokens.

    Return:
        Success message upon successful refresh
    Raises:
        401 Unauthorized.
        422 Validation Error.
        500 Internal server error
        409 conflict
    """
    return await authentication_service.refresh_token(
        request=request, session=session, response=response
    )


@auth_router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    responses=responses,
    response_model=PasswordChangeResponseDto,
    dependencies=[Depends(validate_logout_status)],
)
async def change_password(
    request: Request,
    session: typing.Annotated[AsyncSession, Depends(get_async_session)],
    schema: PasswordChangeRequestDto,
) -> typing.Union[PasswordChangeResponseDto, None]:
    """
    Changes passwords.

    Return:
        Success message upon successful change
    Raises:
        401 Unauthorized.
        422 Validation Error.
        500 Internal server error
        409 conflict
    """
    return await authentication_service.change_password(
        request=request, session=session, schema=schema
    )


@auth_router.post(
    "/password-reset-init",
    status_code=status.HTTP_200_OK,
    responses=responses,
    response_model=PasswordResetInitResponseDto,
)
async def initiate_password_reset(
    _: Request,
    session: typing.Annotated[AsyncSession, Depends(get_async_session)],
    schema: PasswordResetInitRequestDto,
) -> typing.Union[PasswordResetInitResponseDto, None]:
    """
    Initiates password  reset.

    Return:
        Success message upon successful change
    Raises:
        401 Unauthorized.
        422 Validation Error.
        500 Internal server error
        409 conflict
    """
    return await authentication_service.initiate_reset_password(
        session=session, schema=schema
    )


@auth_router.post(
    "/password-reset",
    status_code=status.HTTP_200_OK,
    responses=responses,
    response_model=PasswordResetResponseDto,
)
async def password_reset(
    _: Request,
    session: typing.Annotated[AsyncSession, Depends(get_async_session)],
    schema: PasswordResetRequestDto,
) -> typing.Union[PasswordResetResponseDto, None]:
    """
    Resets password.

    Return:
        Success message upon successful change
    Raises:
        401 Unauthorized.
        422 Validation Error.
        500 Internal server error
        409 conflict
    """
    return await authentication_service.reset_password(session=session, schema=schema)


@auth_router.post(
    "/verify-account",
    status_code=status.HTTP_200_OK,
    responses=responses,
    response_model=AccountVerificationResponseDto,
)
async def account_verification(
    _: Request,
    session: typing.Annotated[AsyncSession, Depends(get_async_session)],
    schema: AccountVerificationRequestDto,
) -> typing.Union[AccountVerificationResponseDto, None]:
    """
    Verifies account.

    Return:
        Success message upon successful verification
    Raises:
        401 Unauthorized.
        422 Validation Error.
        500 Internal server error
        409 conflict
    """
    return await authentication_service.verify_account(session=session, schema=schema)


@auth_router.post(
    "/resend-verification-code",
    status_code=status.HTTP_200_OK,
    responses=responses,
    response_model=ResendVerificationCodeResponseDto,
)
async def resend_verification_code(
    _: Request,
    session: typing.Annotated[AsyncSession, Depends(get_async_session)],
    schema: PasswordResetInitRequestDto,
) -> typing.Union[ResendVerificationCodeResponseDto, None]:
    """
    resends account verifucation code.

    Return:
        Success message upon successful resend
    Raises:
        401 Unauthorized.
        422 Validation Error.
        500 Internal server error
        409 conflict
    """
    return await authentication_service.resend_verification_code(
        session=session, schema=schema
    )
