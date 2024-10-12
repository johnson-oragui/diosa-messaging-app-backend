"""
User Route Module
"""
from typing import Annotated, Optional
from fastapi import (
    APIRouter,
    status,
    Request,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1.users.schema import (
    UserMeOut,
)
from app.database.session import get_session
from app.utils.task_logger import create_logger
from app.v1.auth.responses_schema import responses
from app.v1.auth.dependencies import (
    check_for_access_token,
    get_current_active_user
)
from app.v1.users.services import user_service

logger = create_logger("Users Route")

users = APIRouter(prefix="/users", tags=["USERS"])

@users.get(
    "/me",
    response_model=UserMeOut,
    responses=responses,
    status_code=status.HTTP_200_OK)
async def users_me(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    access_token: Annotated[Optional[str], Depends(check_for_access_token)]
    ):
    """
    Fetches a user and user profile data.

    Args:
        access_token(str): token from cookie or Authorization

    Returns:
        UserData: Data containing all user details.
    """
    user = await get_current_active_user(
            str(access_token), request, session
        )
    return await user_service.get_user_profile(user, session)


__all__ = ["users"]
