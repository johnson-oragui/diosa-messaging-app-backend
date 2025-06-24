"""
Direct Message Route Module
"""

import typing
from fastapi import APIRouter, status, Request, Depends, Query
from redis.asyncio import Redis

from app.utils.responses import responses
from app.service.v1.direct_message_service import direct_message_service, AsyncSession
from app.dto.v1.direct_message_dto import (
    SendMessageDto,
    SendMessageResponseDto,
    AllMessagesResponseDto,
    UpdateMessageResponseDto,
    UpdateMessageDto,
    DeleteMessageDto,
    DeleteMessageResponseDto,
)
from app.database.session import get_async_session
from app.database.redis_db import get_redis_client
from app.core.security import validate_logout_status


direct_message_router = APIRouter(prefix="/direct-messages", tags=["DIRECT MESSAGES"])


@direct_message_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses=responses,
    response_model=SendMessageResponseDto,
    dependencies=[Depends(validate_logout_status)],
)
async def send_new_message(
    request: Request,
    schema: SendMessageDto,
    session: typing.Annotated[AsyncSession, Depends(get_async_session)],
    redis: typing.Annotated[Redis, Depends(get_redis_client)],
) -> typing.Optional[SendMessageResponseDto]:
    """
    Sends message to a user.

    Return:
        Success message upon success
    Raises:
        422
        500
        409
        401
        404
    """
    return await direct_message_service.send_message(
        schema=schema, session=session, request=request, redis=redis
    )


@direct_message_router.get(
    "",
    status_code=status.HTTP_200_OK,
    responses=responses,
    response_model=AllMessagesResponseDto,
    dependencies=[Depends(validate_logout_status)],
)
async def retrieve_messages(
    request: Request,
    conversation_id: str,
    session: typing.Annotated[AsyncSession, Depends(get_async_session)],
    page: int = Query(default=1, ge=1, description="The current page"),
    limit: int = Query(
        default=50, ge=1, le=50, description="The size of messages per page"
    ),
) -> typing.Optional[AllMessagesResponseDto]:
    """
    Retrieve messages of a conversation.

    Return:
        Success message upon success
    Raises:
        422
        500
        409
        401
        404
    """
    return await direct_message_service.retrieve_messages(
        page=page,
        limit=limit,
        conversation_id=conversation_id,
        session=session,
        request=request,
    )


@direct_message_router.patch(
    "",
    status_code=status.HTTP_200_OK,
    responses=responses,
    response_model=UpdateMessageResponseDto,
    dependencies=[Depends(validate_logout_status)],
)
async def update_message(
    request: Request,
    schema: UpdateMessageDto,
    session: typing.Annotated[AsyncSession, Depends(get_async_session)],
) -> typing.Optional[UpdateMessageResponseDto]:
    """
    Updates a message of a conversation.
    Update is allowed within 15 minutes of sending the message

    Return:
        Success message upon success
    Raises:
        422
        500
        409
        401
        404
    """
    return await direct_message_service.update_message(
        schema=schema,
        session=session,
        request=request,
    )


@direct_message_router.put(
    "",
    status_code=status.HTTP_200_OK,
    responses=responses,
    response_model=DeleteMessageResponseDto,
    dependencies=[Depends(validate_logout_status)],
)
async def delete_messages(
    request: Request,
    schema: DeleteMessageDto,
    session: typing.Annotated[AsyncSession, Depends(get_async_session)],
) -> typing.Optional[DeleteMessageResponseDto]:
    """
    Deletes Messages.
    Delete is allowed within 15 minutes of sending the message

    Return:
        Success message upon success
    Raises:
        422
        500
        409
        401
        404
    """
    return await direct_message_service.delete_messages(
        schema=schema,
        session=session,
        request=request,
    )
