"""
Direct Message Route Module
"""

import typing
from fastapi import APIRouter, status, Request, Depends

from app.utils.responses import responses
from app.service.v1.direct_message_service import direct_message_service, AsyncSession
from app.dto.v1.direct_message_dto import SendMessageDto, SendMessageResponseDto
from app.database.session import get_async_session
from app.core.security import validate_logout_status


direct_message_router = APIRouter(prefix="/direct-messages", tags=["DIRECT MESSAGE"])


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
        schema=schema, session=session, request=request
    )
