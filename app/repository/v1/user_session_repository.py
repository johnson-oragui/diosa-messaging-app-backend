"""
UserSession Repository module
"""

import typing
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from app.models.user_session import UserSession


class UserSessionRepository:
    """
    UserSessionRepository
    """

    def __init__(self):
        """
        Constructor
        """
        self.model = UserSession

    async def create(
        self,
        user_id: str,
        jti: str,
        location: typing.Union[str, None],
        ip_address: str,
        session_id: str,
        session: AsyncSession,
    ) -> None:
        """
        Createa a new user_session record.

        Args:
            user_id (str): The id of the user
            jti(str): The jti of the tokens
            location (str): The login location
            ip_address (str): the ip address of the user.
            session_id (str): the session_id from client-side
        Returns:
            None
        """
        user_session = self.model(
            session_id=session_id,
            user_id=user_id,
            jti=jti,
            location=location,
            ip_address=ip_address,
        )

        session.add(user_session)
        await session.commit()

    async def fetch(
        self,
        user_id: typing.Union[str, None],
        jti: typing.Union[str, None],
        session_id: typing.Union[str, None],
        is_logged_out: typing.Union[bool, None],
        session: AsyncSession,
    ) -> typing.Union[UserSession, None]:
        """
        Retrieves the user_session record

        Args:
            user_id (str): The id of the user
            jti(str): The jti of the tokens
            session_id (str): the session_id from client-side
            is_logged_out (bool): the status of the session
        Returns:
            None if not found or user_session record if found
        """
        query = sa.select(self.model)
        if user_id:
            query = query.where(self.model.user_id == user_id)
        if jti:
            query = query.where(self.model.jti == jti)
        if session_id:
            query = query.where(self.model.session_id == session_id)
        if is_logged_out is not None:
            query = query.where(self.model.is_logged_out == is_logged_out)

        return (await session.execute(query)).scalar_one_or_none()

    async def fetch_all(
        self, user_id: typing.Union[str, None], session: AsyncSession
    ) -> typing.Sequence[typing.Union[UserSession, None]]:
        """
        Retrieves all user_session record

        Args:
            user_id (str): The id of the user
            jti(str): The jti of the tokens
            session_id (str): the session_id from client-side
        Returns:
            None if not found or user_session record if found
        """
        query = sa.select(self.model).where(
            self.model.user_id == user_id, self.model.is_logged_out.is_(False)
        )

        return (await session.execute(query)).scalars().all()

    async def log_session_out(self, session_id: str, session: AsyncSession) -> None:
        """
        Logs out  session

        Args:
            session_id (str): the session_id from client-side
        Returns:
            None
        """
        query = (
            sa.update(self.model)
            .where(self.model.session_id == session_id)
            .values(is_logged_out=True, logged_out_at=sa.func.now())
        )

        await session.execute(query)

        await session.commit()

    async def update_jti(
        self, session_id: str, jti: str, session: AsyncSession
    ) -> None:
        """
        Updates the jti of the session.

        Args:
            session_id (str): the session_id from client-side
            jti (str): the new jti of the session to update
        Returns:
            None
        """
        query = (
            sa.update(self.model)
            .where(self.model.session_id == session_id)
            .values(jti=jti)
        )

        await session.execute(query)

        await session.commit()


user_session_repository = UserSessionRepository()
