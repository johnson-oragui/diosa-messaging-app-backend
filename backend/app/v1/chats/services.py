from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy import select

from app.base.services import Service
from app.v1.chats import Message
from app.v1.users import User
from app.v1.profile import Profile
from app.v1.rooms import Room
from app.v1.rooms.services import (
    room_member_service,
    room_service
)
from app.v1.chats.schemas import (
    BaseMessage,
)
from app.utils.task_logger import create_logger
from app.core.custom_exceptions import (
    CannotDeleteMessageError,
    CannotUpdateMessageError,
)


logger = create_logger("Message Service")


class MessageService(Service):
    """
    Service class for message.
    """
    def __init__(self) -> None:
        super().__init__(Message)

    async def delete_message(self, room_id: str,
                             user_id: str,
                             session: AsyncSession,
                             message_id: int | None = None,
                             message_ids: list = []) -> Optional[Message]:
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
        room = await room_service.fetch(
            {
                "id": room_id,
                "is_deleted": False,
            },
            session
        )
        if not room:
            raise CannotDeleteMessageError("Room does not exists or has been deleted.")
        if room.messages_deletable is True:
            if message_id:
                # delete message if user is the creator of the message or a direct_message
                deleted_message = await self.update(
                    [
                        {
                            "user_id": user_id,
                            "id": message_id
                        },
                        {
                            "is_deleted": True,
                        }
                    ],
                    session
                )
                if deleted_message:
                    logger.info(msg=f"User member {user_id} deleted the message successfully")
                    return deleted_message
                else:
                    raise CannotDeleteMessageError("Message not found, or user is not the message owner")
            elif message_ids:
                for message_id in message_ids:
                    # delete message if user is the creator of the message or a direct_message
                    deleted_message = await self.update(
                        [
                            {
                                "user_id": user_id,
                                "id": message_id
                            },
                            {
                                "is_deleted": True,
                            }
                        ],
                        session
                    )
                    if deleted_message:
                        logger.info(msg=f"User deleted the message successfully")
                    else:
                        raise CannotDeleteMessageError("Message not found, or user is not the message owner")
                return

        # delete message if user is an admin in the room
        user_is_admin = await room_member_service.is_user_admin(
            room_id=room_id,
            user_id=user_id,
            session=session
        )
        logger.info(msg=f"user_is_admin: {user_is_admin}")
        if user_is_admin:
            if message_id:
                deleted_message = await self.update(
                    [
                        {
                            "id": message_id
                        },
                        {
                            "is_deleted": True,
                        }
                    ],
                    session
                )
                if deleted_message:
                    logger.info(msg=f"User admin {user_id} deleted the message successfully")
                    return deleted_message
                else:
                    raise CannotDeleteMessageError("Message not found")
            elif message_ids:
                for message_id in message_ids:
                    deleted_message = await self.update(
                        [
                            {
                                "id": message_id
                            },
                            {
                                "is_deleted": True,
                            }
                        ],
                        session
                    )
                    if deleted_message:
                        logger.info(msg=f"User member {user_id} deleted the message successfully")
                        return deleted_message
                    else:
                        raise CannotDeleteMessageError("Message not found")
        raise CannotDeleteMessageError("User is not allowed to delete the message")

    async def fetch_room_messages(self, room_id: str,
                                  filterer: dict,
                                  session: AsyncSession) -> List[BaseMessage]:
        """
        Retrieves messages for a specific room.
        Limited to 20 messages.

        Args:
            room_id (str): The id of the room.
            filterer (dict): the filters to apply on the fetch.
            session (AsyncSession): database session object.
        Returns:
            List[BaseMessage]: A list of dictionaries containing the rom_id, content, created_at,
                                username, first_name, last_name,avatar_url of the room.
        """
        limit = min(20, filterer.get("limit", 20))
        room = aliased(Room, name="room")
        message = aliased(Message, name="message")
        user = aliased(User, name="user")
        profile = aliased(Profile, name="profile")

        stmt = select(
            room.id,
            message.content,
            message.created_at,
            user.username,
            user.first_name,
            user.last_name,
            profile.avatar_url
        ).join(
            message, room.id == message.room_id
        ).join(
            user, message.user_id == user.id
        ).join(
            profile, profile.user_id == user.id
        ).where(
            message.room_id == room_id,
            message.is_deleted != True,
            room.is_deleted != True
        ).order_by(
            message.created_at
        ).limit(limit)

        result = await session.execute(stmt)
        all_messages = result.fetchall()

        room_messages = []
        for msg in all_messages:
            user_message = BaseMessage(
                room_id=msg[0],
                content=msg[1],
                created_at=msg[2],
                username=msg[3],
                first_name=msg[4],
                last_name=msg[5],
                avatar_url=msg[6]
            )
            room_messages.append(user_message)

        return room_messages

    async def update_message(self, room_id: str,
                             user_id: str,
                             session: AsyncSession,
                             message: str,
                             message_id,
                             ) -> Optional[Message]:
        """
        Updates a message if user is the creator.

        Args:
            room_id(str): id of the private/public/direct_message room.
            user_id(str): id of the user updating the message.
            message(str): message to be updated.
            message_id(str): id of the message to be updated.
            session(object): database session object.
        Returns:
            The updated message.
        Raises:
            CannotUpdateMessageError: if the user is not admin or message not found, or message not
                                        a direct_message
        """
        # check if admin set room messages as deletable
        room = await room_service.fetch(
            {
                "id": room_id,
                "is_deleted": False,
            },
            session
        )
        if not room:
            raise CannotUpdateMessageError("Room does not exists or has been deleted.")
        # update message if user is the creator of the message or a direct_message
        updated_message = await self.update(
            [
                {
                    "user_id": user_id,
                    "id": message_id
                },
                {
                    "content": message,
                }
            ],
                session
            )
        if updated_message:
            logger.info(msg=f"User member {user_id} updated the message successfully")
            return updated_message
        raise CannotUpdateMessageError("Message not found, or user is not the message owner")

message_service = MessageService()
