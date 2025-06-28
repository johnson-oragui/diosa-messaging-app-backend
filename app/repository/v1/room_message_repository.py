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


room_message_repository = RoomMessageRepository()
