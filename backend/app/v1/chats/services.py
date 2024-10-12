from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.services import Service
from app.v1.chats import Message
from app.v1.rooms.services import (
    room_member_service,
    room_service
)
from app.utils.task_logger import create_logger
from app.core.custom_exceptions import CannotDeleteMessageError


logger = create_logger("Message Service")


class MessageService(Service):
    """
    Service class for message.
    """
    def __init__(self) -> None:
        super().__init__(Message)

    async def delete_message(self, room_id: str,
                             user_id: str,
                             message_id: str,
                             session: AsyncSession) -> Optional[Message]:
        """
        Delete a message if user is the creator or user is admin.

        Args:
            room_id(str): id of the private/public/direct_message room.
            user_id(str): id of the user deleting the message.
            message_id(str): id of the message to delete.
            session(object): database session object.
        Returns:
            The deleted message.
        Raises:
            CannotDeleteMessageError: if the user is not admin or message not found, or message not
                                        a direct_message
        """
        # check if admin set room messages as deletable
        room_message_deletable = await room_service.fetch(
            {
                "id": room_id
            },
            session
        )
        if room_message_deletable.messages_deletable or room_message_deletable.room_type == "direct_message":
            # delete message if user is the creator of the message
            deleted_message = await message_service.delete(
                {
                    "user_id": user_id,
                    "id": message_id
                },
                session
            )
            if deleted_message:
                logger.info(msg=f"User member {user_id} deleted the message successfully")
                return deleted_message
            else:
                raise CannotDeleteMessageError(f"Message {message_id} not found, or user {user_id} is not the message creator")

        # delete message if user is an admin in the room
        user_is_admin = await room_member_service.is_user_admin(
            room_id=room_id,
            user_id=user_id,
            session=session
        )
        logger.info(msg=f"user_is_admin: {user_is_admin}")
        if user_is_admin:
            deleted_message = await message_service.delete(
                {
                    "id": message_id
                },
                session,
            )
            logger.info(msg=f"User admin {user_id} deleted the message successfully")
            return deleted_message
        raise CannotDeleteMessageError(f"User {user_id} is not allowed to delete the message {message_id}")


message_service = MessageService()
