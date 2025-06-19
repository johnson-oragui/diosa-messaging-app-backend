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
    RoomInvitationUpdateRequestDto,
    RoomInvitationUpdateResponseDto,
)


class RoomInvitationService:
    """
    Room invitation service class
    """

    async def create_room_invitation(
        self, request: Request, session: AsyncSession, schema: RoomInvitationRequestDto
    ) -> typing.Optional[RoomInvitationResponseDto]:
        """
        Creates a new room invitation.

        Args:
            request (Request): The request object.
            session (AsyncSession): The database async session object.
            schema (RoomInvitationRequestDto): The request payload.
        Returns:
            RoomInvitationResponseDto (pydantic): The response payload
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
            invitation_id=None,
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

    async def update_room_invitation_request(
        self,
        request: Request,
        session: AsyncSession,
        schema: RoomInvitationUpdateRequestDto,
    ) -> typing.Optional[RoomInvitationUpdateResponseDto]:
        """
        Updates room invitation request.

        Args:
            request (Request): The request object.
            session (AsyncSession): The database async session object.
            schema (RoomInvitationUpdateRequestDto): The request payload.
        Returns:
            RoomInvitationUpdateResponseDto (pydantic): The response payload
        """
        message = "Invitation request updated successfully."
        claims: dict = request.state.claims
        current_user_id = claims.get("user_id", "")

        room_exists = await room_repository.fetch(
            session=session, room_id=schema.room_id
        )
        if not room_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
            )
        if room_exists.is_deactivated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room deactivated. New Members no longer allowed",
            )

        invitation_exists = await room_invitation_repository.fetch(
            session=session,
            invitation_id=schema.invitation_id,
            invitation_status=None,
            invitee_id=None,
            inviter_id=None,
            room_id=None,
        )
        if not invitation_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found"
            )
        if current_user_id not in [
            invitation_exists.inviter_id,
            invitation_exists.invitee_id,
        ]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has not enough access to this invitation",
            )
        is_room_member = await room_member_repository.fetch(
            session=session, member_id=current_user_id, room_id=schema.room_id
        )

        if schema.action.value == "cancel":
            # admin or inviter is cancelling invitation
            if is_room_member and is_room_member.left_room:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User already left the Room.Cannot cancel invitation",
                )
            if is_room_member and not is_room_member.is_admin:
                # check if room-invitation allowed for non-admins
                if not room_exists.allow_non_admin_invitations:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Room only allows privileges to Admins",
                    )
            # handle case where room-invitation has already been accepted
            if invitation_exists.invitation_status != "pending":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Cannot cancel request, invitation is already {invitation_exists.invitation_status}",
                )
            await room_invitation_repository.update(
                session=session, status="cancelled", invitation_id=schema.invitation_id
            )
            message = "Invitation request cancelled successfully."
        elif schema.action.value == "decline":
            # invitee is declining the invitation
            if invitation_exists.invitee_id != current_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot decline invitation for invitee",
                )
            if invitation_exists.invitation_status != "pending":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Cannot decline invitation request, invitation is already {invitation_exists.invitation_status}",
                )
            await room_invitation_repository.update(
                session=session, status="declined", invitation_id=schema.invitation_id
            )
            message = "Invitation request declined successfully."

        elif schema.action.value == "accept":
            # invitee is accepting the invitation
            if invitation_exists.invitee_id != current_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot accept invitation for invitee",
                )
            if invitation_exists.invitation_status != "pending":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Cannot accept invitation request, invitation is already {invitation_exists.invitation_status}",
                )
            await room_invitation_repository.update(
                session=session, status="accepted", invitation_id=schema.invitation_id
            )
            _ = await room_member_repository.create(
                room_id=schema.room_id,
                session=session,
                is_admin=False,
                member_id=invitation_exists.invitee_id,
            )
            message = "Invitation request accepted successfully."
        await session.refresh(
            instance=invitation_exists, attribute_names=["invitation_status"]
        )
        return RoomInvitationUpdateResponseDto(
            data={
                "invitation_status": invitation_exists.invitation_status,
                "invitation_id": schema.invitation_id,
            },
            message=message,
        )


room_invitation_service = RoomInvitationService()
