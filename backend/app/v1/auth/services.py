from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
import httpx

from app.v1.users.services import user_service
from app.v1.profile.services import profile_service
from app.v1.users.schema import *
from app.v1.users import User
from app.v1.auth.dependencies import (
    generate_idempotency_key,
    generate_jwt_token,
    generate_access_and_refresh,
    authenticate_user,
    set_cookies
)
from app.utils.task_logger import create_logger
from app.core.config import settings, social_oauth
from app.v1.auth.schema import AccessToken


logger = create_logger("Auth Service")


class AuthService:
    """
    Authentication Class Service
    """
    async def register(
        self,
        schema: RegisterInput,
        session: AsyncSession
    ) -> Optional[RegisterOutput]:
        """
        Registers a user.

        Args:
            schema: pydantic model for user registration fields.
            session: Database session object.
        Returns:
            RegisterOutput: pydantic model with feedback for the client.
        Raises:
            HTTPExcption: If email or username already exists.
        """
        # check if client included an idempotency key
        if schema.idempotency_key:
            # fetch user by idempotency key
            idempotency_key_exists = await user_service.fetch(
                {"idempotency_key": schema.idempotency_key},
                session
            )

            # check if user was found using the provided idempotency key
            if idempotency_key_exists:
                # generate a response for the client using the new user's details
                profile = await profile_service.fetch({"user_id": idempotency_key_exists.id}, session)
                user_profile = UserProfile(
                    user=UserBase.model_validate(idempotency_key_exists, from_attributes=True),
                    profile=ProfileBase.model_validate(profile, from_attributes=True)
                )
                # return same response if user already created.
                return RegisterOutput(
                    status_code=201,
                    message="User Already Registered",
                    data=user_profile
                )
        else:
            idempotency_key = await generate_idempotency_key(schema.email, schema.username)
            user_idempotency_exists = await user_service.fetch({"idempotency_key": idempotency_key}, session)
            if user_idempotency_exists:
                # generate a response for the client using the new user's details
                profile = await profile_service.fetch({"user_id": user_idempotency_exists.id}, session)
                user_profile = UserProfile(
                    user=UserBase.model_validate(user_idempotency_exists, from_attributes=True),
                    profile=ProfileBase.model_validate(profile, from_attributes=True)
                )
                # return same response if user already created.
                return RegisterOutput(
                    status_code=201,
                    message="User Already Registered",
                    data=user_profile
                )
            else:
                schema.idempotency_key = idempotency_key
        # check if username or email is already taken by another user.
        user_email_or_username_exists = await user_service.fetch_by_email_or_user_name(
            {"email": schema.email, "username": schema.username},
            session
        )
        # if username or email already taken, notifiy the client.
        if user_email_or_username_exists:
            message = "username already exists"
            if user_email_or_username_exists.email == schema.email:
                message = "email already exists"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        # create a new user
        new_user = await user_service.create(
            schema.model_dump(),
            session
        )
        # create a new profile
        new_profile = await profile_service.create(
            {"user_id": new_user.id},
            session
        )

        # generate a response for the client using the new user's details
        user_profile = UserProfile(
            user=UserBase.model_validate(new_user, from_attributes=True),
            profile=ProfileBase.model_validate(new_profile, from_attributes=True)
        )
        return RegisterOutput(
            status_code=201,
            message="User Registered Successfully",
            data=user_profile
        )

    async def register_google(
        self,
        request: Request,
        google_response: dict,
        session: AsyncSession
    ) -> Optional[RedirectResponse]:
        """
        Creates a user from google.

        Args:
            request: request object
            session: database session object
        Returns:
            RedirectResponse: response object
        Raises:
            Exception: if Authetication fails
        """
        try:
            logger.info(msg=f"google_response: {google_response}")
            user_info: dict = google_response.get("userinfo")

            email = user_info.get("email", None)

            # check for idempotency
            idempotency_key = await generate_idempotency_key(email, email)
            user_idempotencty_exists = await user_service.fetch(
                {"idempotency_key": idempotency_key},
                session
            )
            if user_idempotencty_exists:
                access_token , refresh_token = await generate_access_and_refresh(user_idempotencty_exists.id, request)

                request.session["user_agent"] = None
                request.session["user_ip"] = None

                response = RedirectResponse(
                    url=f"{settings.frontend_url}/register?success=true&token={access_token}",
                    status_code=status.HTTP_302_FOUND,
                )
                return await set_cookies(
                    response,
                    access_token,
                    refresh_token
                )

            # check if username or email is already taken by another user.
            user_email_or_username_exists = await user_service.fetch_by_email_or_user_name(
                {"email": email, "username": email},
                session
            )
            # if username or email already taken, notifiy the client.
            if user_email_or_username_exists:
                message = "email already exists"
                return RedirectResponse(
                    url=f"{settings.frontend_url}/register?success=false&message={message}",
                    status_code=status.HTTP_302_FOUND,
                )

            last_name = (user_info.get("family_name")
                         if user_info.get("family_name")
                         else user_info.get("given_name")
                        )
            user = await user_service.create({
                "first_name": user_info.get("given_name"),
                "last_name": last_name,
                "email": email,
                "email_verified": True,
                "username": email,
                "idempotency_key": idempotency_key
            }, session)

            await user_service.create_social_login({
                "user_id": user.id,
                "provider": "google",
                "sub": user_info.get("sub"),
                "access_token": google_response.get("access_token"),
                "id_token": google_response.get("id_token", ''),
                "refresh_token": google_response.get("refresh_token", '')
            }, session)

            access_token , refresh_token = await generate_access_and_refresh(user.id, request)

            request.session["user_agent"] = None
            request.session["user_ip"] = None

            response = RedirectResponse(
                url=f"{settings.frontend_url}/register?success=true&token={access_token}",
                status_code=status.HTTP_302_FOUND,
            )

            return await set_cookies(
                response,
                access_token,
                refresh_token
            )
        except Exception as exc:
            logger.error(msg=f"error in google callback: {exc}")
            return RedirectResponse(
                url=f"{settings.frontend_url}/register?success=false&message={exc}",
                status_code=status.HTTP_302_FOUND,
            )

    async def register_github(
        self,
        request: Request,
        github_response: dict,
        session: AsyncSession
    ) -> Optional[RedirectResponse]:
        """
        Creates a user from github.

        Args:
            request: request object
            session: database session object
        Returns:
            RedirectResponse: response object
        Raises:
            Exception: if Authetication fails
        """
        try:
            logger.info(msg=f"github_response: {github_response}")
            if "access_token" not in github_response:
                raise Exception("Authetication Failed")
            if "userinfo" not in github_response:
                async with httpx.AsyncClient() as client:
                    access_token = github_response["access_token"]
                    response = await client.get(
                        url="https://api.github.com/user",
                        headers={
                            "Authorization": f"Bearer {access_token}"
                        }
                    )
                user_info: dict = response.json()
                logger.info(msg=f"user_info: {user_info}")
            else:
                user_info: dict = github_response.get("userinfo")

            email = user_info.get("email", None)
            username = user_info.get("login", None)

             # check for idempotency
            idempotency_key = await generate_idempotency_key(email, username)

            user_idempotencty_exists = await user_service.fetch(
                {"idempotency_key": idempotency_key},
                session
            )
            if user_idempotencty_exists:
                access_token , refresh_token = await generate_access_and_refresh(
                    user_idempotencty_exists.id,
                    request
                )

                request.session["user_agent"] = None
                request.session["user_ip"] = None

                response = RedirectResponse(
                    url=f"{settings.frontend_url}/register?success=true&token={access_token}",
                    status_code=status.HTTP_302_FOUND,
                )

                return await set_cookies(
                    response,
                    access_token,
                    refresh_token
                )

            # check if username or email is already taken by another user.
            user_email_or_username_exists = await user_service.fetch_by_email_or_user_name(
                {"email": email, "username": username},
                session
            )
            # if username or email already taken, notifiy the client.
            if user_email_or_username_exists:
                message = "email already exists"
                if user_email_or_username_exists.username == username:
                    message = "username already exists."
                return RedirectResponse(
                    url=f"{settings.frontend_url}/register?success=false&message={message}",
                    status_code=status.HTTP_302_FOUND,
                )

            first_name, last_name = user_info.get("name", '').split(" ")

            user = await user_service.create({
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "email_verified": True,
                "username": username,
                "idempotency_key": idempotency_key
            }, session)

            await user_service.create_social_login({
                "user_id": user.id,
                "provider": "facebook",
                "sub": user_info.get("id"),
                "access_token": github_response.get("access_token", ''),
                "id_token": github_response.get("id_token", ''),
                "refresh_token": github_response.get("refresh_token", '')
            }, session)

            access_token, refresh_token = await generate_access_and_refresh(user.id, request)

            request.session["user_agent"] = None
            request.session["user_ip"] = None

            response = RedirectResponse(
                url=f"{settings.frontend_url}/register?success=true&token={access_token}",
                status_code=status.HTTP_302_FOUND,
            )

            return await set_cookies(
                response,
                access_token,
                refresh_token
            )
        except Exception as exc:
            logger.error(msg=f"error in github callback: {exc}")
            return RedirectResponse(
                url=f"{settings.frontend_url}/register?success=false&message={exc}",
                status_code=status.HTTP_302_FOUND,
            )

    async def check_session_state(self, request: Request) -> None:
        """
        Checks if state matches in session and query params for CSRF.

        Args:
            request: request object.
        Returns:
            tuple(Any, bool): (response, false) if states do not match,
                (None, True) if states match
        """
        state_in_session = request.session.get("state")
        state_from_params = request.query_params.get("state")
        logger.info(msg=f"state_in_session: {state_in_session}, state_from_params: {state_from_params}")
        # verify the state value to prevent CRSF
        if state_from_params != state_in_session:
            message = "custom: mismatching_state: CSRF Warning! State not equal in request and response."
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

    async def openapi_authorization(
        self,
        form: dict,
        request: Request,
        session: AsyncSession) -> Dict[str, Any]:
        """Generates access_token for openapi usage.

        Args:
            form(object): A form object containing username/email and password.
            request(object): request object.
            session(object): A database session object.
        Returns:
            access_token(dict): dictionary containing the generated access_token.
        """
        user = await authenticate_user({
            "username": form.get("username"),
            "password": form.get("password")
        }, session)
        access_token = await generate_jwt_token({
            "user_id": user.id,
            "user_agent": request.headers.get("user-agent"),
            "user_ip": request.client.host
        })
        token_response = AccessToken(access_token=access_token).model_dump()
        return token_response

    async def login_user(self, schema: dict,
                         request: Request,
                         session: AsyncSession) -> Optional[JSONResponse]:
        """
        Authenticates and logs in a user.

        Args:
            schema(dict): dictionary containing username/email and password.
            request(object): The request object.
            session(object): Database async session object.
        Returns:
            response: if Authentication was successful.
        Raises:
            HttpException: If athentication fails.
        """
        authenticated_user = await authenticate_user(schema, session)
        authenticate_profile = await profile_service.fetch(
            {"user_id": authenticated_user.id},
            session
        )

        user_base = UserBase.model_validate(
            authenticated_user,
            from_attributes=True
        )

        profile_base = ProfileBase.model_validate(
            authenticate_profile,
            from_attributes=True
        )

        user_profile = UserProfile(
            user=user_base,
            profile=profile_base
        )

        login_out = LoginOut(
            status_code=200,
            data=user_profile
        )

        response = JSONResponse(
            content=jsonable_encoder(login_out.model_dump()),
            status_code=status.HTTP_200_OK
        )

        access_token, refresh_token = await generate_access_and_refresh(
            authenticated_user.id,
            request
        )

        return await set_cookies(
                    response,
                    access_token,
                    refresh_token
        )


auth_service = AuthService()
