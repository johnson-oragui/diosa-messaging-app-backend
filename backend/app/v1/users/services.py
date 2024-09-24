from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select

from app.utils.task_logger import create_logger
from app.v1.users import User
from app.v1.users.schema import RegisterInput

logger = create_logger("User Service")

class UserService:
    """
    User class services
    """
    async def create(self, schema: RegisterInput, session: AsyncSession) -> User:
        """Creates a new user.
        
        Keyword arguments:
            schema -- model containing user fields.
            session -- Database session object
        Return: new user created.
        """
        new_user = User(
            **schema.model_dump(
                exclude={
                    "confirm_password",
                    "password"
                }
            )
        )
        logger.info(msg=f"{schema.model_dump()}")
        new_user.set_password(schema.password)
        session.add(new_user)
        await session.commit()
        return new_user

    async def fetch_by_email_or_user_name(self, schema: RegisterInput, session: AsyncSession) -> Optional[User]:
        """
        Fetch a user by username or email.

        Keyword arguments:
            schema -- model containing user fields.
            session -- Database session object
        Return: user if user exists or None if user does not exist.
        """
        stmt = select(User).where(
            or_(
                User.email == schema.email,
                User.username == schema.username
            )
        )

        result = await session.execute(stmt)

        return result.scalar_one_or_none()

    async def fetch_by_id(self, user_id, session: AsyncSession) -> Optional[User]:
        """
        Fetch a user by id.

        Keyword arguments:
            user_id(str) -- id of the user.
            session -- Database session object
        Return: user if id is valid, none if id is invalid.
        """
        stmt = select(User).where(User.id == user_id)

        result = await session.execute(stmt)

        return result.scalar_one_or_none()

    async def fetch_by_idempotency_key(self, key: str, session: AsyncSession) -> Optional[User]:
        """
        Fetch a user by idempotency_key.

        Keyword arguments:
            key(str) -- the idempotency key.
            session -- Database session object
        Return: user if idempotency_key is valid, none if idempotency_key is invalid.
        """
        stmt = select(User).where(User.idempotency_key == key)

        result = await session.execute(stmt)

        user = result.scalar_one_or_none()

        return user

user_service = UserService()
