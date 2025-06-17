"""
Room Member Route Module
"""

import typing
from fastapi import APIRouter, status, Request, Depends

from app.utils.responses import responses
from app.service.v1.room_invitation_service import room_invitation_service, AsyncSession
from app.dto.v1.room_inivitation_dto import (
    RoomInvitationRequestDto,
    RoomInvitationResponseDto,
)
from app.core.security import validate_logout_status
from app.database.session import get_async_session

room_invitation_router = APIRouter(prefix="/room-invitations", tags=["ROOM INVITATION"])


@room_invitation_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses=responses,
    response_model=RoomInvitationResponseDto,
    dependencies=[Depends(validate_logout_status)],
)
async def invite_users_to_room(
    request: Request,
    schema: RoomInvitationRequestDto,
    session: typing.Annotated[AsyncSession, Depends(get_async_session)],
) -> typing.Optional[RoomInvitationResponseDto]:
    """
    Invites Users to a room.

    Return:
        Success message upon success
    Raises:
        422
        500
        409
        401
        404
    """
    return await room_invitation_service.create_room_invitation(
        schema=schema, request=request, session=session
    )
