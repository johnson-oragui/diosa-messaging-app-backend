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

    def __init__(self) -> None:
        """
        Constructor.
        """
        self.model = RoomInvitation

    async def create(
        self, session: AsyncSession, room_id: str, inviter_id: str, invitee_id: str
    ) -> RoomInvitation:
        """
        Creates a room invitation.

        Args:
            session (AsyncSession): The database async session object.
            room_id (str): The id of the Room for invitation.
            inviter_id (str): The id of the user inviting another user.
            invitee_id (str): The id of the user been invited by another user.
        Returns:
            RoomInvitation (object): The room-invitation instance.
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
        room_id: typing.Union[None, str],
        inviter_id: typing.Union[None, str],
        invitee_id: typing.Union[None, str],
        invitation_status: typing.Union[None, str],
        invitation_id: typing.Union[None, str],
        attributes: typing.List[typing.Union[str, None]] = [],
    ) -> typing.Union[None, RoomInvitation]:
        """
        Fetches a room invitation.

        Args:
            session (AsyncSession): The database async session object.
            room_id (str): The Optional id of the Room for invitation.
            inviter_id (str): The Optional id of the user inviting another user.
            invitee_id (str): The Optional id of the user been invited by another user.
            invitation_status (str): The Optional status of the invitation.
            invitation_id (str): The Optional id of the invitation.
        Returns:
            int: The number of affected rows
        """
        query = sa.select(RoomInvitation)
        if len(attributes) > 0:
            selected_fields = [
                getattr(self.model, attr)
                for attr in attributes
                if isinstance(attr, str) and hasattr(self.model, attr)
            ]
            if not selected_fields:
                return None
            else:
                query = sa.select(*selected_fields)
        if room_id:
            query = query.where(RoomInvitation.room_id == room_id)
        if inviter_id:
            query = query.where(RoomInvitation.inviter_id == inviter_id)
        if invitee_id:
            query = query.where(RoomInvitation.invitee_id == invitee_id)
        if invitation_status:
            query = query.where(RoomInvitation.invitation_status == invitation_status)
        if invitation_id:
            query = query.where(RoomInvitation.id == invitation_id)

        return (await session.execute(query)).scalar_one_or_none()

    async def update(
        self, session: AsyncSession, invitation_id: str, status: str
    ) -> int:
        """
        Updates room invitation.

        Args:
            session (AsyncSession): The database async session object.
            invitation_id (str): The id of the invitation.
            status (str): The status of the invitation.
        Returns:
            int: The number of affected rows
        """
        expiration = datetime.now(timezone.utc) + timedelta(days=7)
        query = (
            sa.update(RoomInvitation)
            .where(RoomInvitation.id == invitation_id)
            .values(invitation_status=status)
        )
        if status == "pending":
            query = query.values(expiration=expiration, invitation_status=status)

        result = await session.execute(query)
        await session.commit()

        return result.rowcount


room_invitation_repository = RoomInvitationRepository()
