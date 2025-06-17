"""
RoomInvitationRepository Module
"""

import typing
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from app.models.room_invitation import RoomInvitation


class RoomInvitationRepository:
    """
    RoomInvitationRepository class
    """

    async def create(
        self, session: AsyncSession, room_id: str, inviter_id: str, invitee_id: str
    ) -> RoomInvitation:
        """
        Creates a room invitation
        """
        expiration = datetime.now(timezone.utc) + timedelta(days=7)
        new_invitation = RoomInvitation(
            room_id=room_id,
            inviter_id=inviter_id,
            invitee_id=invitee_id,
            expiration=expiration,
        )
        session.add(new_invitation)
        await session.commit()

        return new_invitation

    async def fetch(
        self,
        session: AsyncSession,
        room_id: str,
        inviter_id: typing.Union[None, str],
        invitee_id: typing.Union[None, str],
        invitation_status: typing.Union[None, str],
    ) -> typing.Union[None, RoomInvitation]:
        """
        Fetches a room invitation
        """
        query = sa.select(RoomInvitation).where(RoomInvitation.room_id == room_id)
        if inviter_id:
            query = query.where(RoomInvitation.inviter_id == inviter_id)
        if invitee_id:
            query = query.where(RoomInvitation.invitee_id == invitee_id)
        if invitation_status:
            query = query.where(RoomInvitation.invitation_status == invitation_status)

        return (await session.execute(query)).scalar_one_or_none()

    async def update(
        self, session: AsyncSession, invitation_id: str, status: str
    ) -> int:
        """
        Updates room invitation
        """
        query = (
            sa.update(RoomInvitation)
            .where(RoomInvitation.id == invitation_id)
            .values(invitation_status=status)
        )

        result = await session.execute(query)
        await session.commit()

        return result.rowcount


room_invitation_repository = RoomInvitationRepository()
