"""
Test direct conversations module
"""

from unittest.mock import patch
import pytest
from httpx import AsyncClient

from app.tests.v1.direct_conversation import register_input, register_input_2


class TestDirectConversations:
    """
    Test direct conversations route
    """

    @pytest.mark.asyncio
    async def test_a_user_can_fetch_conversations_successfully(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests user can fetch conversations successfully
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "0gt00sdd0000-0000-0000-0000-00000001",
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

                assert data3["status_code"] == 201
                assert data3["message"] == "message sent successfully"
                assert data3["data"]["recipient_id"] == second_user_id
                assert data3["data"]["content"] == "Hello"
                conversation_id = data3["data"]["conversation_id"]

                # fetch conversations
                convo1_response = await client.get(
                    url="/api/v1/direct-conversations",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert convo1_response.status_code == 200

                convo_data: dict = convo1_response.json()

                assert convo_data["status_code"] == 200
                assert convo_data["page"] == 1
                assert convo_data["limit"] == 50
                assert convo_data["total_pages"] == 1
                assert convo_data["total_conversations"] == 1
                assert convo_data["message"] == "Conversations retrieved successfully"
                assert convo_data["data"][0]["conversation_id"] == conversation_id
                assert convo_data["data"][0]["unread_message_count"] == 1
                assert convo_data["data"][0]["firstname"] is None
                assert convo_data["data"][0]["profile_photo"] is None
                assert convo_data["data"][0]["user_id"] == second_user_id

                # send another message to second user
                message_payload["message"] = "Hello again"
                response3 = await client.post(
                    url="/api/v1/direct-messages",
                    json=message_payload,
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert response3.status_code == 201

                data4: dict = response3.json()

                assert data4["status_code"] == 201
                assert data4["message"] == "message sent successfully"
                assert data4["data"]["recipient_id"] == second_user_id
                assert data4["data"]["content"] == "Hello again"

                # fetch conversations again
                convo2_response = await client.get(
                    url="/api/v1/direct-conversations",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert convo2_response.status_code == 200

                convo_data2: dict = convo2_response.json()

                assert convo_data2["status_code"] == 200
                assert convo_data2["page"] == 1
                assert convo_data2["limit"] == 50
                assert convo_data2["total_pages"] == 1
                assert convo_data2["total_conversations"] == 1
                assert convo_data2["message"] == "Conversations retrieved successfully"
                assert convo_data2["data"][0]["conversation_id"] == conversation_id
                assert convo_data2["data"][0]["unread_message_count"] == 2
                assert convo_data2["data"][0]["firstname"] is None
                assert convo_data2["data"][0]["profile_photo"] is None
                assert convo_data2["data"][0]["user_id"] == second_user_id
