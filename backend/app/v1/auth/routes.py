from typing import Annotated
from fastapi import (
    APIRouter,
    status,
    Request,
    Depends,
    HTTPException,
    Query,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import secrets

from app.v1.users.schema import (
    RegisterInput,
    RegisterOutput,
)
from app.v1.auth.schema import AccessToken
from app.database.session import get_session
from app.v1.auth.services import auth_service
from app.utils.task_logger import create_logger
from app.v1.auth.responses_schema import responses
from app.core.config import social_oauth, settings


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

@auth.get("/register/social",
          responses=responses)
async def register_user_social(request: Request,
                               provider: str = Query(
                                   examples=["google"],
                                   min_length=6,
                                   max_length=9
                                )):
    """Register Users with their social accounts.

    Args:
        provider(str): A header value stating the social account users intend to register with.

    Returns:
        Redirect(302): redirects users to on-screen consent for the specified social account.
    """
    state = secrets.token_urlsafe(16)
    if provider == "google":
        # create a callback-uri
        redirect_uri = "http://127.0.0.1:7001/api/v1/auth/callback/google"
        # set a state for csrf purpose
        request.session["state"] = state
        request.session['user_ip'] = request.client.host
        request.session["user_agent"] = request.headers.get("user-agent")
        logger.info(msg=f"session state during social oauth: {request.session.get('state')}")
        # create google oauth
        google_oauth = social_oauth.create_client("google")
        # redirect user to google
        response = await google_oauth.authorize_redirect(
            request=request,
            redirect_uri=redirect_uri,
            state=state
        )
        return response
    elif provider == "github":
        redirect_uri = "http://127.0.0.1:7001/api/v1/auth/callback/github"
        request.session["user_agent"] = request.headers.get("user-agent")
        request.session['user_ip'] = request.client.host
        request.session["state"] = state
        logger.info(msg=f"session state during social oauth: {request.session.get('state')}")
        github_oauth = social_oauth.create_client("github")
        response = await github_oauth.authorize_redirect(
            request=request,
            redirect_uri=redirect_uri,
            state=state
        )
        return response
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid provider value in the header, provider must be google or github"
        )

@auth.get("/callback/google",
          include_in_schema=False)
async def register_google_callback(request: Request, session: Annotated[AsyncSession, Depends(get_session)]):
    """
    Handles request from google after user has authenticated or
    fails to authenticate with google account.

    Args:
        request: request object
        db: database session object

    Returns:
        response: contains message, status code, tokens, and user data
                    on success or HttpException if not authenticated,
    """
    logger.info(msg=f"session state during social oauth callback: {request.session.get('state')}")
    # for testing purpose
    if not settings.test:
        # verify the state value to prevent CRSF
        await auth_service.check_session_state(request)
        # get the user access token and user_info
    google_response = await social_oauth.google.authorize_access_token(request)
    return await auth_service.register_google(request, google_response, session)

@auth.get("/callback/github",
          include_in_schema=False)
async def register_github_callback(request: Request,
                                   session: Annotated[AsyncSession, Depends(get_session)]):
    """
    Handles request from github after user has authenticated or
    fails to authenticate with google account.

    Args:
        request: request object
        db: database session object

    Returns:
        response: contains message, status code, tokens, and user data
                    on success or HttpException if not authenticated,
    """
    logger.info(msg=f"session state during social oauth callback: {request.session.get('state')}")
    # for testing purpose
    if not settings.test:
        # verify the state value to prevent CRSF
        await auth_service.check_session_state(request)
    github_oauth = social_oauth.create_client("github")
    github_response = await github_oauth.authorize_access_token(request)
    return await auth_service.register_github(request, github_response, session)

@auth.post(
    "/token",
    include_in_schema=False,
    response_model=AccessToken,
    status_code=status.HTTP_200_OK)
async def token(
    request: Request,
    form_schema: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)]):
    """
    Generates access_token for openapi.
    
        Keyword arguments:
            sform_chema -- Fields containing the user details to authenticate
        Return: A response containing the access token.
        Raises: HTTPException if username or email already exists.
        Raises: Validation Error if any field is invalid.
        Raise: Internal Server Error if any other process goes wrong
    """
    return await auth_service.openapi_authorization({
        "username": form_schema.username,
        "password": form_schema.password
    }, request, session)
