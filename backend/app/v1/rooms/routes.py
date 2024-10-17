from typing import Annotated
from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.task_logger import create_logger
from app.v1.auth.dependencies import (
    check_for_access_token,
    get_current_active_user,
)
from app.database.session import get_session
from app.v1.rooms.services import (
    room_service,
)
from app.v1.chats.services import message_service
from app.v1.rooms.schemas import *
from app.core.custom_exceptions import (
    UserDoesNotExistError,
    CannotDeleteMessageError,
)
from app.v1.chats.schemas import (
    AllMessagesResponse,
    MessageDeleteSchema
)

logger = create_logger("Rooms Route")

rooms = APIRouter(prefix="/rooms")


@rooms.post(
    "/create", response_model=RoomSchemaOut, status_code=status.HTTP_201_CREATED
)
async def create_room(
    schema: RoomCreateSchema,
    request: Request,
    token: Annotated[str, Depends(check_for_access_token)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
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
        messages_deletable=schema.messages_deletable,
    )
    if not room or not room_member:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    room_and_room_members = RoomAndRoomMembersBase(
        room=RoomBase.model_validate(room, from_attributes=True),
        room_members=[
            RoomMembersBase.model_validate(room_member, from_attributes=True)
        ],
    )
    message = "Room Created Successfully"
    if exists:
        message = "Room already exists"
    room_out = RoomSchemaOut(
        status_code=201, message=message, data=room_and_room_members
    )
    return room_out


@rooms.get("", status_code=status.HTTP_200_OK)
async def get_rooms(
    request: Request,
    token: Annotated[str, Depends(check_for_access_token)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Retrieves all rooms a user belongs to.
    """
    user = await get_current_active_user(
        access_token=token,
        request=request,
        session=session,
    )

    rooms = await room_service.fetch_rooms_user_belongs_to(
        user.id,
        session
    )

    rooms_base: list| None = [RoomBase.model_validate(room, from_attributes=True) for room in rooms if room]

    return RoomBelongsToResponse(data=rooms_base)

@rooms.get("/{room_id}/messages", status_code=status.HTTP_200_OK,
           response_model=AllMessagesResponse)
async def get_room_messages(room_id: str, request: Request,
                            token: Annotated[str, Depends(check_for_access_token)],
                            session: Annotated[AsyncSession, Depends(get_session)]):
    """
    retrieves all messages for a specific room.
    """
    _ = await get_current_active_user(
        access_token=token,
        request=request,
        session=session
    )

    messages_list = await message_service.fetch_room_messages(
        room_id=room_id,
        filterer={},
        session=session
    )

    return AllMessagesResponse(data=messages_list)

@rooms.delete("/{room_id}/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room_message(room_id: str, message_id: int,
                              request: Request,
                              token: Annotated[str, Depends(check_for_access_token)],
                              session: Annotated[AsyncSession, Depends(get_session)]):
    """
    Delete single room message.
    """
    user = await get_current_active_user(
        access_token=token,
        request=request,
        session=session
    )
    try:
        _ = await message_service.delete_message(
            room_id=room_id,
            user_id=user.id,
            session=session,
            message_id=message_id
        )
    except CannotDeleteMessageError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exc.args[0]}"
        )
    return

@rooms.delete("/{room_id}/messages", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room_messages(room_id: str, request: Request,
                              token: Annotated[str, Depends(check_for_access_token)],
                              session: Annotated[AsyncSession, Depends(get_session)],
                              schema: MessageDeleteSchema):
    """
    Delete single or multiple room messages.
    """
    user = await get_current_active_user(
        access_token=token,
        request=request,
        session=session
    )
    try:
        _ = await message_service.delete_message(
            room_id=room_id,
            user_id=user.id,
            session=session,
            message_ids=schema.message_ids
        )
    except CannotDeleteMessageError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exc.args[0]}"
        )
    return

# TODO: delete private/public room
# TODO: delete direct-message room
# TODO: update private/public room

@rooms.post(
    "/create/dm", response_model=RoomSchemaOut, status_code=status.HTTP_201_CREATED
)
async def create_direct_message_room(
    schema: CreateDirectMessageSchema,
    request: Request,
    token: Annotated[str, Depends(check_for_access_token)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
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
        room_members=[
            RoomMembersBase.model_validate(member, from_attributes=True)
            for member in room_members
        ],
    )
    message = "Room Created Successfully"
    if exists:
        message = "Room already exists"
    room_out = RoomSchemaOut(
        status_code=201, message=message, data=room_and_room_members
    )
    return room_out


@rooms.get("/dm", status_code=status.HTTP_200_OK,
           response_model=AllDirectRoomsResponse)
async def get_direct_message_room(
    request: Request,
    token: Annotated[str, Depends(check_for_access_token)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Retrieves all direct_message rooms a user has.
    """
    user = await get_current_active_user(
        access_token=token,
        request=request,
        session=session,
    )

    direct_msg_rooms = await room_service.fetch_user_direct_message_rooms(
        user.id,
        session
    )

    return AllDirectRoomsResponse(data=direct_msg_rooms)


__all__ = ["rooms"]
