"""
Room Invitation service module
"""

import typing
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request, HTTPException, status

from app.repository.v1.room_invitation_repository import room_invitation_repository
from app.repository.v1.user_repository import user_repository
from app.repository.v1.room_repository import room_repository
from app.repository.v1.room_member_repository import room_member_repository
from app.dto.v1.room_inivitation_dto import (
    RoomInvitationBaseDto,
    RoomInvitationRequestDto,
    RoomInvitationResponseDto,
)


class RoomInvitationService:
    """
    Room invitation service class
    """

    async def create_room_invitation(
        self, request: Request, session: AsyncSession, schema: RoomInvitationRequestDto
    ) -> typing.Optional[RoomInvitationResponseDto]:
        """
        Creates a new room invitation
        """
        claims: dict = request.state.claims
        current_user_id = claims.get("user_id", "")
        if current_user_id == schema.invitee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot invite self to room",
            )

        room_exists = await room_repository.fetch(
            session=session, room_id=schema.room_id
        )
        if not room_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room does not exist.",
            )

        invitee_exists = await user_repository.fetch_by_id(
            session=session, user_id=schema.invitee_id
        )
        if not invitee_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitee not found",
            )

        is_current_user_a_member = await room_member_repository.fetch(
            room_id=schema.room_id, session=session, member_id=current_user_id
        )
        if not is_current_user_a_member or is_current_user_a_member.left_room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not part of the Room.",
            )
        if (
            not room_exists.allow_non_admin_invitations
            and not is_current_user_a_member.is_admin
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invitation only alowed for Admins",
            )
        is_invited_user_a_member = await room_member_repository.fetch(
            room_id=schema.room_id, session=session, member_id=schema.invitee_id
        )
        if is_invited_user_a_member and not is_invited_user_a_member.left_room:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Invited User is already a member",
            )
        invitation_exists = await room_invitation_repository.fetch(
            session=session,
            room_id=schema.room_id,
            invitee_id=schema.invitee_id,
            inviter_id=None,
            invitation_status=None,
        )

        if (
            is_invited_user_a_member
            and is_invited_user_a_member.left_room
            and invitation_exists
        ):
            await room_invitation_repository.update(
                session=session, invitation_id=invitation_exists.id, status="pending"
            )
            invitation_base = RoomInvitationBaseDto.model_validate(
                invitation_exists, from_attributes=True
            )
            return RoomInvitationResponseDto(data=invitation_base)

        if invitation_exists and invitation_exists.invitation_status == "pending":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Invitee already has an Invitation to this room.",
            )
        if invitation_exists and invitation_exists.invitation_status in [
            "cancelled",
            "expired",
            "declined",
        ]:
            await room_invitation_repository.update(
                session=session, invitation_id=invitation_exists.id, status="pending"
            )
            invitation_base = RoomInvitationBaseDto.model_validate(
                invitation_exists, from_attributes=True
            )
            return RoomInvitationResponseDto(data=invitation_base)

        new_invitation = await room_invitation_repository.create(
            session=session,
            room_id=schema.room_id,
            invitee_id=schema.invitee_id,
            inviter_id=current_user_id,
        )
        invitation_base = RoomInvitationBaseDto.model_validate(
            new_invitation, from_attributes=True
        )
        return RoomInvitationResponseDto(data=invitation_base)


room_invitation_service = RoomInvitationService()
