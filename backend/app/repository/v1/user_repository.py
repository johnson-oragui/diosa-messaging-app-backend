"""
User Repository Module
"""

import typing

from fastapi import Depends
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.task_logger import create_logger
from app.models.user import User
from app.database.session import get_async_session

logger = create_logger("::USER Repository::")


class UserRepository:
    """
    User Repository
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        COnstructor
        """
        self.model = User
        self.__session = session

    async def create(
        self,
        first_name: typing.Union[str, None],
        last_name: typing.Union[str, None],
        email: str,
        password: typing.Union[str, None],
        username: typing.Union[str, None],
        profile_photo: typing.Union[str, None],
        idempotency_key: typing.Union[str, None],
        email_verified: bool,
    ) -> User:
        """
        Creates a new User.

        Args
            first_name(str|None): The user first_name,
            last_name(str|None): The user last name,
            email(str): The user email
            password(str|None): The user password,
            username(str|None): the user username
            profile_photo(str|None): the user profile photo.
            idempotency_key(str): idempotency key
            email_verified(bool). If email is verified
        Returns:
            User(object): The user instance
        """
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            profile_photo=profile_photo,
            idempotency_key=idempotency_key,
            email_verified=email_verified,
        )
        if not idempotency_key:
            await user.set_idempotency_key(email)
        if password:
            user.set_password(password)

        self.__session.add(user)
        await self.__session.commit()

        return user

    async def fetch_by_id(self, user_id: str) -> typing.Optional[User]:
        """
        Retrieves a user by id.

        Args:
            user_id(str). The user id
        Returns:
            User(object): The user instance or none
        """
        query = sa.select(User).where(User.id == user_id, User.is_deleted.is_(False))

        return (await self.__session.execute(query)).scalar_one_or_none()

    async def fetch_by_email(
        self,
        email: str,
    ) -> typing.Optional[User]:
        """
        Retrieves a user by email.

        Args:
            email(str). The user email
        Returns:
            User(object): The user instance or none
        """
        query = sa.select(User).where(User.email == email, User.is_deleted.is_(False))

        return (await self.__session.execute(query)).scalar_one_or_none()

    async def fetch_by_username(self, username: str) -> typing.Optional[User]:
        """
        Retrieves a user by username.

        Args:
            username(str). The user username
        Returns:
            User(object): The user instance or none
        """
        query = sa.select(User).where(
            User.username == username, User.is_deleted.is_(False)
        )

        return (await self.__session.execute(query)).scalar_one_or_none()

    async def fetch_by_idempotency_key(
        self, idempotency_key: str
    ) -> typing.Optional[User]:
        """
        Retrieves a user by idempotency_key.

        Args:
            idempotency_key(str). The user idempotency_key
        Returns:
            User(object): The user instance or none
        """
        query = sa.select(User).where(
            User.idempotency_key == idempotency_key, User.is_deleted.is_(False)
        )

        return (await self.__session.execute(query)).scalar_one_or_none()

    async def fetch_by_username_or_email(
        self, email: str, username: str
    ) -> typing.Optional[User]:
        """
        Retrieves a user by username or email.

        Args:
            email(str). The user email
        Returns:
            User(object): The user instance or none
        """
        query = sa.select(User).where(
            sa.or_(User.username == username, User.email == email),
            User.is_deleted.is_(False),
        )

        return (await self.__session.execute(query)).scalar_one_or_none()

    async def delete(
        self,
        user_id: str,
    ) -> None:
        """
        Soft deletes a user account.

        Args:
            user_id(str). The user id
        Returns:
            None
        """
        query = (
            sa.update(User)
            .where(
                User.id == user_id,
                User.is_deleted.is_(False),
            )
            .values(is_deleted=True)
        )

        await self.__session.execute(query)

    async def update_password(self, user: User, new_password: str) -> None:
        """
        Updates user password

        Args:
            user(User). The user object.
            new_password(str): The new password
        Returns:
            None
        """
        user.set_password(new_password)
        self.__session.add(user)
        await self.__session.commit()
        await self.__session.refresh(user)


async def get_user_repository(
    session: AsyncSession = Depends(get_async_session),
) -> UserRepository:
    """
    User repository DI
    """
    return UserRepository(session)


UserRepositoryDI = typing.Annotated[UserRepository, Depends(get_user_repository)]


async def get_user_repository_transaction(
    session: AsyncSession = Depends(get_async_session),
) -> typing.AsyncIterator[UserRepository]:
    """
    User repository DI with Transaction
    """
    async with session.begin():
        yield UserRepository(session)


UserRepositoryTransactionDI = typing.Annotated[
    UserRepository, Depends(get_user_repository_transaction)
]
