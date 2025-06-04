"""
Test suthentication module
"""

from unittest.mock import patch
import pytest
from httpx import AsyncClient

from app.tests.v1.auth import login_register_input


class TestAuthenticationROute:
    """
    Test authenticate route
    """

    @pytest.mark.asyncio
    async def test_a_when_email_and_password_present_return_422(
        self, client: AsyncClient
    ):
        """
        Tests authentication when username and email are present
        """
        login_payload = {
            "email": "jayson@gtest.com",
            "username": "mynameis",
            "password": "Jayson1234#",
        }

        response = await client.post(url="/api/v1/auth/login", json=login_payload)

        assert response.status_code == 422

        data: dict = response.json()

        assert data["status_code"] == 422
        assert data["message"] == "Validation Error."
        assert (
            data["data"]["msg"] == "Value error, must provide either username or email"
        )

    @pytest.mark.asyncio
    async def test_b_when_email_and_password_absent_return_422(
        self, client: AsyncClient
    ):
        """
        Tests  authentication when username and email are absent
        """
        login_payload = {
            "password": "Jayson1234#",
        }

        response = await client.post(url="/api/v1/auth/login", json=login_payload)

        assert response.status_code == 422

        data: dict = response.json()

        assert data["status_code"] == 422
        assert data["message"] == "Validation Error."
        assert (
            data["data"]["msg"] == "Value error, must provide either username or email"
        )

    @pytest.mark.asyncio
    async def test_c_when_missing_sessionid_return_422(self, client: AsyncClient):
        """
        Tests authentication user does not exist
        """
        login_payload = {
            "password": "Jayson1234#",
            "username": "nonexisting",
        }

        response = await client.post(url="/api/v1/auth/login", json=login_payload)

        assert response.status_code == 422

        data: dict = response.json()

        assert data["status_code"] == 422
        assert data["message"] == "Validation Error."
        assert data["data"]["msg"] == "Field required"

    @pytest.mark.asyncio
    async def test_d_when_user_does_not_exist_return_401(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests authentication user does not exist
        """
        login_payload = {
            "password": "Jayson1234#",
            "username": "nonexisting",
            "session_id": "000000000000-0000-0000-0000-00000000",
        }

        response = await client.post(url="/api/v1/auth/login", json=login_payload)

        assert response.status_code == 401

        data: dict = response.json()

        assert data["status_code"] == 401
        assert data["message"] == "Invalid credentials"

    @pytest.mark.asyncio
    async def test_e_user_can_login_successfully_after_registration(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests user can login successfully after registration
        """
        login_payload = {
            "password": login_register_input.get("password"),
            "email": login_register_input.get("email"),
            "session_id": "000000000000-0000-0000-0000-00000001",
        }
        with patch(
            "app.service.v1.authentication_service.AuthenticationService.send_email",
            return_value=None,
        ):
            with patch(
                "app.service.v1.authentication_service.AuthenticationService.generate_six_digit_code",
                return_value="123456",
            ):
                response = await client.post(
                    url="/api/v1/auth/register", json=login_register_input
                )
                assert response.status_code == 201

                await client.post(
                    url="/api/v1/auth/verify-account",
                    json={"email": login_register_input.get("email"), "code": "123456"},
                )

                response = await client.post(
                    url="/api/v1/auth/login", json=login_payload
                )

                assert response.status_code == 200
                assert response.headers.get("x-refresh-token") is not None

                data: dict = response.json()

                assert data["status_code"] == 200
                assert data["message"] == "Login success"
                assert data["data"]["access_token"] is not None
