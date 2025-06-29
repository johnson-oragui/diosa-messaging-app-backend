"""
Room Message route module
"""

import typing

from fastapi import APIRouter, Depends, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto.v1.room_message_dto import (
    SendRoomMessageResponseDto,
    SendRoomMessageRequestDto,
    AllRoomMessagesResponseDto,
    RoomMessageOrderEnum,
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


@room_message_router.get(
    "/{room_id}",
    status_code=status.HTTP_200_OK,
    responses=responses,
    response_model=AllRoomMessagesResponseDto,
    dependencies=[Depends(validate_logout_status)],
)
async def retrieve_messages(
    request: Request,
    room_id: str,
    session: typing.Annotated[AsyncSession, Depends(get_async_session)],
    order_by: RoomMessageOrderEnum = Query(
        default=RoomMessageOrderEnum.DESC,
        description="The order of the messages. (Optional)",
    ),
    page: int = Query(default=1, ge=1, description="The current page"),
    limit: int = Query(
        default=50, ge=1, le=50, description="The size of messages per page"
    ),
) -> typing.Optional[AllRoomMessagesResponseDto]:
    """
    Retrieve messages of a room.

    Return:
        Success message upon success
    Raises:
        422
        500
        409
        401
        404
    """
    return await room_message_service.fetch_room_messages(
        page=page,
        limit=limit,
        room_id=room_id,
        session=session,
        request=request,
        order_by=order_by,
    )
