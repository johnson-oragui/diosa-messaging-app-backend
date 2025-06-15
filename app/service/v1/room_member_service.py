"""
Room member service module
"""

import typing
from fastapi import Request, status, HTTPException

from app.repository.v1.room_member_repository import (
    room_member_repository,
    AsyncSession,
)
from app.dto.v1.room_member_dto import RoomMebersResponseDto, RoomMemberBaseDto
from app.repository.v1.room_repository import room_repository


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


room_member_service = RoomMemberService()
