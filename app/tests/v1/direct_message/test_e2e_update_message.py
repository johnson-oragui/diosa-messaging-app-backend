"""
Test update direct message module
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch
import pytest
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.v1.direct_message import register_input, register_input_2
from app.models.direct_message import DirectMessage


class TestUpdateDirectMessage:
    """
    Test update direct message route
    """

    @pytest.mark.asyncio
    async def test_a_user_can_update_message_successfully(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests user can update message successfully
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00000sdd0000-0000-0000-0000-00asq001",
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
                message_id = data3["data"]["id"]
                conversation_id = data3["data"]["conversation_id"]

                # edit message

                response_edit = await client.patch(
                    url="/api/v1/direct-messages",
                    json={
                        "message_id": message_id,
                        "message": "Not Hello",
                        "conversation_id": conversation_id,
                    },
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert response_edit.status_code == 200

                data_edit: dict = response_edit.json()

                assert data_edit["status_code"] == 200
                assert data_edit["message"] == "message updated successfully"
                assert data_edit["data"]["recipient_id"] == second_user_id
                assert data_edit["data"]["content"] == "Not Hello"
                assert data_edit["data"]["is_edited"] is True

    @pytest.mark.asyncio
    async def test_b_when_invalid_message_id_returns_404(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests when invalid message id returns 404
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00000sdd0000-0000-0000-qqq0-00asq001",
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

                # edit message

                response_edit = await client.patch(
                    url="/api/v1/direct-messages",
                    json={
                        "message_id": "message_id",
                        "message": "Not Hello",
                        "conversation_id": conversation_id,
                    },
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert response_edit.status_code == 404

                data_edit: dict = response_edit.json()

                assert data_edit["status_code"] == 404
                assert data_edit["message"] == "Invalid message id"

    @pytest.mark.asyncio
    async def test_c_when_message_more_than_15_minutes_returns_400(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when message more than 15 minutes returns 400
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00000sdd0000-ooo0-0000-a000-00asq001",
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

                new_message = DirectMessage(
                    content="Hello",
                    sender_id=user_id,
                    recipient_id=second_user_id,
                    created_at=datetime.now(timezone.utc) - timedelta(minutes=20),
                    conversation_id=conversation_id,
                )
                test_get_session.add(new_message)
                await test_get_session.commit()

                # edit message

                response_edit = await client.patch(
                    url="/api/v1/direct-messages",
                    json={
                        "message_id": new_message.id,
                        "message": "Not Hello",
                        "conversation_id": conversation_id,
                    },
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert response_edit.status_code == 400

                data_edit: dict = response_edit.json()

                assert data_edit["status_code"] == 400
                assert (
                    data_edit["message"]
                    == "Cannot update after 15 minutes of sending a message"
                )

    @pytest.mark.asyncio
    async def test_d_when_message_is_deleted_already_returns_400(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when message is deleted already returns 400
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00000sdd0000-oooo-0000-a000-00asq001",
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

                new_message = DirectMessage(
                    content="Hello",
                    sender_id=user_id,
                    is_deleted_for_sender=True,
                    recipient_id=second_user_id,
                    created_at=datetime.now(timezone.utc) - timedelta(minutes=20),
                    conversation_id=conversation_id,
                )
                test_get_session.add(new_message)
                await test_get_session.commit()

                # edit message

                response_edit = await client.patch(
                    url="/api/v1/direct-messages",
                    json={
                        "message_id": new_message.id,
                        "message": "Not Hello",
                        "conversation_id": conversation_id,
                    },
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert response_edit.status_code == 404

                data_edit: dict = response_edit.json()

                assert data_edit["status_code"] == 404
                assert data_edit["message"] == "Message not found."

    @pytest.mark.asyncio
    async def test_e_when_user_has_limited_access_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when user has limited access returns 403
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00000sdd0000-oooo-0000-a000-0oasq001",
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

                new_message = DirectMessage(
                    content="Hello",
                    sender_id=second_user_id,
                    is_deleted_for_sender=True,
                    recipient_id=user_id,
                    created_at=datetime.now(timezone.utc) - timedelta(minutes=20),
                    conversation_id=conversation_id,
                )
                test_get_session.add(new_message)
                await test_get_session.commit()

                # edit message

                response_edit = await client.patch(
                    url="/api/v1/direct-messages",
                    json={
                        "message_id": new_message.id,
                        "message": "Not Hello",
                        "conversation_id": conversation_id,
                    },
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert response_edit.status_code == 403

                data_edit: dict = response_edit.json()

                assert data_edit["status_code"] == 403
                assert data_edit["message"] == "User does not have enough access"
