from typing import Annotated
from fastapi import APIRouter, Depends, Request, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.utils.task_logger import create_logger
from app.v1.auth.dependencies import (
    check_for_access_token,
    get_current_active_user,
)
from app.database.session import get_session
from app.v1.rooms.services import (
    room_service,
    room_member_service,
    room_invitation_service
)
from app.v1.chats.services import message_service
from app.v1.rooms.schemas import *
from app.core.custom_exceptions import (
    UserDoesNotExistError,
    CannotDeleteMessageError,
    CannotUpdateMessageError,
    InvitationNotFoundError,
    RoomNotFoundError,
)
from app.v1.chats.schemas import (
    AllMessagesResponse,
    MessageDeleteSchema,
    UpdateMessageInput,
    UpdateMessageResponse,
    BaseMessage,
)
from app.utils.celery_setup.tasks import (
    update_roommembers_room_data_in_batches,
    update_room_messages_room_data_in_batches,
)

logger = create_logger("Rooms Route")

rooms = APIRouter(prefix="/rooms", tags=["ROOMS"])


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
    room = await room_service.fetch(
        {
            "id": room_id,
            "is_deleted": False,
        },
        session=session
    )
    if not room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room does not exists or has been deleted."
        )

    messages_list = await message_service.fetch_room_messages(
        room_id=room_id,
        filterer={},
        session=session
    )

    return AllMessagesResponse(data=messages_list)

# TODO: update private/public room messages
@rooms.patch("/{room_id}/messages/{message_id}", status_code=status.HTTP_200_OK,
             response_model=UpdateMessageResponse)
async def update_room_messages(room_id: str, message_id: str, request: Request,
                               schema: UpdateMessageInput,
                               token: Annotated[str, Depends(check_for_access_token)],
                               session: Annotated[AsyncSession, Depends(get_session)]):
    """
    Updates a room message.
    """
    user = await get_current_active_user(
        access_token=token,
        request=request,
        session=session
    )
    try:
        updated_message = await message_service.update_message(
            room_id=room_id,
            user_id=user.id,
            session=session,
            message=schema.message,
            message_id=message_id
        )
    except CannotUpdateMessageError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exc.args[0]}"
        )
    return UpdateMessageResponse(
        data=BaseMessage(
            room_id=room_id,
            content=schema.message,
            created_at=updated_message.created_at,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=None
        )
    )

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

@rooms.put("/{room_id}", response_model=UpdateRoomResponse, status_code=status.HTTP_201_CREATED)
async def update_room_fields(room_id: str, schema: UpdateRoomSchema,
                           request: Request,
                            token: Annotated[str, Depends(check_for_access_token)],
                            session: Annotated[AsyncSession, Depends(get_session)],):
    """
    Updates room(s) field.
    """
    user = await get_current_active_user(
        access_token=token,
        request=request,
        session=session,
    )
    room_is_deleted = await room_service.fetch(
        {
            "id": room_id,
            "is_deleted": True,
        },
        session
    )
    if room_is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room does not exist or has been deleted."
        )
    user_is_admin = await room_member_service.fetch(
        {
            "user_id": user.id,
            "is_admin": True,
            "room_id": room_id,
        },
        session
    )
    if not user_is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not an admin of the room."
        )
    update_fields = {}
    if schema.room_type:
        # Defer the updating of related data (messages, room members)
        task_id1 = update_roommembers_room_data_in_batches.delay(
            room_id,
            schema.room_type
        )
        task_id2 = update_room_messages_room_data_in_batches.delay(
            room_id,
            schema.room_type
        )
        logger.info(f"task_id1: {task_id1}, task_id2: {task_id2}")
        update_fields.update({"room_type": schema.room_type})

    if schema.messages_deletable is not None:
        update_fields.update({"messages_deletable": schema.messages_deletable})
    if schema.description:
        update_fields.update({"description": schema.description})
    logger.info(f"update_fields: {update_fields}")

    # Perform the update in the room service
    updated_room = await room_service.update(
        [
            {
                "id": room_id,
                "is_deleted": False,
            },
            update_fields
        ],
        session
    )

    logger.info(f"updated_room: {updated_room}")

    return UpdateRoomResponse(
        data=RoomBase.model_validate(updated_room, from_attributes=True)
    )


# TODO: delete private/public room
@rooms.delete(
    "/{room_id}", status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_room(room_id: str, request: Request,
                      token: Annotated[str, Depends(check_for_access_token)],
                      session: Annotated[AsyncSession, Depends(get_session)]):
    """
    Deletes a public/private room.
    """
    user = await get_current_active_user(
        access_token=token,
        request=request,
        session=session,
    )
    direct_message_room = await room_service.fetch(
        {
            "id": room_id,
            "room_type": "direct_message",
        },
        session=session
    )
    if direct_message_room:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot Delete Direct-Message Room."
        )
    room = await room_service.fetch(
        {
            "id": room_id,
            "creator_id": user.id,
            "is_deleted": False,
        },
        session=session
    )
    if not room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room does not exist or has already been deleted."
        )

    if room.idempotency_key:
        room.idempotency_key = f"{str(uuid4())}_deleted"
    room.is_deleted = True
    await session.commit()

    return


# TODO: invite user to room
@rooms.post("/{room_id}/invite", status_code=status.HTTP_200_OK,
            response_model=RoomInvitationResponse)
async def invite_user_to_room(room_id: str, request: Request,
                              schema: RoomInvitationInput,
                              token: Annotated[str, Depends(check_for_access_token)],
                              session: Annotated[AsyncSession, Depends(get_session)]):
    """
    Invites a user to a room.
    """
    user = await get_current_active_user(
        access_token=token,
        request=request,
        session=session,
    )
    try:
        invitation = await room_invitation_service.invite_user_to_room(
            room_id=room_id,
            invitee_id=schema.invitee_id,
            inviter_id=user.id,
            session=session
        )

        return RoomInvitationResponse(
            data=InvitationBase.model_validate(invitation, from_attributes=True)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{exc.args[0]}"
        )

# TODO: accept/reject room invitation
@rooms.post("/{room_id}/accept-invite", status_code=status.HTTP_200_OK,
            response_model=AcceptInvitationResponse)
async def accept_invitation_to_room(room_id: str, request: Request,
                              schema: AcceptInvitationInput,
                              token: Annotated[str, Depends(check_for_access_token)],
                              session: Annotated[AsyncSession, Depends(get_session)]):
    """
    Allows a user to accept an invitation.
    """
    user = await get_current_active_user(
        access_token=token,
        request=request,
        session=session,
    )
    try:
        invitation, room_member = await room_invitation_service.accept_room_invitations(
            invitee_id=user.id,
            invitation_id=schema.invitation_id,
            room_id=room_id,
            session=session
        )
        if invitation and not room_member:
            # invitation has already been accepted
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already a member"
            )
        logger.info(msg=f"invitation: {invitation}")
        return AcceptInvitationResponse(
                data=InvitationBase.model_validate(invitation, from_attributes=True)
            )
    except (
            UserDoesNotExistError,
            CannotDeleteMessageError,
            CannotUpdateMessageError,
            InvitationNotFoundError,
            RoomNotFoundError,
        ) as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{exc.args[0]}"
        )


# TODO: cancel pending room invitations
# TODO: get pending room invitations
# TODO: get accepted room invitations
# TODO: get  rejected room invitations
# TODO: get  ignored room invitations


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
