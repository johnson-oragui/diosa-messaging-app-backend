from typing import Annotated
from fastapi import APIRouter, status, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1.users.schema import (
    RegisterInput,
    RegisterOutput
)
from app.database.session import get_session
from app.v1.auth.services import auth_service
from app.utils.task_logger import create_logger
from app.v1.auth.responses_schema import responses

logger = create_logger("Auth Route")

auth = APIRouter(prefix="/auth", tags=["AUTH"])

@auth.post(
    "/register",
    response_model=RegisterOutput,
    responses=responses,
    status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    schema: RegisterInput,
    session: Annotated[AsyncSession, Depends(get_session)]):
    """
    Registers a new user.
    
        Keyword arguments:
            schema -- Fields containing the user details to register
        Return: A response containing the newly created user details and success message.
        Raises: HTTPException if username or email already exists.
        Raises: Validation Error if any field is invalid.
        Raise: Internal Server Error if any other process goes wrong
    """
    return await auth_service.register(schema, session)
