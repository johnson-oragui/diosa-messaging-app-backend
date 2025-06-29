"""
RoomMessageRepository module
"""

import typing

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.room_message import RoomMessage
from app.models.room_member import RoomMember
from app.models.room import Room
from app.models.user import User


class RoomMessageRepository:
    """
    RoomMessageRepository class
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self.model = RoomMessage

    async def create(
        self,
        content: typing.Union[str, None],
        sender_id: str,
        room_id: str,
        parent_message_id: typing.Union[str, None],
        media_url: typing.Union[str, None],
        media_type: typing.Union[str, None],
        session: AsyncSession,
    ) -> RoomMessage:
        """
        Creates a new room message.


        Args:
            content(str): The message content
            sender_id(str): The id of the sender content
            room_id(str): The id of the recipient content
            media_type(str): The media type
            media_url(str): The message content.
        Returns:
            Message(object): new message object.
        """
        new_message = self.model(
            sender_id=sender_id,
            content=content,
            media_type=media_type,
            media_url=media_url,
            room_id=room_id,
            parent_message_id=parent_message_id,
        )

        session.add(new_message)

        await session.commit()

        return new_message

    async def fetch_all(
        self,
        room_id: str,
        offset: int,
        order: str,
        session: AsyncSession,
        attributes: typing.List[typing.Optional[str]] = [],
    ) -> typing.Tuple[typing.Sequence[typing.Optional[RoomMessage]], int]:
        """
        Retrieves all messages.

        Args:
            room_id(str): The id of the room
            offset(int): The offset for pagination
            order(str): The order by (e., asc, desc).
            session (AsyncSession): The database async session object.
            attributes (List[str]): Optional list of fields to select from the message
        Returns:
            List[Optional[RoomMessage]]: List containing optional room messages.
        """
        order_by = sa.desc if order == "desc" else sa.asc
        if len(attributes) > 0:
            selected_fields = [
                getattr(self.model, attr)
                for attr in attributes
                if isinstance(attr, str) and hasattr(self.model, attr)
            ]
            if not selected_fields:
                return [], 0
            query = sa.select(*selected_fields).where(
                self.model.room_id == room_id, self.model.is_deleted.is_(False)
            )

            count_stmt = sa.select(sa.func.count()).select_from(query.subquery())
            count_result = await session.execute(count_stmt)
            total_count = count_result.scalar_one() or 0

            query = query.offset(offset).order_by(order_by(self.model.created_at))

            result = (await session.execute(query)).scalars().all()

            return (result, total_count)
        query = sa.select(self.model).where(
            self.model.room_id == room_id, self.model.is_deleted.is_(False)
        )

        count_stmt = sa.select(sa.func.count()).select_from(query.subquery())
        count_result = await session.execute(count_stmt)
        total_count = count_result.scalar_one() or 0

        query = query.offset(offset).order_by(order_by(self.model.created_at))

        result = (await session.execute(query)).scalars().all()

        return (result, total_count)

    async def fetch(
        self,
        session: AsyncSession,
        message_id: str,
        room_id: str,
        attributes: typing.List[typing.Union[str, None]] = [],
    ) -> typing.Union[RoomMessage, None]:
        """
        Retrieves a message.

        Args:
            session (AsyncSession): Database async session object.
            message_id (str): The id of the message to retrieve.
            room_id (str): The id of the room message to retrieve.
            attributes (List[str]): Optional list of fields to select from the message
        Returns:
            Message if found or None
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
                self.model.id == message_id, self.model.room_id == room_id
            )

            return (await session.execute(query)).scalar_one_or_none()

        query = sa.select(self.model).where(
            self.model.id == message_id, self.model.room_id == room_id
        )

        return (await session.execute(query)).scalar_one_or_none()

    async def update(
        self,
        user_id: str,
        content: str,
        session: AsyncSession,
        message: RoomMessage,
    ) -> RoomMessage:
        """
        Updates a message.
        Args:
            message(DirectMessage): The message to update
            contest(str): The new message content
            user_id(str): The id of the current user.
            session (AsyncSession): The database async session object.
        Returns:
            int
        """
        query = (
            sa.update(self.model)
            .where(
                self.model.room_id == message.room_id,
                self.model.id == message.id,
                self.model.sender_id == user_id,
            )
            .values(content=content, is_edited=True)
        )

        await session.execute(query)
        await session.commit()
        await session.refresh(message)
        return message


room_message_repository = RoomMessageRepository()
