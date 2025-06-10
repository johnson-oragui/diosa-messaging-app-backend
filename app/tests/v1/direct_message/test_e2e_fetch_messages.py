"""
Test create direct message module
"""

from unittest.mock import patch
import pytest
from httpx import AsyncClient

from app.tests.v1.direct_message import register_input, register_input_2


class TestFetchDirectMessage:
    """
    Test create direct message route
    """

    @pytest.mark.asyncio
    async def test_a_user_can_fetch_messages_successfully(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests user can fetch messages successfully
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "0gt00sddws00-0000-0000-0000-00000001",
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

                # register second user
                response = await client.post(
                    url="/api/v1/auth/register", json=register_input_2
                )
                assert response.status_code == 201
                data2: dict = response.json()

                second_user_id = data2["data"]["id"]

                message_payload = {"recipient_id": second_user_id, "message": "Hello"}

                # send message to second user
                response = await client.post(
                    url="/api/v1/direct-messages",
                    json=message_payload,
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert response.status_code == 201

                data3: dict = response.json()

                conversation_id = data3["data"]["conversation_id"]

                # fetch messages
                convo1_response = await client.get(
                    url=f"/api/v1/direct-messages?conversation_id={conversation_id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert convo1_response.status_code == 200

                convo_data: dict = convo1_response.json()

                assert convo_data["status_code"] == 200
                assert convo_data["page"] == 1
                assert convo_data["limit"] == 50
                assert convo_data["total_pages"] == 1
                assert convo_data["message"] == "messages retrieved successfully"
                assert convo_data["data"][0]["conversation_id"] == conversation_id
                assert convo_data["data"][0]["is_edited"] is False
                assert convo_data["data"][0]["status"] == "sent"
                assert convo_data["data"][0]["recipient_id"] == second_user_id
