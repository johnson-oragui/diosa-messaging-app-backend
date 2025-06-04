"""
Test refresh token module
"""

from unittest.mock import patch
import pytest
from httpx import AsyncClient

from app.tests.v1.auth import login_register_input


class TestRefreshTokens:
    """
    Tests refresh token class
    """

    @pytest.mark.asyncio
    async def test_a_when_missing_refresh_token_header_returns_401(
        self, test_setup: None, client: AsyncClient
    ) -> None:
        """
        Tests refresh token when x-refresh-token header missing
        """
        response = await client.post(url="/api/v1/auth/refresh-tokens")

        assert response.status_code == 422

        data: dict = response.json()

        assert data["message"] == "Validation Error."
        assert data["data"]["msg"] == "Field required"

    @pytest.mark.asyncio
    async def test_b_when_refresh_token_header_uses_access_token_returns_401(
        self, test_setup: None, client: AsyncClient
    ) -> None:
        """
        Tests refresh token when x-refresh-token header missing
        """
        login_payload = {
            "password": login_register_input.get("password"),
            "email": login_register_input.get("email"),
            "session_id": "000000000000-0000-0100-0000-01010001",
        }
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
                    url="/api/v1/auth/register", json=login_register_input
                )
                assert response.status_code == 201

                await client.patch(
                    url="/api/v1/auth/verify-account",
                    json={
                        "email": login_register_input.get("email"),
                        "code": "123456",
                    },
                )

        # login
        response = await client.post(url="/api/v1/auth/login", json=login_payload)

        assert response.status_code == 200

        data: dict = response.json()

        # get access token
        access_token = data["data"]["access_token"]["token"]

        # send access token as refresh token
        response = await client.post(
            url="/api/v1/auth/refresh-tokens", headers={"X-REFRESH-TOKEN": access_token}
        )

        assert response.status_code == 401

        data: dict = response.json()

        assert data["message"] == "Invalid token type"

    @pytest.mark.asyncio
    async def test_c_full_refresh_token_flow(
        self, test_setup: None, client: AsyncClient
    ) -> None:
        """
        Tests when cannot reuse access and refresh token after refresh
        """
        login_payload = {
            "password": login_register_input.get("password"),
            "email": login_register_input.get("email"),
            "session_id": "000000000000-0000-0100-0000-01011001",
        }
        # register
        with patch(
            "app.service.v1.authentication_service.AuthenticationService.generate_six_digit_code",
            return_value="123456",
        ):
            with patch(
                "app.service.v1.authentication_service.AuthenticationService.send_email",
                return_value=None,
            ):
                response = await client.post(
                    url="/api/v1/auth/register", json=login_register_input
                )
                assert response.status_code == 201

                await client.patch(
                    url="/api/v1/auth/verify-account",
                    json={
                        "email": login_register_input.get("email"),
                        "code": "123456",
                    },
                )

                # login
                login_response = await client.post(
                    url="/api/v1/auth/login", json=login_payload
                )

                assert login_response.status_code == 200

                data: dict = login_response.json()

                # get access token
                old_access_token = data["data"]["access_token"]["token"]
                # get refresh token
                refresh_token = login_response.headers.get("x-refresh-token")

                # refresh tokens
                # should return 200
                refresh_response = await client.post(
                    url="/api/v1/auth/refresh-tokens",
                    headers={"X-REFRESH-TOKEN": refresh_token},
                )

                assert refresh_response.status_code == 200

                data: dict = refresh_response.json()

                assert data["message"] == "Tokens refresh successful"
                # get new access token
                new_access_token = data["data"]["token"]

                # get refresh token
                new_refresh_token = refresh_response.headers.get("x-refresh-token")

                # access logout route with old access token
                # should return 401
                logout_response = await client.post(
                    url="/api/v1/auth/logout",
                    headers={"Authorization": f"Bearer {old_access_token}"},
                )

                assert logout_response.status_code == 401

                data: dict = logout_response.json()

                assert data["status_code"] == 401
                assert data["message"] == "Invalid or expired session"

                # use new access token to access logout route
                # should revoke access and refresh tokens successfully
                logout2_response = await client.post(
                    url="/api/v1/auth/logout",
                    headers={"Authorization": f"Bearer {new_access_token}"},
                )

                assert logout2_response.status_code == 200

                data: dict = logout2_response.json()

                assert data["status_code"] == 200

                # refresh tokens with revoked new_refresh_token due to logout
                # should return 401
                response = await client.post(
                    url="/api/v1/auth/refresh-tokens",
                    headers={"X-REFRESH-TOKEN": new_refresh_token},
                )

                assert response.status_code == 401

                data: dict = response.json()

                assert data["message"] == "Invalid refresh token"
