"""
TestAccountDeletion module
"""

from unittest.mock import patch
import pytest
from httpx import AsyncClient

from app.tests.v1.auth import delete_register_input


class TestAccountDeletion:
    """
    Test account deletion route
    """

    @pytest.mark.asyncio
    async def test_c_when_not_aunthenticated_returns_401(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests user account deletion unauthenticated
        """
        response3 = await client.post(
            url="/api/v1/auth/account-deletion",
        )

        assert response3.status_code == 401

    @pytest.mark.asyncio
    async def test_b_when_successful_account_deletion_returns_200(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests user account deletion
        """
        login_payload = {
            "password": delete_register_input.get("password"),
            "email": delete_register_input.get("email"),
            "session_id": "0000aaa00000-0000-0000-0000-00000001",
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
                    url="/api/v1/auth/register", json=delete_register_input
                )
                assert response.status_code == 201

                await client.patch(
                    url="/api/v1/auth/verify-account",
                    json={
                        "email": delete_register_input.get("email"),
                        "code": "123456",
                    },
                )

                response = await client.post(
                    url="/api/v1/auth/login", json=login_payload
                )

                assert response.status_code == 200

                data: dict = response.json()

                access_token = data["data"]["access_token"]["token"]

                response3 = await client.post(
                    url="/api/v1/auth/account-deletion",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert response3.status_code == 200

                data = response3.json()

                assert data["message"] == "Account deletion successful."

                response3 = await client.post(
                    url="/api/v1/auth/account-deletion",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert response3.status_code == 404

                data = response3.json()

                assert data["message"] == "User not found"

                response = await client.post(
                    url="/api/v1/auth/login", json=login_payload
                )

                assert response.status_code == 401
