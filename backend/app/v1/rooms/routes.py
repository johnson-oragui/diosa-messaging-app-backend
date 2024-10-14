from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    Request,
    status,
    HTTPException
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.task_logger import create_logger
from app.v1.auth.dependencies import (
    check_for_access_token,
    get_current_active_user,
)
from app.database.session import get_session
from app.v1.rooms.services import room_service
from app.v1.rooms.schemas import (
    RoomCreateSchema,
    RoomSchemaOut,
    RoomAndRoomMembersBase,
    RoomBase,
    RoomMembersBase,
    CreateDirectMessageSchema,
)
from app.core.custom_exceptions import (
    UserDoesNotExistError
)

logger = create_logger("Rooms Route")

rooms = APIRouter(prefix="/rooms")


@rooms.post("/create",
            response_model=RoomSchemaOut,
            status_code=status.HTTP_201_CREATED)
async def create_room(schema: RoomCreateSchema,
                   request: Request,
                   token: Annotated[str, Depends(check_for_access_token)],
                   session: Annotated[AsyncSession, Depends(get_session)]):
    """
    Creates a public or private room.
    """
    user = await get_current_active_user(
        access_token=token,
        request=request,
        session=session,
    )
    room, room_member, exists = await room_service.create_a_public_or_private_room(
        room_name=schema.room_name,
        creator_id=user.id,
        room_type=schema.room_type,
        session=session,
        description=schema.description,
        messages_deletable=schema.messages_deletable
    )
    if not room or not room_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST
        )
    room_and_room_members = RoomAndRoomMembersBase(
        room=RoomBase.model_validate(room, from_attributes=True),
        room_members=[RoomMembersBase.model_validate(
            room_member,
            from_attributes=True
        )]
    )
    message = "Room Created Successfully"
    if exists:
        message = "Room already exists"
    room_out = RoomSchemaOut(
        status_code=201,
        message=message,
        data=room_and_room_members
    )
    return room_out

# TODO: delete private/public room
# TODO: delete direct-message room
# TODO: update private/public room
# TODO: get private/public room
# TODO: get direct_message room

@rooms.post("/create/dm",
            response_model=RoomSchemaOut,
            status_code=status.HTTP_201_CREATED)
async def create_direct_message_room(schema: CreateDirectMessageSchema,
                   request: Request,
                   token: Annotated[str, Depends(check_for_access_token)],
                   session: Annotated[AsyncSession, Depends(get_session)]):
    """
    Creates a direct-message room.
    """
    user = await get_current_active_user(
        access_token=token,
        request=request,
        session=session,
    )
    try:
        room, room_members, exists = await room_service.create_direct_message_room(
            user_id_1=user.id,
            user_id_2=schema.receiver_id,
            session=session,
        )
    except UserDoesNotExistError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.args[0])
    room_and_room_members = RoomAndRoomMembersBase(
        room=RoomBase.model_validate(room, from_attributes=True),
        room_members=[RoomMembersBase.model_validate(member, from_attributes=True) for member in room_members]
    )
    message = "Room Created Successfully"
    if exists:
        message = "Room already exists"
    room_out = RoomSchemaOut(
        status_code=201,
        message=message,
        data=room_and_room_members
    )
    return room_out

__all__ = ["rooms"]
