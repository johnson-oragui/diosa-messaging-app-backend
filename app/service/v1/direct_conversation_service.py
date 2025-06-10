"""
DirectConversationService module
"""

import typing
import math

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from app.repository.v1.direct_conv_repository import (
    direct_conversation_repository,
)
from app.dto.v1.direct_conversation_dto import (
    ConversationBaseDto,
    AllConversationsResponseDto,
)
from app.utils.task_logger import create_logger


logger = create_logger(":: DirectConversation Service ::")


class DirectConversationService:
    """
    DirectMessage Service
    """

    async def fetch_direct_conversations(
        self, request: Request, session: AsyncSession, page: int, limit: int
    ) -> typing.Union[AllConversationsResponseDto, None]:
        """
        Retrieves all conversations.

        Args:
            request (Request): The request object.
            session (AsyncSession): The database async session object.
            page (int): The current page.
            limit (int): The number of conversations per page
        Returns:
            AllConversationsResponseDto (pydantic): The response payload
        """
        claims: dict = request.state.claims
        current_user_id = claims.get("user_id", "")

        all_conversations, count = (
            await direct_conversation_repository.get_conversation_with_last_message_count(
                limit=limit, page=page, session=session, user_id=current_user_id
            )
        )

        return AllConversationsResponseDto(
            data=[
                ConversationBaseDto.model_validate(conversation, from_attributes=True)
                for conversation in all_conversations
                if conversation
            ],
            page=page,
            limit=limit,
            total_pages=(0 if count == 0 else math.ceil(count / limit)),
            total_conversations=count,
        )


direct_conversation_service = DirectConversationService()
