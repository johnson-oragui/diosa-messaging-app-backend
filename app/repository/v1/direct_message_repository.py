"""
DirectMessageRepository Module
"""

import typing
from datetime import datetime, timezone, timedelta

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.direct_message import DirectMessage
from app.models.direct_conversation import DirectConversation


class DirectMessageRepository:
    """
    Direct Message repo
    """

    def __init__(self) -> None:
        """
        Constructor.
        """
        self.model = DirectMessage

    async def create(
        self,
        content: typing.Union[str, None],
        sender_id: str,
        recipient_id: str,
        conversation: DirectConversation,
        parent_message_id: typing.Union[str, None],
        media_url: typing.Union[str, None],
        media_type: typing.Union[str, None],
    ) -> DirectMessage:
        """
        Creates a new message.


        Args:
            content(str): The message content
            sender_id(str): The id of the sender content
            recipient_id(str): The id of the recipient content
            conversation_id(str): The id of the conversation content
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
            recipient_id=recipient_id,
            direct_conversation=conversation,
            parent_message_id=parent_message_id,
        )

        return new_message

    async def fetch(
        self,
        session: AsyncSession,
        message_id: str,
        attributes: typing.List[typing.Union[str, None]] = [],
    ) -> typing.Union[DirectMessage, None]:
        """
        Retrieves a message.

        Args:
            session (AsyncSession): Database async session object.
            message_id (str): The id of the message to retrieve.
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
            query = sa.select(*selected_fields).where(self.model.id == message_id)
            return (await session.execute(query)).scalar_one_or_none()

        query = sa.select(self.model).where(self.model.id == message_id)

        return (await session.execute(query)).scalar_one_or_none()

    async def fetch_all(
        self,
        conversation_id: str,
        user_id: str,
        offset: int,
        order: str,
        session: AsyncSession,
        attributes: typing.List[typing.Union[str, None]] = [],
    ) -> typing.Sequence[typing.Optional[DirectMessage]]:
        """
        Retrieves all messages.


        Args:
            conversation_id(str): The id of the conversation content
            user_id(str): The id of the current user
            offset(int): The offset for pagination
            order(str): The order by (e., asc, desc).
            session (AsyncSession): The database async session object.
            attributes (List[str]): Optional list of fields to select from the message
        Returns:
            Message(object): new message object.
        """
        order_by = sa.desc if order == "desc" else sa.asc
        if len(attributes) > 0:
            selected_fields = [
                getattr(self.model, attr)
                for attr in attributes
                if isinstance(attr, str) and hasattr(self.model, attr)
            ]
            if not selected_fields:
                return []
            query = (
                sa.select(*selected_fields)
                .where(
                    self.model.conversation_id == conversation_id,
                    sa.or_(
                        self.model.sender_id == user_id,
                        self.model.recipient_id == user_id,
                    ),
                    self.model.status.is_not("deleted"),
                    sa.and_(
                        self.model.is_deleted_for_sender.is_(False),
                        self.model.sender_id == user_id,
                    ),
                    sa.and_(
                        self.model.is_deleted_for_recipient.is_(False),
                        self.model.recipient_id == user_id,
                    ),
                )
                .offset(offset)
                .order_by(order_by(self.model.created_at))
            )

            result = (await session.execute(query)).scalars().all()
            return result
        query = (
            sa.select(self.model)
            .where(
                self.model.conversation_id == conversation_id,
                sa.or_(
                    self.model.sender_id == user_id,
                    self.model.recipient_id == user_id,
                ),
                self.model.status.is_not("deleted"),
                sa.and_(
                    self.model.is_deleted_for_sender.is_(False),
                    self.model.sender_id == user_id,
                ),
                sa.and_(
                    self.model.is_deleted_for_recipient.is_(False),
                    self.model.recipient_id == user_id,
                ),
            )
            .offset(offset)
            .order_by(order_by(self.model.created_at))
        )

        result = (await session.execute(query)).scalars().all()
        return result

    async def delete_for_sender(
        self,
        conversation_id: str,
        user_id: str,
        message_id: typing.Union[str, None],
        session: AsyncSession,
    ) -> None:
        """
        Deletes message for sender.
        Args:
            conversation_id(str): The id of the converstion
            message_id(str): The id of the message
            user_id(str): The id of the current user.
            session (AsyncSession): The database async session object.
        Returns:
            None
        """
        query = sa.update(self.model).where(
            self.model.conversation_id == conversation_id,
            self.model.sender_id == user_id,
        )
        if message_id:
            query = query.where(self.model.id == message_id)
        query = query.values(is_deleted_for_sender=True)

        await session.execute(query)

    async def delete_for_recipient(
        self,
        conversation_id: str,
        user_id: str,
        message_id: typing.Union[str, None],
        session: AsyncSession,
    ) -> None:
        """
        Deletes message for recipient.
        Args:
            conversation_id(str): The id of the converstion
            message_id(str): The id of the message
            user_id(str): The id of the current user.
            session (AsyncSession): The database async session object.
        Returns:
            None
        """
        query = sa.update(self.model).where(
            self.model.conversation_id == conversation_id,
            self.model.recipient_id == user_id,
        )
        if message_id:
            query = query.where(self.model.id == message_id)
        query = query.values(is_deleted_for_recipient=True)

        await session.execute(query)

    async def delete_for_all(
        self,
        conversation_id: str,
        user_id: str,
        message_ids: typing.List[str],
        session: AsyncSession,
    ) -> int:
        """
        Deletes message(s).
        Args:
            conversation_id(str): The id of the converstion
            message_id(str): The id of the message
            user_id(str): The id of the current user.
            session (AsyncSession): The database async session object.
        Returns:
            int
        """
        now = datetime.now(timezone.utc)
        query = (
            sa.update(self.model)
            .where(
                self.model.created_at + timedelta(minutes=15) > now,
                self.model.conversation_id == conversation_id,
                self.model.recipient_id == user_id,
                self.model.id.in_(message_ids),
            )
            .values(status="deleted")
        )

        result = await session.execute(query)
        await session.commit()
        return result.rowcount

    async def update(
        self,
        conversation_id: str,
        message_id: str,
        user_id: str,
        content: str,
        session: AsyncSession,
    ) -> int:
        """
        Updates a message.
        Args:
            conversation_id(str): The id of the converstion
            message_id(str): The id of the message
            user_id(str): The id of the current user.
            session (AsyncSession): The database async session object.
        Returns:
            int
        """
        query = (
            sa.update(self.model)
            .where(
                self.model.conversation_id == conversation_id,
                self.model.id == message_id,
                self.model.sender_id == user_id,
            )
            .values(content=content, is_edited=True)
        )

        result = await session.execute(query)
        await session.commit()
        return result.rowcount


direct_message_repository = DirectMessageRepository()
