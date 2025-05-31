"""
AuthenticationService module
"""

import typing

from fastapi import Depends, status, HTTPException
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import IntegrityConstraintViolationError

from app.dto.v1.authentication_dto import (
    RegisterUserRequestDto,
    RegisterOutputResponseDto,
    UserBaseDto,
)
from app.repository.v1.user_repository import (
    UserRepository,
    UserRepositoryTransactionDI,
)
from app.utils.task_logger import create_logger

logger = create_logger(":: Authentication Service ::")


class AuthenticationService:
    """
    Authentication Service
    """

    def __init__(self, user_repository: UserRepository) -> None:
        """
        Authentication constructor
        """
        self.user_repository = user_repository

    async def register_new_user(
        self, schema: RegisterUserRequestDto
    ) -> typing.Optional[RegisterOutputResponseDto]:
        """
        Registers a new User
        """
        user_exists = await self.user_repository.fetch_by_idempotency_key(
            schema.idempotency_key
        )

        if user_exists:
            return RegisterOutputResponseDto(
                data=UserBaseDto.model_validate(user_exists, from_attributes=True),
                message="User already Registered",
            )
        try:

            new_user = await self.user_repository.create(
                None,
                None,
                schema.email,
                schema.password,
                None,
                None,
                schema.idempotency_key,
                False,
            )
            return RegisterOutputResponseDto(
                data=UserBaseDto.model_validate(new_user, from_attributes=True)
            )
        except (IntegrityConstraintViolationError, IntegrityError) as exc:
            logger.error(str(exc.args))
            raise HTTPException(
                status.HTTP_409_CONFLICT, detail="Email already in use"
            ) from exc


async def get_authentication_service(
    user_repository: UserRepositoryTransactionDI,
) -> AuthenticationService:
    """
    DI to get authentication service
    """
    return AuthenticationService(user_repository)


AuthenticationServiceDI = typing.Annotated[
    AuthenticationService, Depends(get_authentication_service)
]
