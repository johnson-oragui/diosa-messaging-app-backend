"""
Room Message route module
"""

import typing

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto.v1.room_message_dto import (
    SendRoomMessageResponseDto,
    SendRoomMessageRequestDto,
)
from app.utils.responses import responses
from app.core.security import validate_logout_status
from app.database.session import get_async_session
from app.service.v1.room_message_service import room_message_service

room_message_router = APIRouter(prefix="/room-messages", tags=["ROOM MESSAGES"])


@room_message_router.post(
    "",
    responses=responses,
    response_model=SendRoomMessageResponseDto,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(validate_logout_status)],
)
async def send_room_message(
    request: Request,
    schema: SendRoomMessageRequestDto,
    session: typing.Annotated[AsyncSession, Depends(get_async_session)],
) -> typing.Optional[SendRoomMessageResponseDto]:
    """
    Sends messages to a room.

    Return:
        Success message upon success
    Raises:
        HTTPException 401: when not authenticated.
        HTTPException 401: when invalid access token.
        HTTPException 401: when access token is blacklisted.
        HTTPException 404: when room not found.
        HTTPException 403: when Room is deactivated.
        HTTPException 403: when User not a member.
        HTTPException 403: when User already left room.
        HTTPException 403: when Only Room Admins can send messages.
    """
    return await room_message_service.create_room_message(
        request=request, session=session, schema=schema
    )
