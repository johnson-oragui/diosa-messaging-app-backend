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
)
from app.database.session import get_async_session

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
