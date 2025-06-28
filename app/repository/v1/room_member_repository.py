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

    async def create(
        self, room_id: str, member_id: str, is_admin: bool, session: AsyncSession
    ) -> RoomMember:
        """
        Adds a new member to a room.

        Args:
            member_id (str): The id of the room member to fetch.
            session ( AsyncSession): The async database session object.
            room_id (str): The id of room.
            is_admin (bool): The admin status of the new member to add.
        Returns:
            RoomMember
        """
        new_member = RoomMember(member_id=member_id, room_id=room_id, is_admin=is_admin)
        session.add(new_member)

        await session.commit()
        return new_member

    async def fetch(
        self,
        member_id: str,
        session: AsyncSession,
        room_id: str,
        attributes: typing.List[typing.Union[str, None]] = [],
    ) -> typing.Union[RoomMember, None, typing.Mapping]:
        """
        Fetches a room member.

        Args:
            member_id (str): The id of the room member to fetch
            session ( AsyncSession): The async database session object.
            room_id (str): The id of room.
        Returns:
            RoomMember or None
        """
        if len(attributes) > 0:
            selected_fields = [
                getattr(self.model, attr)
                for attr in attributes
                if isinstance(attr, str) and hasattr(self.model, attr)
            ]
            if not selected_fields:
                return None
            query = sa.select(*selected_fields).where(
                self.model.member_id == member_id, self.model.room_id == room_id
            )

            return (await session.execute(query)).mappings().one_or_none()

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

    async def update(
        self,
        room_id: str,
        session: AsyncSession,
        member_id: str,
        is_admin: typing.Union[None, bool],
        left_room: typing.Union[None, bool],
    ):
        """
        Updates room member status
        """
        query = sa.update(RoomMember).where(
            RoomMember.room_id == room_id, RoomMember.member_id == member_id
        )
        if is_admin is not None:
            query = query.values(is_admin=is_admin)
        if left_room is not None:
            query = query.values(left_room=left_room)

        await session.execute(query)
        await session.commit()


room_member_repository = RoomMemberRepository()
