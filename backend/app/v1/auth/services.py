from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException

from app.v1.users.services import user_service
from app.v1.users.schema import (
    RegisterInput,
    UserBase,
    RegisterOutput
)
from app.v1.auth.dependencies import generate_idempotency_key
from app.utils.task_logger import create_logger


logger = create_logger("Auth Service")


class AuthService:
    """
    Authentication Class Service
    """
    async def register(self, schema: RegisterInput, session: AsyncSession) -> Optional[RegisterOutput]:
        """
        Registers a user.

        Args:
            schema: pydantic model for user registration fields.
            session: Database session object.
        Returns:
            RegisterOutput: pydantic model with feedback for the client.
        Raises:
            HTTPExcption: If email or username already exists.
        """
        # check if client included an idempotency key
        if schema.idempotency_key:
            # fetch user by idempotency key
            idempotency_key_exists = await user_service.fetch_by_idempotency_key(
                schema.idempotency_key,
                session
            )

            # check if user was found using the provided idempotency key
            if idempotency_key_exists:
                user_out = UserBase.model_validate(
                    idempotency_key_exists,
                    from_attributes=True
                )
                # return same response if user already created.
                return RegisterOutput(
                    status_code=201,
                    message="User Already Registered",
                    data=user_out
                )
        # check if username or email is already taken by another user.
        user_email_or_username_exists = await user_service.fetch_by_email_or_user_name(
            schema,
            session
        )
        # if username or email already taken, notifiy the client.
        if user_email_or_username_exists:
            message = "username already exists"
            if user_email_or_username_exists.email == schema.email:
                message = "email already exists"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        # if the client did not include an idempotency key, generate one
        if not schema.idempotency_key:
            schema.idempotency_key = await generate_idempotency_key(
                schema.email,
                schema.username
            )
        # create a new user
        new_user = await user_service.create(
            schema,
            session
        )

        # generate a response for the client using the new user's details
        user_out = UserBase.model_validate(new_user, from_attributes=True)
        return RegisterOutput(
            status_code=201,
            message="User Registered Successfully",
            data=user_out
        )

auth_service = AuthService()
