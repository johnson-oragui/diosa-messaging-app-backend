"""
Room Service Module
"""

import typing

from fastapi import Request, status, HTTPException

from app.repository.v1.room_repository import room_repository, AsyncSession
from app.dto.v1.room_dto import RoomBaseDto, CreateRoomRequestDto, CreateRoomResponseDto


class RoomService:
    """
    Room Service
    """

    async def create_room(
        self, session: AsyncSession, schema: CreateRoomRequestDto, request: Request
    ) -> typing.Union[CreateRoomResponseDto, None]:
        """
        Creates a new room.

        Args:
            session (AsyncSession): The database async session object.
            shema (CreateRoomRequestDto): The request payload.
            request (Request): The request object.
        Returns:
            CreateRoomResponseDto: response payload
        """
        claims: dict = request.state.claims

        current_user_id = claims.get("user_id", "")

        new_room = await room_repository.create(
            auto_commit=True,
            session=session,
            owner_id=current_user_id,
            room_icon=str(schema.room_icon),
            allow_admin_messages_only=schema.allow_admin_messages_only,
            is_private=schema.is_private,
            messages_delete_able=schema.messages_delete_able,
            name=schema.name,
        )

        room_base = RoomBaseDto.model_validate(new_room, from_attributes=True)

        return CreateRoomResponseDto(data=room_base)


room_service = RoomService()
