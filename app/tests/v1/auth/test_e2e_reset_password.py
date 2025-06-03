"""
Reset password Test module
"""

from unittest.mock import patch
from httpx import AsyncClient
import pytest

from tests.v1.auth import password_reset_register_input


class TestResetPassword:
    """
    Test class for password reset route.
    """

    @pytest.mark.asyncio
    async def test_a_when_invalid_email_returns_404(
        self, client: AsyncClient, test_setup: None
    ):
        """
        Test when invalid email, returns 404
        """
        # register

        response = await client.post(
            url="/api/v1/auth/password-reset-init", json={"email": "fake@gmail.com"}
        )
        assert response.status_code == 404

        data = response.json()

        assert data["message"] == "Email not found"

    @pytest.mark.asyncio
    async def test_b_when_email_code_missing_returns_401(
        self, client: AsyncClient, test_setup: None
    ):
        """
        Test when email code missing, returns 401
        """
        # register

        response = await client.post(
            url="/api/v1/auth/password-reset",
            json={
                "email": "fake@gmail.com",
                "code": "123456",
                "password": "Password1234#",
                "confirm_password": "Password1234#",
            },
        )
        assert response.status_code == 401

        data = response.json()

        assert data["message"] == "code expired or invalid"

    @pytest.mark.asyncio
    async def test_c_when_passwords_do_not_match_returns_401(
        self, client: AsyncClient, test_setup: None
    ):
        """
        Test when email code missing, returns 401
        """
        # register

        response = await client.post(
            url="/api/v1/auth/password-reset",
            json={
                "email": "fake@gmail.com",
                "code": "123456",
                "password": "Password12345#",
                "confirm_password": "Password1234#",
            },
        )
        assert response.status_code == 422

        data = response.json()

        assert data["message"] == "Validation Error."

    @pytest.mark.asyncio
    async def test_d_when_valid_email_returns_200(
        self, client: AsyncClient, test_setup: None
    ):
        """
        Test when invalid email, returns 200
        """
        # register

        response = await client.post(
            url="/api/v1/auth/register", json=password_reset_register_input
        )
        assert response.status_code == 201

        with patch(
            "app.service.v1.authentication_service.AuthenticationService.generate_six_digit_code",
            return_value="12345",
        ):
            response = await client.post(
                url="/api/v1/auth/password-reset-init",
                json={"email": password_reset_register_input.get("email")},
            )
            assert response.status_code == 200

            data = response.json()

            assert data["message"] == "Reset code sent, To expire in 5 minutes"
            with patch(
                "app.service.v1.authentication_service.AuthenticationService.send_email",
                return_value=None,
            ):
                response = await client.post(
                    url="/api/v1/auth/password-reset",
                    json={
                        "email": password_reset_register_input.get("email"),
                        "code": "123456",
                        "password": "Password1234#",
                        "confirm_password": "Password1234#",
                    },
                )
                assert response.status_code == 200

                data = response.json()

                assert data["message"] == "Password reset successful"
