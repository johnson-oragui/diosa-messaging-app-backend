"""
Test suthentication module
"""

from unittest.mock import patch
import pytest
from httpx import AsyncClient

from app.tests.v1.auth import login_register_input


class TestLogoutRoute:
    """
    Test logout route
    """

    @pytest.mark.asyncio
    async def test_a_when_missing_auth_header_returns_401(self, client: AsyncClient):
        """
        Tests authentication when missing auth header
        """

        response = await client.post(url="/api/v1/auth/logout")

        assert response.status_code == 401

        data: dict = response.json()

        assert data["status_code"] == 401
        assert data["message"] == "Missing Authorization header"

    @pytest.mark.asyncio
    async def test_b_when_missing_auth_beaerer_returns_401(self, client: AsyncClient):
        """
        Tests authentication when missing auth bearer
        """

        response = await client.post(
            url="/api/v1/auth/logout", headers={"Authorization": "NotBearer"}
        )

        assert response.status_code == 401

        data: dict = response.json()

        assert data["status_code"] == 401
        assert data["message"] == "Missing Authorization header"

    @pytest.mark.asyncio
    async def test_c_when_logout_success_returns_200(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests logout success
        """

        login_payload = {
            "password": login_register_input.get("password"),
            "email": login_register_input.get("email"),
            "session_id": "000000000000-0000-0000-0000-01000001",
        }
        with patch(
            "app.service.v1.authentication_service.AuthenticationService.send_email",
            return_value=None,
        ):
            response = await client.post(
                url="/api/v1/auth/register", json=login_register_input
            )
            assert response.status_code == 201

        response = await client.post(url="/api/v1/auth/login", json=login_payload)

        assert response.status_code == 200

        data: dict = response.json()

        access_token = data["data"]["access_token"]["token"]

        response = await client.post(
            url="/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data: dict = response.json()

        assert data["status_code"] == 200
        assert data["message"] == "Logout success"

    @pytest.mark.asyncio
    async def test_d_when_logout_twice_returns_401(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests logout success
        """

        login_payload = {
            "password": login_register_input.get("password"),
            "email": login_register_input.get("email"),
            "session_id": "000000000000-0000-0100-0000-01000001",
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

        response = await client.post(url="/api/v1/auth/login", json=login_payload)

        assert response.status_code == 200

        data: dict = response.json()

        access_token = data["data"]["access_token"]["token"]

        response = await client.post(
            url="/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data: dict = response.json()

        assert data["status_code"] == 200
        assert data["message"] == "Logout success"

        response = await client.post(
            url="/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 401

        data: dict = response.json()

        assert data["status_code"] == 401
        assert data["message"] == "session expired"
