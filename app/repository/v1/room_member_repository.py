"""
Room meber repo module
"""

import typing

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.room_member import RoomMember
from app.models.room import Room
from app.models.user import User


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
        Returns:
            RoomMember or None
        """
        query = sa.select(self.model).where(
            self.model.member_id == member_id, self.model.room_id == room_id
        )

        return (await session.execute(query)).scalar_one_or_none()

    async def fetch_all(
        self, session: AsyncSession, room_id: str
    ) -> typing.Sequence[typing.Optional[typing.Any]]:
        """
        Retrieves all room members.

        Args:
            session (AsyncSession): The database async session object.
            room_id (str): The id of the room to fetch.
        Returns:
            Sequence of Object or None
        """
        query = (
            sa.select(
                User.first_name,
                User.last_name,
                User.id.label("member_id"),
                User.profile_photo,
                RoomMember.is_admin,
            )
            .select_from(Room)
            .join(
                RoomMember,
                Room.id == RoomMember.room_id,
            )
            .join(User, RoomMember.member_id == User.id)
            .where(Room.id == room_id, RoomMember.left_room.is_(False))
        )

        return (await session.execute(query)).mappings().all()


room_member_repository = RoomMemberRepository()
