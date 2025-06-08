"""
Direct Conversation Route Module
"""

import typing
from fastapi import APIRouter, status, Request, Depends, Query

from app.utils.responses import responses
from app.service.v1.direct_conversation_service import (
    direct_conversation_service,
    AsyncSession,
)
from app.dto.v1.direct_conversation_dto import AllConversationsResponseDto
from app.database.session import get_async_session
from app.core.security import validate_logout_status


direct_conversation_router = APIRouter(
    prefix="/direct-conversations", tags=["DIRECT CONVERSATIONS"]
)


@direct_conversation_router.get(
    "",
    status_code=status.HTTP_200_OK,
    responses=responses,
    response_model=AllConversationsResponseDto,
    dependencies=[Depends(validate_logout_status)],
)
async def retrieve_conversations(
    request: Request,
    session: typing.Annotated[AsyncSession, Depends(get_async_session)],
    page: int = Query(default=1, ge=1, description="The current page"),
    limit: int = Query(
        default=50, ge=1, le=50, description="The number of conversations per page"
    ),
) -> typing.Optional[AllConversationsResponseDto]:
    """
    Fetches all direct conversations.

    Return:
        Success message upon success
    Raises:
        422
        500
        409
        401
        404
    """
    return await direct_conversation_service.fetch_direct_conversations(
        page=page, session=session, request=request, limit=limit
    )
