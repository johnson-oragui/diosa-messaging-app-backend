"""
Room Route Module
"""

import typing
from fastapi import APIRouter, status, Request, Depends, Query

from app.utils.responses import responses
from app.service.v1.room_service import room_service, AsyncSession
from app.dto.v1.room_dto import (
    CreateRoomRequestDto,
    CreateRoomResponseDto,
    RetrieveResponseDto,
)
from app.core.security import validate_logout_status
from app.database.session import get_async_session

rooms_router = APIRouter(prefix="/rooms", tags=["ROOMS"])


@rooms_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses=responses,
    response_model=CreateRoomResponseDto,
    dependencies=[Depends(validate_logout_status)],
)
async def create_new_room(
    request: Request,
    schema: CreateRoomRequestDto,
    session: typing.Annotated[AsyncSession, Depends(get_async_session)],
) -> typing.Optional[CreateRoomResponseDto]:
    """
    Creates a new room.

    Return:
        Success message upon success
    Raises:
        422
        500
        409
        401
        404
    """
    return await room_service.create_room(
        schema=schema, request=request, session=session
    )


@rooms_router.get(
    "",
    status_code=status.HTTP_200_OK,
    responses=responses,
    response_model=RetrieveResponseDto,
    dependencies=[Depends(validate_logout_status)],
)
async def retrieve_rooms(
    request: Request,
    session: typing.Annotated[AsyncSession, Depends(get_async_session)],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=50),
) -> typing.Optional[RetrieveResponseDto]:
    """
    Retrieves all rooms.

    Return:
        Success message upon success
    Raises:
        422
        500
        409
        401
        404
    """
    return await room_service.retrieve_rooms(
        page=page, limit=limit, request=request, session=session
    )
