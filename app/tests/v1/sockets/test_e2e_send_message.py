"""
Test websocket connection module
"""

from unittest.mock import patch
import json
import uuid

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from redis.asyncio import Redis

from app.tests.v1.direct_message import register_input, register_input_2
from app.models.user import User


class TestWebSocketConnection:
    """
    Test websocket connection
    """

    @pytest.mark.asyncio
    async def test_a_user_can_connect_to_socket_successfully(
        self,
        test_setup: None,
        client: AsyncClient,
        app_client: TestClient,
        test_get_session: AsyncSession,
        test_get_redis_client: Redis,
    ):
        """
        Tests user can connect to socket successfully
        """

        login_user_one_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": str(uuid.uuid4()),
        }
        login_user_two_payload = {
            "password": register_input_2.get("password"),
            "email": register_input_2.get("email"),
            "session_id": str(uuid.uuid4()),
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
                user_one_reg_response = await client.post(
                    url="/api/v1/auth/register", json=register_input
                )
                assert user_one_reg_response.status_code == 201

                # verify first user
                await client.patch(
                    url="/api/v1/auth/verify-account",
                    json={"email": register_input.get("email"), "code": "123456"},
                )

                # login first user
                user_one_login_response = await client.post(
                    url="/api/v1/auth/login", json=login_user_one_payload
                )

                assert user_one_login_response.status_code == 200

                data: dict = user_one_login_response.json()

                user_one_access_token = data["data"]["access_token"]["token"]
                user_one_id = data["data"]["user_data"]["id"]

                # register second user
                user_two_reg_response = await client.post(
                    url="/api/v1/auth/register", json=register_input_2
                )
                assert user_two_reg_response.status_code == 201
                data2: dict = user_two_reg_response.json()

                user_two_id = data2["data"]["id"]
                # verify user_two
                await test_get_session.execute(
                    sa.update(User)
                    .where(User.id == user_two_id)
                    .values(email_verified=True)
                )

                await test_get_session.commit()
                await test_get_session.flush()

                # login second user
                user_two_login_response = await client.post(
                    url="/api/v1/auth/login", json=login_user_two_payload
                )

                assert user_two_login_response.status_code == 200

                data: dict = user_two_login_response.json()

                user_two_access_token = data["data"]["access_token"]["token"]

                # send message to second user
                user_one_send_dm_response = await client.post(
                    url="/api/v1/direct-messages",
                    json={"recipient_id": user_two_id, "message": "Hello is here!"},
                    headers={"Authorization": f"Bearer {user_one_access_token}"},
                )

                assert user_one_send_dm_response.status_code == 201
                user_one_send_dm_data = user_one_send_dm_response.json()

                conversation_id = user_one_send_dm_data["data"]["conversation_id"]

                # user two connect to websocket

                with app_client.websocket_connect(
                    url=f"chats/ws?subscribe_to=dm:{conversation_id}",
                    headers={"Authorization": f"Bearer {user_two_access_token}"},
                ) as websocket:

                    # --- Verify WebSocket Connected ---
                    received = websocket.receive_text()
                    assert json.loads(received)["type"] == "presence"
                    assert user_two_id in json.loads(received)["users"]

                    message_payload = {"recipient_id": user_two_id, "message": "Hello"}

                    # send message to second user
                    user_one_send_dm_response = await client.post(
                        url="/api/v1/direct-messages",
                        json=message_payload,
                        headers={"Authorization": f"Bearer {user_one_access_token}"},
                    )

                    assert user_one_send_dm_response.status_code == 201

                    user_one_dm_data: dict = user_one_send_dm_response.json()

                    # --- Verify WebSocket Rceived messages ---
                    received = websocket.receive_json()
                    assert received["type"] == "dm"
                    assert received["from"] == user_one_id
                    assert received["to"] == user_two_id
                    assert received["conversation_id"] == conversation_id

                    assert user_one_dm_data["data"]["content"] == received["content"]
                    assert (
                        user_one_dm_data["data"]["conversation_id"]
                        == received["conversation_id"]
                    )

                    await test_get_redis_client.srem(f"user-sockets-connected:{user_two_id}", 50000)  # type: ignore
                    await test_get_redis_client.hdel("online_users", user_two_id)  # type: ignore
