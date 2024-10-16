"""
Room Services Module
"""
from typing import Sequence, Optional, Tuple, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import aliased
import hashlib

from app.base.services import Service
from app.v1.users.services import user_service, User
from app.v1.profile import Profile
from app.v1.rooms import (
    Room,
    RoomMember,
    RoomInvitation
)
from app.core.custom_exceptions import (
    RoomNotFoundError,
    UserNotAMemberError,
    UserNotAnAdminError,
    InvitationNotFoundError,
    UserDoesNotExistError
)
from app.utils.task_logger import create_logger
from app.v1.rooms.schemas import DMBase

logger = create_logger("Room Service")


async def generate_dm_idempotency_key(user_id_1: str, user_id_2: str) -> str:
    """
    Generates an idempotency key for room_members_tables.
    The order of the id passed does not matter, the IDs are sorted and would
    always generate the hash in the same order.

    Args:
        user_id_1(str): the user id of the first user.
        user_id_2(str): the user id of the second user.
    Returns:
        hashed string.
    """
    user_ids = sorted([user_id_1, user_id_2])
    key = f"{user_ids[0]}:{user_ids[1]}"

    return hashlib.sha256(string=key.encode()).hexdigest()

async def generate_public_private_idempotency_key(creator_id: str, room_type: str, room_name: str) -> str:
    """
    Generates an idempotency key for room_members_tables on private/public rooms.

    Args:
        creator_id(str): the user id of the user creating the room.
        room_type(str): the type(private/public) of room been created.
        room_name(str): the name of the room been created.
    Returns:
        hashed string.
    """
    sorted_list = sorted([creator_id, room_type, room_name])
    key = f"{sorted_list[0]}:{sorted_list[1]}:{sorted_list[2]}"

    return hashlib.sha256(string=key.encode()).hexdigest()

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
                            messages_deletable: bool = True) -> Tuple[Optional[Room], Optional[RoomMember], Optional[str]]:
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
            return None, None, None
        idempotency_key = await generate_public_private_idempotency_key(
            creator_id=creator_id,
            room_type=room_type,
            room_name=room_name
        )
        # check if room already created.
        room_exists = await self.fetch(
            {"idempotency_key": idempotency_key},
            session
        )
        if room_exists:
            room_member = await room_member_service.fetch(
                {
                    "room_id": room_exists.id,
                    "user_id": creator_id,
                    "is_admin": True,
                    "room_type": room_exists.room_type,
                },
                session,
            )
            logger.info(msg=f"Room {room_exists.id} ({room_type}) already created by user {creator_id}.")
            return room_exists, room_member, "exists"
        new_room = await self.create(
            {
                "creator_id": creator_id,
                "room_type": room_type,
                "room_name": room_name,
                "description": description,
                "messages_deletable": messages_deletable,
                "idempotency_key": idempotency_key
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
        return new_room, room_member, None

    async def create_direct_message_room(self, user_id_1: str,
                                         user_id_2: str,
                                         session: AsyncSession) -> Tuple[Room, Sequence[RoomMember], Optional[str]]:
        """
        Create a direct-message type of room.
        Checks if a direct-message room already exists, if exists, returns the
        room and the members.

        Args:
            user_id_1(str): The user_id of the engaging user.
            user_id_2(str): The user_id of the user been enganged in a conversation.
            session(object): database session object.
        Returns:
            Room: The room created.
        Raises:
            UserDoesNotExistError if user does not exists, or if user is same with room creator.
        """
        # check if user_id_1 is same with user_id_2
        if user_id_1 == user_id_2:
            raise UserDoesNotExistError(message=f"User {user_id_1} and User {user_id_2} cannot be the same")

        # check if the user exists before creating a room
        user_exists = await user_service.fetch(
            {"id": user_id_2},
            session
        )
        if not user_exists:
            raise UserDoesNotExistError(f"User {user_id_2} does not exists")

        idempotency_key = await generate_dm_idempotency_key(
            user_id_1=user_id_1,
            user_id_2=user_id_2
        )
        room_members = await room_member_service.fetch_all(
            {"idempotency_key": idempotency_key},
            session
        )

        if room_members:
            logger.info(msg=f"members: {room_members}")
            existing_room = await room_service.fetch(
                {
                    "id": room_members[0].room_id
                },
                session=session
            )
            # Return existing DM room
            return existing_room, room_members, "exists"

        # Create new DM room if DM room does not exists
        new_dm_room = await self.create(
            {
                "creator_id": user_id_1,
                "room_type": "direct_message",
                "room_name": f"DM-{user_id_1}-and-{user_id_2}",
            },
            session
        )

        # Add both users to the room
        room_members = await room_member_service.create_all(
            [
                {
                    "user_id": user_id_1,
                    "is_admin": True,
                    "room_id": new_dm_room.id,
                    "room_type": new_dm_room.room_type,
                    "idempotency_key": idempotency_key,
                },
                {
                    "user_id": user_id_2,
                    "is_admin": True,
                    "room_id": new_dm_room.id,
                    "room_type": new_dm_room.room_type,
                    "idempotency_key": idempotency_key,
                }
            ],
            session
        )
        return new_dm_room, room_members, None

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

    async def fetch_rooms_user_belongs_to(self, user_id: str, session: AsyncSession) -> Sequence[Room]:
        """
        Retrieves all private/public rooms a user belongs to.

        Args:
            user_id(str): the id of the user.
            session(object): database session object.
        Returns:
            list of rooms a user belongs to or empty list.
        """
        stmt = select(Room).join(
            Room.room_members
        ).where(
            RoomMember.user_id == user_id,
            RoomMember.idempotency_key == None
        )

        result = await session.execute(stmt)

        return result.scalars().all()

    async def fetch_user_direct_message_rooms(self, user_id: str,
                                              session: AsyncSession) -> List[Optional[DMBase]]:
        """
        Retrieves all direct-message rooms a user has.

        Args:
            user_id (str): the id of the user.
            session (AsyncSession): database session object.
        Returns:
            list[DMBase]: A list of dictionaries containing the other user's ID, username, and avatar URL.
        """
        self_member = aliased(RoomMember, name="self_member")
        other_member = aliased(RoomMember, name="other_member")
        user = aliased(User)
        profile = aliased(Profile)
        room = aliased(Room)

        stmt = select(
            room.id,
            room.room_name,
            other_member.user_id,
            user.username,
            profile.avatar_url,
        ).select_from(
            self_member  # Explicitly setting the starting point of the query
        ).join(
            room, self_member.room_id == room.id
        ).join(
            other_member, self_member.room_id == other_member.room_id
        ).join(
            user, other_member.user_id == user.id
        ).outerjoin(
            profile, user.id == profile.user_id
        ).where(
            self_member.user_id == user_id,
            self_member.room_type == "direct_message",
            self_member.idempotency_key != None,
            other_member.user_id != user_id
        )

        result = await session.execute(stmt)
        all_rows = result.fetchall()
        direct_messages = []

        for row in all_rows:
            direct_messages.append(
                DMBase(
                    room_id=row[0],
                    room_name=row[1],
                    user_id=row[2],
                    username=row[3],
                    avatar_url=row[4]
                )
            )

        return direct_messages


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
