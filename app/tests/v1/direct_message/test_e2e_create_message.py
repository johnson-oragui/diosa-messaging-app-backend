"""
Test direct message module
"""

from unittest.mock import patch
import pytest
from httpx import AsyncClient

from app.tests.v1.direct_message import register_input, register_input_2


class TestCreateDirectMessage:
    """
    Test create direct message route
    """

    @pytest.mark.asyncio
    async def test_a_user_can_send_message_successfully(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests user can send message successfully
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00000sdd0000-0000-0000-0000-00000001",
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

    @pytest.mark.asyncio
    async def test_b_when_parent_message_not_exist_returns_404(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests when parent message not exist returns 404
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00000sdd0s00-0000-0000-0000-00000001",
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

                # register second user
                response = await client.post(
                    url="/api/v1/auth/register", json=register_input_2
                )
                assert response.status_code == 201
                data2: dict = response.json()

                second_user_id = data2["data"]["id"]

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

                message_payload = {
                    "parent_message_id": "12345789098-0000-0000-00000000",
                    "message": "Hello",
                    "recipient_id": second_user_id,
                }

                # send message to second user
                response = await client.post(
                    url="/api/v1/direct-messages",
                    json=message_payload,
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert response.status_code == 404

                data3: dict = response.json()

                assert data3["status_code"] == 404
                assert data3["message"] == "Parent message not found"

    @pytest.mark.asyncio
    async def test_c_when_conversation_not_exist__returns_404(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests when conversation not exist returns 404
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00000sdd0s00-0000-0000-0000-00000aa1",
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

                # register second user
                r_response = await client.post(
                    url="/api/v1/auth/register", json=register_input_2
                )
                assert r_response.status_code == 201
                r_data2: dict = r_response.json()

                second_user_id = r_data2["data"]["id"]

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

                message_payload = {
                    "conversation_id": "12345789098-0000-0000-00000212",
                    "message": "Hello",
                    "recipient_id": second_user_id,
                }

                # send message to second user
                response_2 = await client.post(
                    url="/api/v1/direct-messages",
                    json=message_payload,
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert response_2.status_code == 404

                data3: dict = response_2.json()

                assert data3["status_code"] == 404
                assert data3["message"] == "Conversation not found"

    @pytest.mark.asyncio
    async def test_d_when_current_user_send_message_to_self_returns_409(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests when current user send message to self returns 409
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "10000sdd0s00-0000-0000-0000-00000aa1",
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
                current_user_id = data["data"]["user_data"]["id"]

                message_payload = {
                    "conversation_id": "12345789098-0000-0000-00000000",
                    "message": "Hello",
                    "recipient_id": current_user_id,
                }

                # send message to second user
                response = await client.post(
                    url="/api/v1/direct-messages",
                    json=message_payload,
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert response.status_code == 409

                data3: dict = response.json()

                assert data3["status_code"] == 409
                assert data3["message"] == "Cannot send message to self"

    @pytest.mark.asyncio
    async def test_e_when_media_type_missing_returns_422(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests when media type missing returns 422
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "10000sdd0s00-0000-0000-s000-00000aa1",
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

                message_payload = {
                    "conversation_id": "12345789098-0000-0000-00000000",
                    "message": "Hello",
                    "recipient_id": "current_user_id",
                    "media_url": "https://media.com/image.png",
                }

                # send message to second user
                response = await client.post(
                    url="/api/v1/direct-messages",
                    json=message_payload,
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert response.status_code == 422

                data3: dict = response.json()

                assert data3["status_code"] == 422
                assert data3["message"] == "Validation Error."
                assert (
                    data3["data"]["msg"]
                    == "Value error, media_type must be provided when media_url is provided"
                )

    @pytest.mark.asyncio
    async def test_f_when_wrong_media_type_returns_422(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests when wrong media_type returns 422
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "10000sdd0s00-0000-0000-s000-0a000aa1",
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

                message_payload = {
                    "conversation_id": "12345789098-0000-0000-00000000",
                    "message": "Hello",
                    "recipient_id": "current_user_id",
                    "media_url": "https://media.com/image.png",
                    "media_type": "done",
                }

                # send message to second user
                response = await client.post(
                    url="/api/v1/direct-messages",
                    json=message_payload,
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert response.status_code == 422

                data3: dict = response.json()

                assert data3["status_code"] == 422
                assert data3["message"] == "Validation Error."
                assert (
                    data3["data"]["msg"]
                    == "Value error, mdeia_type must only be video, image, or text"
                )

    @pytest.mark.asyncio
    async def test_g_when_media_type_is_text_returns_422(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests when media_type is text and media_url is present returns 422
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "10000sdd0s00-0000-0000-sd00-0a000aa1",
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

                message_payload = {
                    "conversation_id": "12345789098-0000-0000-00000000",
                    "message": "Hello",
                    "recipient_id": "current_user_id",
                    "media_url": "https://media.com/image.png",
                    "media_type": "text",
                }

                # send message to second user
                response = await client.post(
                    url="/api/v1/direct-messages",
                    json=message_payload,
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert response.status_code == 422

                data3: dict = response.json()

                assert data3["status_code"] == 422
                assert data3["message"] == "Validation Error."
                assert (
                    data3["data"]["msg"]
                    == "Value error, media_type must not be text when media_url is provided"
                )
