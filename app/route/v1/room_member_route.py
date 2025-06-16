"""
Room Member Route Module
"""

import typing
from fastapi import APIRouter, status, Request, Depends

from app.utils.responses import responses
from app.service.v1.room_member_service import room_member_service, AsyncSession
from app.dto.v1.room_member_dto import (
    RoomMebersResponseDto,
    AddRoomMemberRequestDto,
    AddRoomMemberResponseDto,
)
from app.core.security import validate_logout_status
from app.database.session import get_async_session

room_members_router = APIRouter(prefix="/room-members", tags=["ROOM MEMBERS"])


@room_members_router.get(
    "/{room_id}",
    status_code=status.HTTP_200_OK,
    responses=responses,
    response_model=RoomMebersResponseDto,
    dependencies=[Depends(validate_logout_status)],
)
async def retrieve_room_members(
    request: Request,
    room_id: str,
    session: typing.Annotated[AsyncSession, Depends(get_async_session)],
) -> typing.Optional[RoomMebersResponseDto]:
    """
    Retrieves all room members.

    Return:
        Success message upon success
    Raises:
        422
        500
        409
        401
        404
    """
    return await room_member_service.retrieve_room_members(
        room_id=room_id, request=request, session=session
    )


@room_members_router.post(
    "/{room_id}",
    status_code=status.HTTP_201_CREATED,
    responses=responses,
    response_model=AddRoomMemberResponseDto,
    dependencies=[Depends(validate_logout_status)],
)
async def add_room_member(
    request: Request,
    room_id: str,
    schema: AddRoomMemberRequestDto,
    session: typing.Annotated[AsyncSession, Depends(get_async_session)],
) -> typing.Optional[AddRoomMemberResponseDto]:
    """
    Adds a new room member.

    Return:
        Success message upon success
    Raises:
        422
        500
        409
        401
        404
    """
    return await room_member_service.add_room_member(
        room_id=room_id, request=request, session=session, schema=schema
    )
