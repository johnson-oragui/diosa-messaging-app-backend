"""
Room meber repo module
"""

import typing

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.room_member import RoomMember


class RoomMemberRepository:
    """
    Room member repository
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self.model = RoomMember

    async def fetch(
        self, member_id: str, session: AsyncSession, room_id: str
    ) -> typing.Optional[RoomMember]:
        """
        Fetches a room member.

        Args:
            member_id (str): The id of the room member to fetch
            session ( AsyncSession): The async database session object.
            room_id (str): The id of room.
        """
        query = sa.select(self.model).where(
            self.model.member_id == member_id, self.model.room_id == room_id
        )

        return (await session.execute(query)).scalar_one_or_none()


room_member_repository = RoomMemberRepository()
