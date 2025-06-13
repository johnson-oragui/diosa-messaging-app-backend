"""
Room Service Module
"""

import typing
import math

from fastapi import Request, status, HTTPException

from app.repository.v1.room_repository import room_repository, AsyncSession
from app.dto.v1.room_dto import (
    RoomBaseDto,
    CreateRoomRequestDto,
    CreateRoomResponseDto,
    RetrieveResponseDto,
)


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

    async def retrieve_rooms(
        self, request: Request, session: AsyncSession, page: int, limit: int
    ) -> typing.Union[None, RetrieveResponseDto]:
        """
        Retrieves rooms
        """
        claims: dict = request.state.claims
        current_user_id = claims.get("user_id", "")
        offset = page * limit - limit

        rooms, count = await room_repository.fetch_all(
            owner_id=current_user_id, session=session, offset=offset, limit=limit
        )

        return RetrieveResponseDto(
            data=[
                RoomBaseDto.model_validate(room, from_attributes=True)
                for room in rooms
                if room
            ],
            page=page,
            limit=limit,
            total_pages=count if count == 0 else math.ceil(count / limit),
            total_rooms=count,
        )


room_service = RoomService()
