import pytest
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
from unittest import mock

from app.v1.auth.services import auth_service
from app.v1.users.schema import (
    RegisterOutput,
    UserProfile
)
from app.utils.task_logger import create_logger

logger = create_logger("Test Auth")

class TestAuthService:
    """
    Test class for auth_service
    """
    async def test_register_method(self,
                                 mock_register_input_johnson,
                                 test_get_session,
                                 test_setup):
        """
        Tests user creation successful
        """
        async with test_get_session as session:
            response = await auth_service.register(mock_register_input_johnson, session)

            assert response.status_code == 201
            assert isinstance(response, RegisterOutput)           
            assert response.message == "User Registered Successfully"
            assert isinstance(response.data, UserProfile)

    async def test_register_google_method(self,
                                 mock_register_input_johnson,
                                 mock_google_response,
                                 test_get_session,
                                 test_setup):
        """
        Tests user creation successful for google sign up
        """
        async with test_get_session as session:
            request = mock.AsyncMock(spec=Request)
            request.headers.get.return_value = "Fake-User_agent"
            request.client.host.return_value = "127.0.0.1"
            response = await auth_service.register_google(request, mock_google_response, session)

            assert response.status_code == 302
            assert isinstance(response, RedirectResponse)           

    # async def test_register_github_method(self,
    #                              mock_register_input_johnson,
    #                              test_get_session,
    #                              test_setup):
    #     """
    #     Tests user creation successful for github sign up
    #     """
    #     async with test_get_session as session:
    #         response = await auth_service.register_github(mock_register_input_johnson, session)

    #         assert response.status_code == 302
    #         assert isinstance(response, RegisterOutput)           
    #         assert response.message == "User Registered Successfully"
    #         assert isinstance(response.data, UserProfile)


    async def test_existing_idempotency_key(self,
                                            mock_register_input_jayson,
                                            test_get_session,
                                            test_setup):
        """
        Tests existing idempotency_key
        """
        # register user
        await auth_service.register(mock_register_input_jayson, test_get_session)
        # register user again with same idempotency_key
        response = await auth_service.register(mock_register_input_jayson, test_get_session)

        assert isinstance(response, RegisterOutput)
        assert response.status_code == 201
        assert response.message == "User Already Registered"

    async def test_email_already_exists(self,mock_register_input_johnson,
                                        test_get_session,
                                        test_setup):
        """
        Test email already exists
        """
        await auth_service.register(mock_register_input_johnson, test_get_session)
        # cretae a new user with the same email.
        new_schema = mock_register_input_johnson
        new_schema.username = "username"
        new_schema.idempotency_key = "1234567890"

        with pytest.raises(HTTPException) as exc_info:
            await auth_service.register(
                new_schema,
                test_get_session
            )
        assert str(exc_info.value) == "400: email already exists"

    @pytest.mark.asyncio
    async def test_username_already_exists(self,
                                           mock_register_input_johnson,
                                           test_get_session,
                                           test_setup):
        """
        Test username already exists
        """
        await auth_service.register(mock_register_input_johnson, test_get_session)
        new_user = mock_register_input_johnson
        new_user.email = "newuser@gmail.com"
        new_user.idempotency_key = "1234567890qq"
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.register(
                new_user,
                test_get_session
            )
        assert str(exc_info.value) == "400: username already exists"

    @pytest.mark.asyncio
    async def test_openapi_authorization(self,
                                         mock_register_input_johnson,
                                         test_get_session,
                                         test_setup):
        """
        Test openapi oauth2 authorization
        """
        await auth_service.register(mock_register_input_johnson, test_get_session)
        form_data = {
            "username": mock_register_input_johnson.username,
            "password":  mock_register_input_johnson.password
        }

        # Mock the request object
        mock_request = mock.AsyncMock(spec=Request)
        mock_request.headers.get.return_value = "Mocked-User-Agent"
        mock_request.client.host = "127.0.0.1"

        # Call the method to test
        response = await auth_service.openapi_authorization(
            form_data,
            mock_request,
            test_get_session
        )

        assert isinstance(response.get("access_token"), str)
