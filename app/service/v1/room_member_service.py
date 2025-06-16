"""
Room member service module
"""

import typing
from fastapi import Request, status, HTTPException
from asyncpg.exceptions import ForeignKeyViolationError

from sqlalchemy.exc import IntegrityError

from app.repository.v1.room_member_repository import (
    room_member_repository,
    AsyncSession,
)
from app.dto.v1.room_member_dto import (
    RoomMebersResponseDto,
    RoomMemberBaseDto,
    AddRoomMemberRequestDto,
    AddRoomMemberResponseDto,
)
from app.repository.v1.room_repository import room_repository
from app.utils.task_logger import create_logger

logger = create_logger(":::: RoomMemberService ::::")


class RoomMemberService:
    """
    Room member service class
    """

    async def retrieve_room_members(
        self, request: Request, session: AsyncSession, room_id: str
    ) -> typing.Union[None, RoomMebersResponseDto]:
        """
        Retrieves all room members

        Args:
            request (Request): The request object.
            session (AsyncSession): The database async session object.
            room_id (str): The room to fetch its members
        Returns:
            RoomMebersResponseDto(pydantic): Response payload
        """
        claims: dict = request.state.claims
        current_user_id = claims.get("user_id", "")

        room_exists = await room_repository.fetch(room_id=room_id, session=session)
        if not room_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
            )
        is_user_a_member = await room_member_repository.fetch(
            member_id=current_user_id, session=session, room_id=room_id
        )
        if not is_user_a_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User not a member"
            )
        if is_user_a_member.left_room:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User already left the room",
            )

        all_members = await room_member_repository.fetch_all(
            session=session, room_id=room_id
        )

        return RoomMebersResponseDto(
            data=[
                RoomMemberBaseDto.model_validate(member, from_attributes=True)
                for member in all_members
                if member
            ]
        )

    async def add_room_member(
        self,
        session: AsyncSession,
        schema: AddRoomMemberRequestDto,
        request: Request,
        room_id: str,
    ) -> typing.Union[None, AddRoomMemberResponseDto]:
        """
        Adss a new member to a room.

        Args:
            session (AsyncSession): The database async session object.
            schema (AddRoomMemberRequestDto): The request payload.
            request (Request): the request object.
            room_id (str): The id of the room.
        Returns:
            AddRoomMemberResponseDto: response payload
        """
        claims: dict = request.state.claims
        current_user_id = claims.get("user_id", "")

        if schema.member_id == current_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot add self to room",
            )

        is_user_admin = await room_member_repository.fetch(
            member_id=current_user_id, session=session, room_id=room_id
        )
        if not is_user_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not a member",
            )
        if not is_user_admin.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User not an admin"
            )
        if is_user_admin.left_room:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User already left the room",
            )

        try:
            await room_member_repository.create(
                session=session,
                room_id=room_id,
                member_id=schema.member_id,
                is_admin=schema.is_admin,
            )
        except (ForeignKeyViolationError, IntegrityError) as exc:
            logger.error("Error adding user to room: %s", str(exc))
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            ) from exc

        return AddRoomMemberResponseDto()


room_member_service = RoomMemberService()
