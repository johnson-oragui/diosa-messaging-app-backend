"""
Room Services Module
"""
from typing import Sequence, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.base.services import Service
from app.v1.rooms import (
    Room,
    RoomMember,
    RoomInvitation
)
from app.core.custom_exceptions import (
    RoomNotFoundError,
    UserNotAMemberError,
    UserNotAnAdminError,
    InvitationNotFoundError
)
from app.utils.task_logger import create_logger

logger = create_logger("Room Service")
    

class RoomService(Service):
    """
    Service class for Room
    """
    def __init__(self):
        super().__init__(Room)

    async def create_a_public_or_private_room(self,
                            room_name: str,
                            creator_id: str,
                            session: AsyncSession,
                            room_type: str = "private",
                            description: str = "",
                            messages_deletable: bool = True) -> Tuple[Optional[Room], Optional[RoomMember]]:
        """
        Create a room private or public room and make the creator an admin.

        Args:
            room_name(str): the name to be given to the room.
            creator_id(str): The id of the user creating the room.
            session(object): database session object.
            room_type(str): the type of room,e.g private, public
            description(str): The description of the room. Optional.
            messages_deletable: Flag that sets if the room messages are deletable.
        Returns:
            tuple(Room, RoomMember): if room is created, and tuple(None, None) if not.
        """
        if room_type == "direct_message":
            return None, None
        new_room = await self.create(
            {
                "creator_id": creator_id,
                "room_type": room_type,
                "room_name": room_name,
                "description": description,
                "messages_deletable": messages_deletable
            },
            session,
        )
        # If private, add the creator to the room and make them admin
        room_member = await room_member_service.create(
            {
                "user_id": creator_id,
                "room_id": new_room.id,
                "is_admin": True,
                "room_type": new_room.room_type,
            },
            session,
        )

        logger.info(msg=f"Room {new_room.id} ({room_type}) created by user {creator_id}.")
        return new_room, room_member

    async def create_direct_message_room(self, user_id_1: str,
                                         user_id_2: str,
                                         session: AsyncSession) -> Room:
        """
        Create a direct-message type of room.

        Args:
            user_id_1(str): The user_id of the engaging user.
            user_id_2(str): The user_id of the user been enganged in a conversation.
            session(object): database session object.
        Returns:
            Room: The room created.
        """
        # Check if a direct message room already exists between these two users
        stmt = select(Room).join(
            RoomMember, Room.id == RoomMember.room_id
        ).filter(
            Room.room_type == "direct_message"
        ).filter(
            or_(
                RoomMember.user_id == user_id_1,
                RoomMember.user_id == user_id_2
            )
        )
        result = await session.execute(stmt)
        existing_room = result.scalar_one_or_none()

        if existing_room:
            # Return existing DM room
            return existing_room

        # Create new DM room if DM room does not exists
        new_dm_room = await self.create(
            {
                "creator_id": user_id_1,
                "room_type": "direct_message",
                "room_name": f"DM-{user_id_1}-{user_id_2}",
            },
            session
        )

        # Add both users to the room
        await room_member_service.create_all(
            [
                {
                    "user_id": user_id_1,
                    "is_admin": True,
                    "room_id": new_dm_room.id,
                    "room_type": new_dm_room.room_type
                },
                {
                    "user_id": user_id_2,
                    "is_admin": True,
                    "room_id": new_dm_room.id,
                    "room_type": new_dm_room.room_type
                }
            ],
            session
        )
        return new_dm_room

    async def search_public_rooms(self, keyword: str, session: AsyncSession) -> Sequence[Room]:
        """
        Retrieves all public rooms similar to search terms provided.

        Args:
            keyword(str): the name of the room or similar room to fetch.
            session(object): database session object.
        Returns:
            A list of rooms if the search matches any room.
        """
        stmt = select(Room).where(
            Room.room_type == "public"
        ).where(
            Room.room_name.ilike(f"%{keyword}%")
        )

        result = await session.execute(stmt)

        public_rooms = result.scalars().all()
        return public_rooms

class RoomMemberService(Service):
    """
    Service class for Room
    """
    def __init__(self):
        super().__init__(RoomMember)

    async def join_public_room(self, user_id: str,
                               room_id: str,
                               session: AsyncSession) -> Optional[Room]:
        """
        Adds a user to a public room.

        Args:
            user_id(str): the id of the user joining a room.
            room_id(str): The id of the public room the user is trying to join.
            session(object): database session object.
        Returns:
            Room if room exists.
        Raises:
            RoomNotFoundError if room does not exist.
        """
        public_room_to_join = await room_service.fetch(
            {
                "room_id": room_id,
                "room_type": "public"
            },
            session
        )
        if public_room_to_join:
            await self.create(
                {
                    "user_id": user_id,
                    "room_id": room_id,
                    "room_type": public_room_to_join.room_type
                },
                session
            )
            return public_room_to_join
        raise RoomNotFoundError(f"Room {room_id} not found")

    async def join_private_room_by_invite(self, user_id: str,
                                          room_id: str,
                                          session: AsyncSession) -> Optional[Room]:
        """
        Joins a private room by invite.

        Args:
            user_id(str): The id of the user joining a private room.
            room_id(str): The id of the private room the user is trying to joing.
            session(object): database session object.
        Returns:
            Room if user joined the room and room exists.
        Raises:
            RoomNotFoundError if the room does not exist.
        """
        private_room_to_join = await room_service.fetch(
            {
                "room_id": room_id,
                "room_type": "private"
            },
            session
        )
        if private_room_to_join:
            await self.create(
                {
                    "user_id": user_id,
                    "room_id": room_id,
                    "room_type": private_room_to_join.room_type
                },
                session
            )
            return private_room_to_join
        raise RoomNotFoundError(f"Room {room_id} not found")

    async def set_user_as_admin(self, room_id: str,
                                user_id: str,
                                session: AsyncSession) -> Optional[RoomMember]:
        """
        Set another member as an admin to a room.

        Args:
            room_id(str): The room where the user is to be set as an admin.
            user_id(str): The user to be set as an admin.
            session(object): Database session object.
        Returns:
            The newly added admin.
        Raises:
            UserNotAMemberError if the user is not a member of the room.
        """
        new_admin_user = await room_member_service.update(
            [
              {"user_id": user_id, "room_id": room_id},
              {"is_admin": True}
            ],
            session
        )
        if new_admin_user and new_admin_user.is_admin is True:
            logger.info(msg=f"User {user_id} is now an admin of room {room_id}.")
            return new_admin_user
        else:
            raise UserNotAMemberError(f"User {user_id} not a member of room {room_id}")

    async def is_user_admin(self, room_id: str,
                            user_id: str,
                            session: AsyncSession) -> bool:
        """
        Check if a user is an admin of the room.

        Args:
            room_id(str): The id of the room to check for admin priviledge.
            user_id(str): the id of the user.
            session(object): database session object.
        Returns:
            bool(True) if the user is an admin, False if the user is not an admin.
        """
        is_user_admin = await room_member_service.fetch(
            {
                "user_id": user_id,
                "room_id": room_id,
                "is_admin": True
            },
            session
        )

        logger.info(msg=f"User {user_id} is an admin in room {room_id}: {bool(is_user_admin)}")
        return bool(is_user_admin)


class RoomInvitationService(Service):
    """
    Room-invitation-service class
    """
    def __init__(self) -> None:
        super().__init__(RoomInvitation)

    async def invite_user_to_room(self, inviter_id: str,
                                  invitee_id: str,
                                  room_id: str,
                                  session: AsyncSession) -> Optional[RoomInvitation]:
        """
        Invite a user to a private room. Only admins or the room owner/creator can invite others to private rooms.
        All members can invite any user to a public room.

        Args:
            inviter_id(str): the id of the user making the invitation.
            invitee_id(str): the id of the user been invited.
            room_id(str): the id of the room where the user is been invited.
            session(object): database session object.
        Returns:
            RoomInvitation if successfull.
        Raises:
            UserNotAnAdminError if it not a public room, and the inviter user is not an admin.
        """
        room = await room_service.fetch(
            {"id": room_id},
            session
        )
        if room.room_type == "public":
            # create invitations
            invitations = await self.create(
                {
                    "room_id": room_id,
                    "inviter_id": inviter_id,
                    "invitee_id": invitee_id,
                    "room_type": room.room_type
                },
                session
            )
            return invitations
        # Check if inviter is an admin or room owner
        inviter_is_admin = await room_member_service.fetch(
            {
                "user_id": inviter_id,
                "is_admin": True,
                "room_id": room_id,
            },
            session
        )
        if not inviter_is_admin:
            raise UserNotAnAdminError(f"User {inviter_id} is not an admin in room {room_id}")
        # create invitations
        invitations = await self.create(
            {
                "room_id": room_id,
                "inviter_id": inviter_id,
                "invitee_id": invitee_id,
                "room_type": room.room_type
            },
            session
        )
        return invitations

    async def accept_room_invitations(self, invitee_id: str,
                                      room_id: str,
                                      session: AsyncSession) -> Optional[Tuple[RoomInvitation, RoomMember]]:
        """
        Accepts an invitation.

        Args:
            invitee_id(str): The id of the user accepting the room invitation.
            room_id(str): the id of the room the user is joining.
            session(object): database session object.
        Returns:
            tuple(roomInvitation, RoomMember) if the invitation exists and accepted.
        Raises:
            InvitationNotFoundError if the invitation does not exist.
        """
        # fetch the invitation
        invitation = await self.fetch(
            {
                "invitee_id": invitee_id,
                "room_id": room_id
            },
            session
        )
        if not invitation:
            raise InvitationNotFoundError(f"Invitation to room {room_id} to user {invitee_id} not found")

        # Add user to the room as a member
        new_member = await room_member_service.create(
            {
                "user_id": invitee_id,
                "room_id": room_id,
                "room_type": invitation.room_type
            },
            session
        )
        # Update the invitation status to accepted
        invitation.invitation_status = "accepted"
        await session.commit()
        return invitation, new_member

    async def rejects_room_invitations(self, invitee_id: str,
                                      room_id: str,
                                      session: AsyncSession) -> Tuple[Optional[RoomInvitation], Optional[RoomMember]]:
        """
        Rejects an invitation.

        Args:
            invitee_id(str): The id of the user accepting the room invitation.
            room_id(str): the id of the room the user is joining.
            session(object): database session object.
        Returns:
            tuple(roomInvitation, RoomMember) if the invitation exists and accepted.
        Raises:
            InvitationNotFoundError if the invitation does not exist.
        """
        # fetch the invitation
        invitation = await self.fetch(
            {
                "invitee_id": invitee_id,
                "room_id": room_id
            },
            session
        )
        if not invitation:
            raise InvitationNotFoundError(f"Invitation to room {room_id} to user {invitee_id} not found")

        # reject the invitation.
        new_member = await self.update(
            [
                {
                    "invitee_id": invitee_id,
                    "room_id": room_id,
                    "room_type": invitation.room_type
                },
                {
                    "invitation_status": "declined"
                }
            ],
            session
        )
        return invitation, new_member

room_service = RoomService()

room_member_service = RoomMemberService()

room_invitation_service = RoomInvitationService()
