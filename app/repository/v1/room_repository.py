"""
Room Repository Module
"""

import typing

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from app.models.room import Room


class RoomRepository:
    """
    RoomReposiroty class
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self.model = Room

    async def create(
        self,
        messages_delete_able: bool,
        owner_id: str,
        name: str,
        room_icon: typing.Union[str, None],
        is_private: bool,
        allow_admin_messages_only: bool,
        session: AsyncSession,
        auto_commit: bool = False,
    ) -> Room:
        """
        Creates a new room.

        Args:
            messages_delete_able(bool): If messages are deletable.
            owner_id(str): Id of the creator.
            name(str): The name of the room,
            room_icon(Optional[str]): The room icon.
            is_private(bool): Sets the privacy of the room.
            allow_admin_messages_only(bool): If only admins are allowed to send messages.
            session (AsyncSession): .
            auto_commit (bool): Decides if to immediately commit changes.
        Returns:
            Room
        """
        new_room = Room(
            owner_id=owner_id,
            name=name,
            room_icon=room_icon,
            is_private=is_private,
            messages_delete_able=messages_delete_able,
            allow_admin_messages_only=allow_admin_messages_only,
        )
        session.add(new_room)

        if auto_commit:
            await session.commit()

        return new_room

    async def update(
        self,
        room_id: str,
        session: AsyncSession,
        room_icon: typing.Optional[str] = None,
        name: typing.Optional[str] = None,
        is_private: typing.Optional[bool] = None,
        messages_delete_able: typing.Optional[bool] = None,
        allow_admin_messages_only: typing.Optional[bool] = None,
        is_deactivated: typing.Optional[bool] = None,
        auto_commit: bool = True,
    ) -> int:
        """
        Updates a room
        """
        query = sa.update(self.model).where(self.model.id == room_id)

        if room_icon:
            query = query.values(room_icon=room_icon)
        if name:
            query = query.values(name=name)
        if is_private is not None:
            query = query.values(is_private=is_private)
        if messages_delete_able is not None:
            query = query.values(messages_delete_able=messages_delete_able)
        if allow_admin_messages_only is not None:
            query = query.values(allow_admin_messages_only=allow_admin_messages_only)
        if is_deactivated is not None:
            query = query.values(is_deactivated=is_deactivated)

        result = await session.execute(query)
        if auto_commit:
            await session.commit()
        return result.rowcount

    async def fetch(
        self, room_id: str, session: AsyncSession
    ) -> typing.Union[Room, None]:
        """
        Retrieves a room
        """
        return (
            await session.execute(sa.select(self.model).where(self.model.id == room_id))
        ).scalar_one_or_none()

    async def fetch_all(
        self, owner_id: str, session: AsyncSession
    ) -> typing.Sequence[typing.Optional[Room]]:
        """
        Retrieves all rooms
        """
        return (
            (
                await session.execute(
                    sa.select(self.model).where(self.model.owner_id == owner_id)
                )
            )
            .scalars()
            .all()
        )


room_repository = RoomRepository()
