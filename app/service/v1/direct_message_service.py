"""
DirectMessageService module
"""

import typing

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request, HTTPException, status

from app.repository.v1.direct_message_repository import (
    direct_message_repository,
)
from app.repository.v1.direct_conv_repository import (
    direct_conversation_repository,
)
from app.dto.v1.direct_message_dto import (
    SendMessageDto,
    SendMessageResponseDto,
    MessageBaseDto,
)
from app.utils.task_logger import create_logger


logger = create_logger(":: DirectMessage Service ::")


class DirectMessageService:
    """
    DirectMessage Service
    """

    async def send_message(
        self, schema: SendMessageDto, session: AsyncSession, request: Request
    ) -> typing.Union[SendMessageResponseDto, None]:
        """
        Sends a new message to a user.

        Args:
            schema (pydantic): The request payload object.
            session (AsyncSession): The async database session.
            request (Request): The request object.
        Returns:
            SendMessageResponseDto(pydantic): Response payload
        Raises:
            HTTPException(409)
            HTTPException(404)
        """
        claims: dict = request.state.claims
        current_user_id = claims.get("user_id", "")

        if current_user_id == schema.recipient_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot send message to self",
            )

        conversation_exists = None
        add_to_session_list = []
        if schema.parent_message_id:
            parent_message_exists = await direct_message_repository.fetch(
                session=session, message_id=schema.parent_message_id, attributes=["id"]
            )
            if not parent_message_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent message not found",
                )
        if schema.conversation_id:
            conversation_exists = await direct_conversation_repository.find_by_users(
                sender_id=current_user_id,
                recipient_id=schema.recipient_id,
                session=session,
            )
            if not conversation_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found",
                )
        if not schema.conversation_id:
            conversation_exists = await direct_conversation_repository.find_by_users(
                sender_id=current_user_id,
                recipient_id=schema.recipient_id,
                session=session,
            )
        if conversation_exists and (
            conversation_exists.is_deleted_for_sender
            or conversation_exists.is_deleted_for_recipient
        ):
            conversation_exists.is_deleted_for_sender = False
            conversation_exists.is_deleted_for_recipient = False

            add_to_session_list.append(conversation_exists)

        if not conversation_exists:
            conversation_exists = await direct_conversation_repository.create(
                sender_id=current_user_id,
                recipient_id=schema.recipient_id,
                session=session,
            )
            add_to_session_list.append(conversation_exists)
        new_message = await direct_message_repository.create(
            content=schema.message,
            sender_id=current_user_id,
            recipient_id=schema.recipient_id,
            conversation=conversation_exists,
            media_type=schema.media_type,
            media_url=str(schema.media_url),
            parent_message_id=schema.parent_message_id,
        )

        add_to_session_list.append(new_message)
        session.add_all(add_to_session_list)
        await session.commit()

        message_base = MessageBaseDto.model_validate(new_message, from_attributes=True)
        return SendMessageResponseDto(data=message_base)


direct_message_service = DirectMessageService()
