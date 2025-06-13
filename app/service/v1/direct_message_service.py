"""
DirectMessageService module
"""

import typing
import math
from datetime import timezone, datetime, timedelta

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
    AllMessagesResponseDto,
    UpdateMessageDto,
    UpdateMessageResponseDto,
    DeleteMessageResponseDto,
    DeleteMessageDto,
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

    async def retrieve_messages(
        self,
        request: Request,
        page: int,
        limit: int,
        session: AsyncSession,
        conversation_id: str,
    ) -> typing.Union[AllMessagesResponseDto, None]:
        """
        Retrieves all messages.

        Args:
            request (Request): The request object.
            session (AsyncSession): The database async session object.
            page (int): The current page.
            limit (int): The number of messages per page
            conversation_id (str): The conversation for the messages
        Returns:
            AllMessagesResponseDto (pydantic): The response payload
        """
        claims: dict = request.state.claims
        current_user_id = claims.get("user_id", "")
        offset = page * limit - limit

        conversation_exists = await direct_conversation_repository.fetch_by_id(
            conversation_id=conversation_id, session=session
        )
        if not conversation_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        all_messages, count = await direct_message_repository.fetch_all(
            conversation_id=conversation_id,
            user_id=current_user_id,
            order="desc",
            session=session,
            offset=offset,
        )

        return AllMessagesResponseDto(
            page=page,
            limit=limit,
            total_pages=0 if count == 0 else math.ceil(count / limit),
            total_messages=count,
            data=[
                MessageBaseDto.model_validate(message, from_attributes=True)
                for message in all_messages
                if message
            ],
        )

    async def update_message(
        self,
        request: Request,
        session: AsyncSession,
        schema: UpdateMessageDto,
    ) -> typing.Union[UpdateMessageResponseDto, None]:
        """
        Updates a message.

        Args:
            request (Request): The request object.
            session (AsyncSession): The database async session object.
            schema (pydantic): The request payload
        Returns:
            UpdateMessageResponseDto (pydantic): The response payload
        """
        claims: dict = request.state.claims
        current_user_id = claims.get("user_id", "")

        message_exists = await direct_message_repository.fetch(
            session=session,
            message_id=schema.message_id,
            conversation_id=schema.conversation_id,
        )
        if not message_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid message id",
            )
        if message_exists.sender_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have enough access",
            )
        if (
            message_exists
            and message_exists.sender_id == current_user_id
            and message_exists.is_deleted_for_sender
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Message not found."
            )
        if (
            message_exists
            and message_exists.recipient_id == current_user_id
            and message_exists.is_deleted_for_recipient
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Message not found."
            )
        now = datetime.now(timezone.utc)

        if (
            message_exists.created_at.replace(tzinfo=timezone.utc)
            + timedelta(minutes=15)
        ) < (now + timedelta(seconds=0)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update after 15 minutes of sending a message",
            )
        updated_message = await direct_message_repository.update(
            user_id=current_user_id,
            session=session,
            content=schema.message,
            message=message_exists,
        )

        return UpdateMessageResponseDto(
            data=MessageBaseDto.model_validate(updated_message, from_attributes=True)
        )

    async def delete_messages(
        self, schema: DeleteMessageDto, session: AsyncSession, request: Request
    ) -> typing.Union[DeleteMessageResponseDto, None]:
        """
        Deletes messages.

        Args:
            request (Request): The request object.
            session (AsyncSession): The database async session object.
            schema (pydantic): The request payload
        Returns:
            DeleteMessageResponseDto (pydantic): The response payload
        """
        claims: dict = request.state.claims

        current_user_id = claims.get("user_id", "")

        if not schema.delete_for_both:
            for message_id in schema.message_ids:
                message_exists = await direct_message_repository.fetch(
                    session=session, message_id=message_id, conversation_id=None
                )
                if not message_exists:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Message with id {message_id} not found",
                    )

                affected_row = await direct_message_repository.delete_for_sender(
                    session=session,
                    conversation_id=None,
                    message_id=message_id,
                    user_id=current_user_id,
                )

        else:
            for message_id in schema.message_ids:
                message_exists = await direct_message_repository.fetch(
                    session=session, message_id=message_id, conversation_id=None
                )
                if not message_exists:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Message with id {message_id} not found",
                    )

                affected_row = await direct_message_repository.delete_for_all(
                    session=session, message_id=message_id, user_id=current_user_id
                )
                if affected_row < 1:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot delete message after 15 minutes",
                    )
        await session.commit()

        return DeleteMessageResponseDto()


direct_message_service = DirectMessageService()
