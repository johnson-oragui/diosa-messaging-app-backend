"""
Room message service module
"""

import typing
import math
from datetime import datetime, timedelta, timezone

from fastapi import Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto.v1.room_message_dto import (
    SendRoomMessageResponseDto,
    SendRoomMessageRequestDto,
    RoomMessageBaseDto,
    AllRoomMessagesResponseDto,
    RoomMessageOrderEnum,
    UpdateRoomMessageResponseDto,
    UpdateRoomMessageDto,
)
from app.repository.v1.room_message_repository import room_message_repository
from app.repository.v1.room_repository import room_repository
from app.repository.v1.room_member_repository import room_member_repository
from app.utils.task_logger import create_logger

logger = create_logger(":::: RoomMessageService ::::")


class RoomMessageService:
    """
    Roommessage service class
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self.repository = room_message_repository

    async def create_room_message(
        self, request: Request, session: AsyncSession, schema: SendRoomMessageRequestDto
    ) -> typing.Optional[SendRoomMessageResponseDto]:
        """
        Creates and Sends a message to a room.

        Args:
            request (Request): The request object.
            session (AsyncSession): The database async session object.
            schema (pydantic): The payload request object.
        Returns:
            SendRoomMessageResponseDto (pydantic): The payoad response object.
        Raises:
            HTTPException 404: when room not found.
            HTTPException 403: when Room is deactivated.
            HTTPException 403: when User not a member.
            HTTPException 403: when User already left room.
            HTTPException 403: when Only Room Admins can send messages.
        """
        claims: dict = request.state.claims
        current_user_id = claims.get("user_id", "")

        room_exists = await room_repository.fetch(
            session=session,
            room_id=schema.room_id,
            attributes=["allow_admin_messages_only", "is_deactivated"],
        )
        if room_exists is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
            )
        if room_exists.is_deactivated:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Room is deactivated"
            )

        is_room_member = await room_member_repository.fetch(
            session=session,
            member_id=current_user_id,
            room_id=schema.room_id,
            attributes=["left_room", "is_admin"],
        )
        if is_room_member is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User not a member"
            )
        if is_room_member.left_room:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User already left room"
            )

        if room_exists.allow_admin_messages_only and not is_room_member.is_admin:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Room Admins can send messages",
            )

        new_room_message = await self.repository.create(
            session=session,
            content=schema.message,
            sender_id=current_user_id,
            room_id=schema.room_id,
            parent_message_id=schema.parent_message_id,
            media_url=schema.media_url and str(schema.media_url),
            media_type=schema.media_type,
        )

        room_base_dto = RoomMessageBaseDto.model_validate(
            new_room_message, from_attributes=True
        )

        return SendRoomMessageResponseDto(data=room_base_dto)

    async def fetch_room_messages(
        self,
        request: Request,
        session: AsyncSession,
        page: int,
        limit: int,
        room_id: str,
        order_by: RoomMessageOrderEnum,
    ) -> typing.Optional[AllRoomMessagesResponseDto]:
        """
        Retrieves all room messages.

        Args:
            request (Request): The request object.
            session (AsyncSession): The database async session object.
            page (int): The current page.
            limit (int): The number of messages per page
            room_id (str): The id of the messages to retrieve
            order_by (str): The order of the messages to fetch (default=desc)
        Returns:
            AllRoomMessagesResponseDto (pydantic): The response payload
        """
        claims: dict = request.state.claims
        current_user_id = claims.get("user_id", "")
        offset = page * limit - limit

        room_exists = await room_repository.fetch(session=session, room_id=room_id)
        if not room_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
            )

        is_user_member = await room_member_repository.fetch(
            session=session,
            room_id=room_id,
            member_id=current_user_id,
            attributes=["left_room"],
        )
        if is_user_member is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User not Room member"
            )
        if is_user_member.left_room:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User already left room"
            )

        all_messages, count = await room_message_repository.fetch_all(
            room_id=room_id,
            order=order_by.value,
            session=session,
            offset=offset,
        )

        return AllRoomMessagesResponseDto(
            page=page,
            limit=limit,
            total_pages=0 if count == 0 else math.ceil(count / limit),
            total_messages=count,
            data=[
                RoomMessageBaseDto.model_validate(message, from_attributes=True)
                for message in all_messages
                if message
            ],
        )

    async def update_message(
        self,
        request: Request,
        session: AsyncSession,
        schema: UpdateRoomMessageDto,
        room_id: str,
    ) -> typing.Union[UpdateRoomMessageResponseDto, None]:
        """
        Updates a message.

        Args:
            request (Request): The request object.
            session (AsyncSession): The database async session object.
            schema (pydantic): The request payload
            room_id (str): The id of the room
        Returns:
            UpdateRoomMessageResponseDto (pydantic): The response payload
        """
        claims: dict = request.state.claims
        current_user_id = claims.get("user_id", "")

        room_exists = await room_repository.fetch(session=session, room_id=room_id)
        if not room_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
            )

        is_user_member = await room_member_repository.fetch(
            session=session,
            room_id=room_id,
            member_id=current_user_id,
            attributes=["left_room"],
        )
        if is_user_member is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User not Room member"
            )
        if is_user_member.left_room:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User already left room"
            )

        message_exists = await room_message_repository.fetch(
            session=session,
            message_id=schema.message_id,
            room_id=room_id,
        )
        if not message_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid message id",
            )
        if message_exists.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found",
            )
        if message_exists.sender_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update another User message!!!",
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
        updated_message = await room_message_repository.update(
            user_id=current_user_id,
            session=session,
            content=schema.message,
            message=message_exists,
        )

        return UpdateRoomMessageResponseDto(
            data=RoomMessageBaseDto.model_validate(
                updated_message, from_attributes=True
            )
        )


room_message_service = RoomMessageService()
