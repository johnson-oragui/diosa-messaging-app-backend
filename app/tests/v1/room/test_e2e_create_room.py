"""
Test Create Room module
"""

from unittest.mock import patch
import pytest
from httpx import AsyncClient


from app.tests.v1.direct_message import register_input


class TestCreateRoom:
    """
    Test Create Room route
    """

    @pytest.mark.asyncio
    async def test_a_user_can_create_room_successfully(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests user can create room successfully
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00osqwosdd0000-pll0-0000-0000-00asq001",
        }

        with patch(
            "app.service.v1.authentication_service.AuthenticationService.send_email",
            return_value=None,
        ):
            with patch(
                "app.service.v1.authentication_service.AuthenticationService.generate_six_digit_code",
                return_value="123456",
            ):
                # register first user
                response = await client.post(
                    url="/api/v1/auth/register", json=register_input
                )
                assert response.status_code == 201

                # verify first user
                await client.patch(
                    url="/api/v1/auth/verify-account",
                    json={"email": register_input.get("email"), "code": "123456"},
                )

                # login first user
                response = await client.post(
                    url="/api/v1/auth/login", json=login_payload
                )

                assert response.status_code == 200

                data: dict = response.json()

                access_token = data["data"]["access_token"]["token"]
                user_id = data["data"]["user_data"]["id"]

                # create room
                response = await client.post(
                    url="/api/v1/rooms",
                    json={
                        "name": "My room",
                        "room_icon": "https://room.com",
                        "is_private": True,
                        "messages_delete_able": False,
                        "is_deactivated": False,
                        "allow_admin_messages_only": False,
                    },
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert response.status_code == 201

                data: dict = response.json()

                assert data["message"] == "Room created successfully."
                assert data["data"]["name"] == "My room"
                assert data["data"]["owner_id"] == user_id
                assert data["data"]["id"] is not None
