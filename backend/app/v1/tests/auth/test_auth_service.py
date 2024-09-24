import pytest
from unittest import mock
from fastapi import HTTPException

from app.v1.auth.services import auth_service
from app.v1.users.schema import (
    UserBase,
    RegisterOutput
)
from app.utils.task_logger import create_logger

logger = create_logger("Test Auth")

class TestAuthService:
    """
    Test class for auth_service
    """
    @pytest.mark.asyncio
    @mock.patch("app.v1.users.services.user_service.fetch_by_idempotency_key",
                new=mock.AsyncMock(return_value=None))
    @mock.patch("app.v1.users.services.user_service.fetch_by_email_or_user_name",
                new=mock.AsyncMock(return_value=None))
    @mock.patch("app.v1.auth.dependencies.generate_idempotency_key",
                new=mock.AsyncMock(return_value="1234567890"))
    @mock.patch("app.v1.users.services.user_service.create")
    async def test_user_creation(self,
                                 mock_user_service_create,
                                 mock_session,
                                 mock_register_input_johnson,
                                 mock_register_output_johnson,
                                 mock_johnson,
                                 mock_userbase_johnson):
        """
        Tests user creation successful
        """
        mock_user_service_create.return_value = mock_johnson
        response = await auth_service.register(mock_register_input_johnson, mock_session)

        assert isinstance(response, RegisterOutput)
        assert response == mock_register_output_johnson
        assert response.status_code == 201
        assert response.message == "User Registered Successfully"
        assert isinstance(mock_userbase_johnson, UserBase)
        assert response.data == mock_userbase_johnson

    @pytest.mark.asyncio
    @mock.patch("app.v1.auth.services.auth_service.register")
    @mock.patch("app.v1.users.services.user_service.fetch_by_idempotency_key")
    async def test_existing_idempotency_key(self, mock_fetch_by_idempotency_key,
                                            mock_register,
                                            mock_session,
                                            mock_register_input_johnson,
                                            mock_userbase_johnson,
                                            mock_register_output_johnson_idempotency,
                                            mock_johnson):
        """
        Tests existing idempotency_key
        """
        mock_register.return_value = mock_register_output_johnson_idempotency

        mock_fetch_by_idempotency_key.return_value = mock_johnson

        response = await auth_service.register(mock_register_input_johnson, mock_session)

        assert isinstance(response, RegisterOutput)
        assert response == mock_register_output_johnson_idempotency
        assert response.status_code == 201
        assert response.message == "User Already Registered"
        assert isinstance(mock_userbase_johnson, UserBase)
        assert response.data == mock_userbase_johnson

    @pytest.mark.asyncio
    @mock.patch("app.v1.users.services.user_service.fetch_by_email_or_user_name")
    @mock.patch("app.database.session.get_session")
    async def test_email_already_exists(self, mock_get_session,
                                           mock_fetch_by_email_or_user_name,
                                           mock_register_input_johnson,
                                           mock_johnson):
        """
        Test email already exists
        """
        mock_get_session.execute = mock.AsyncMock()

        mock_fetch_by_email_or_user_name.return_value = mock_johnson

        with pytest.raises(HTTPException):
            await auth_service.register(
                mock_register_input_johnson,
                mock_get_session
            )

    @pytest.mark.asyncio
    @mock.patch("app.v1.users.services.user_service.fetch_by_email_or_user_name")
    @mock.patch("app.database.session.get_session")
    async def test_username_already_exists(self, mock_get_session,
                                           mock_fetch_by_email_or_user_name,
                                           mock_register_input_johnson,
                                           mock_johnson_2):
        """
        Test username already exists
        """
        mock_get_session.execute = mock.AsyncMock()

        mock_fetch_by_email_or_user_name.return_value = mock_johnson_2

        with pytest.raises(HTTPException):
            response = await auth_service.register(
                mock_register_input_johnson,
                mock_get_session
            )
