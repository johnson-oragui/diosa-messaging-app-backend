"""
DirectConversationRepository Module
"""

import typing
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.direct_conversation import DirectConversation
from app.models.direct_message import DirectMessage
from app.models.user import User


class DirectConversationRepository:
    """
    Direct conversation repo
    """

    async def create(
        self, sender_id: str, recipient_id: str, session: AsyncSession
    ) -> DirectConversation:
        """
        Creates a new conversation.


        Args:
            sender_id(str): The id of the current user
            recipeint_id(str): The id of the recipient.
        Returns:
            DirectConversation(object): direct_conversation instance
        """
        new_direct_conversation = DirectConversation(
            sender_id=sender_id,
            recipient_id=recipient_id,
        )

        return new_direct_conversation

    async def update(
        self, is_deleted: bool, conversation_id: str, session: AsyncSession
    ) -> None:
        """
        Updates direct conversation is_deleted status.


        Args:
            is_deleted(bool): The status of deletion.
            converstion_id(str): The id of conversation.
            session(AsyncSession): The database session object.
        Returns:
            None
        """
        query = (
            sa.update(DirectConversation)
            .where(DirectConversation.id == conversation_id)
            .values(is_deleted=is_deleted)
        )

        await session.execute(query)

    async def fetch_by_id(
        self, conversation_id: str, session: AsyncSession
    ) -> typing.Optional[DirectConversation]:
        """
        Fetches a conversation.


        Args:
            conversation_id(str): The id of the conversation.
            session(AsyncSession): The database session object.
        Returns:
            DirectConversation(object): The direct_conversation instance or None
        """
        query = sa.select(DirectConversation).where(
            DirectConversation.id == conversation_id,
        )
        return (await session.execute(query)).scalar_one_or_none()

    async def fetch_all(
        self,
        user_id: str,
        session: AsyncSession,
    ) -> typing.Sequence[typing.Optional[DirectConversation]]:
        """
        Fetches conversations.


        Args:
            conversation_id(str): The id of the conversation.
            session(AsyncSession): The database session object.
        Returns:
            DirectConversation(object): The direct_conversation instance or None
        """
        query = sa.select(DirectConversation).where(
            sa.or_(
                sa.and_(
                    DirectConversation.is_deleted_for_recipient.is_(False),
                    DirectConversation.recipient_id == user_id,
                ),
                sa.and_(
                    DirectConversation.is_deleted_for_sender.is_(False),
                    DirectConversation.sender_id == user_id,
                ),
            ),
        )

        return (await session.execute(query)).scalars().all()

    async def get_conversation_with_last_message_count(
        self, user_id: str, page: int, limit: int, session: AsyncSession
    ) -> typing.Tuple[typing.Sequence[sa.RowMapping], int]:
        """
        Fetches all conversations including the last messages and count
        unread messages with pagination.


        Args:
            user_id(str): The id of the current user.
            page(int): The page for pagination
            limit(int): the limit for pagination
            session(AsyncSession): The database session object.
        Returns:
            Tuple[Sequence[RowMapping], int]: The sequence of direct_conversation mappings and count
        """
        # Subquery to get the latest message per conversation
        latest_message_subquery = (
            sa.select(
                DirectMessage.conversation_id,
                DirectMessage.content,
                DirectMessage.created_at,
                sa.func.row_number()
                .over(
                    partition_by=DirectMessage.conversation_id,
                    order_by=DirectMessage.created_at.desc(),
                )
                .label("row_num"),
            )
            .select_from(DirectMessage)
            .subquery()
        ).alias("latest_message_rn")

        # Subquery to count unread messages per conversation for the current user
        unread_message_count_subquery = (
            sa.select(
                DirectMessage.conversation_id,
                sa.func.count(DirectMessage.id).label("unread_count"),
            )
            .select_from(DirectMessage)
            .where(
                DirectMessage.conversation_id == DirectConversation.id,
                DirectMessage.read_at.is_(None),
                sa.or_(
                    DirectMessage.recipient_id == user_id,
                    DirectMessage.sender_id == user_id,
                ),
            )
            .group_by(DirectMessage.conversation_id)
            .correlate(
                DirectConversation
            )  # Correlate with the outer Conversation table
            .subquery()
        ).alias("unread_counts")

        # Main query
        stmt = (
            sa.select(
                DirectConversation.id.label("conversation_id"),
                User.id.label("user_id"),
                User.first_name.label("firstname"),
                User.profile_photo.label("profile_photo"),
                DirectConversation.updated_at.label("updated_at"),
                latest_message_subquery.c.content.label("last_message"),
                sa.func.coalesce(unread_message_count_subquery.c.unread_count, 0).label(
                    "unread_message_count"
                ),
            )
            .select_from(DirectConversation)
            .join(
                User,
                sa.or_(
                    DirectConversation.sender_id == User.id,
                    DirectConversation.recipient_id == User.id,
                ),
            )
            .outerjoin(
                latest_message_subquery,
                sa.and_(
                    latest_message_subquery.c.conversation_id == DirectConversation.id,
                    latest_message_subquery.c.row_num == 1,
                ),
            )
            .outerjoin(
                unread_message_count_subquery,  # Join with the new unread count subquery
                unread_message_count_subquery.c.conversation_id
                == DirectConversation.id,
            )
            .where(
                sa.or_(
                    sa.and_(
                        DirectConversation.is_deleted_for_recipient.is_(False),
                        DirectConversation.recipient_id == user_id,
                    ),
                    sa.and_(
                        DirectConversation.is_deleted_for_sender.is_(False),
                        DirectConversation.sender_id == user_id,
                    ),
                ),
                User.id != user_id,
            )
            .order_by(DirectConversation.updated_at.desc())
        )

        # Execute the query
        count_stmt = sa.select(sa.func.count()).select_from(stmt.subquery())  # noqa
        count_result = await session.execute(count_stmt)
        total_conversations = count_result.scalar_one_or_none() or 0

        stmt = stmt.limit(limit).offset((page - 1) * limit)

        result = await session.execute(stmt)
        conversations = result.mappings().all()

        return conversations, total_conversations

    async def find_by_users(
        self, sender_id: str, recipient_id: str, session: AsyncSession
    ) -> typing.Optional[DirectConversation]:
        """
        Checks if users already has a conversation using their IDs


        Args:
            sender_id (str): The id of the sender.
            recipeint_id (str): The id of the recipient.
            session (AsyncSession): The database async session object
        Return:
            COnversation if found, None if not found.
        """
        query = sa.select(DirectConversation).where(
            (
                (DirectConversation.sender_id == sender_id)
                & (DirectConversation.recipient_id == recipient_id)
                | (DirectConversation.sender_id == recipient_id)
                & (DirectConversation.recipient_id == sender_id)
            )
        )

        result = await session.execute(query)
        return result.scalar_one_or_none()


direct_conversation_repository = DirectConversationRepository()
