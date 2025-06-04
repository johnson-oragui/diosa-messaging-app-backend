"""
Password change Test module
"""

from unittest.mock import patch
from httpx import AsyncClient
import pytest

from tests.v1.auth import password_change_register_input


class TestResendVerificationCode:
    """
    Test class for resend verification code.
    """

    @pytest.mark.asyncio
    async def test_a_successful_returns_200(
        self, client: AsyncClient, test_setup: None
    ):
        """
        Test when old and new password match
        """

        # register
        with patch(
            "app.service.v1.authentication_service.AuthenticationService.send_email",
            return_value=None,
        ):
            with patch(
                "app.service.v1.authentication_service.AuthenticationService.generate_six_digit_code",
                return_value="123456",
            ):

                response = await client.post(
                    url="/api/v1/auth/register", json=password_change_register_input
                )
                assert response.status_code == 201

                response = await client.post(
                    url="/api/v1/auth/resend-verification-code",
                    json={"email": password_change_register_input.get("email")},
                )
                assert response.status_code in [409, 200]
