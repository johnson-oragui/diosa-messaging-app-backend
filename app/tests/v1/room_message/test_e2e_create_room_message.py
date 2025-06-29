"""
Test create room message
"""

from unittest.mock import patch
import pytest
from httpx import AsyncClient
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.v1.room_message import register_input, uuid4
from app.models.room_member import RoomMember
from app.models.room import Room
from app.models.room_message import RoomMessage
from app.models.user import User


class TestCreateRoomMessage:
    """
    Test create room message route
    """

    @pytest.mark.asyncio
    async def test_a_user_can_create_room_message_successfully(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests user can create new room message successfully
        """

        # create user
        user = User(
            email=register_input.get("email"),
            profile_photo="https://photo.com",
            email_verified=True,
        )
        await user.set_idempotency_key(register_input.get("email", ""))
        user.set_password(register_input.get("password", ""))

        # create room and add room member
        new_room = Room(owner=user, name="Greatestest room")
        new_member = RoomMember(
            member=user,
            is_admin=True,
            room=new_room,
            left_room=False,
        )

        test_get_session.add_all([user, new_room, new_member])
        await test_get_session.commit()
        await test_get_session.flush()

        # login user
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": str(uuid4()),
        }

        response = await client.post(url="/api/v1/auth/login", json=login_payload)

        assert response.status_code == 200

        data: dict = response.json()

        access_token = data["data"]["access_token"]["token"]

        # create message
        new_message_data = {
            "sender_id": user.id,
            "room_id": new_room.id,
            "message": "Hello world!",
            "media_type": "text",
        }
        message_response = await client.post(
            url="/api/v1/room-messages",
            json=new_message_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert message_response.status_code == 201

        message_data = message_response.json()

        assert message_data["data"]["sender_id"] == user.id
        assert message_data["data"]["room_id"] == new_room.id

    @pytest.mark.asyncio
    async def test_b_when_room_not_found_returns_404(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when room not found returns 404
        """

        # create user
        email = f"{uuid4()}@email.com"
        user = User(
            email=email,
            profile_photo="https://photo.com",
            email_verified=True,
        )
        await user.set_idempotency_key(email)
        user.set_password(register_input.get("password", ""))

        # create room and add room member
        new_room = Room(owner=user, name="Greatestest room")
        new_member = RoomMember(
            member=user,
            is_admin=True,
            room=new_room,
            left_room=False,
        )

        test_get_session.add_all([user, new_room, new_member])
        await test_get_session.commit()
        await test_get_session.flush()

        # login user
        login_payload = {
            "password": register_input.get("password"),
            "email": email,
            "session_id": str(uuid4()),
        }

        response = await client.post(url="/api/v1/auth/login", json=login_payload)

        assert response.status_code == 200

        data: dict = response.json()

        access_token = data["data"]["access_token"]["token"]

        # create message
        new_message_data = {
            "sender_id": user.id,
            "room_id": "12121212-1212-1212-1212-121212121212",
            "message": "Hello world!",
            "media_type": "text",
        }
        message_response = await client.post(
            url="/api/v1/room-messages",
            json=new_message_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert message_response.status_code == 404

        message_data = message_response.json()

        assert message_data["message"] == "Room not found"

    @pytest.mark.asyncio
    async def test_c_when_room_is_deactivated_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when room is deactivated returns 403
        """

        # create user
        email = f"{uuid4()}@email.com"
        user = User(
            email=email,
            profile_photo="https://photo.com",
            email_verified=True,
        )
        await user.set_idempotency_key(email)
        user.set_password(register_input.get("password", ""))

        # create room and add room member
        new_room = Room(owner=user, name="Greatestest room", is_deactivated=True)
        new_member = RoomMember(
            member=user,
            is_admin=True,
            room=new_room,
            left_room=False,
        )

        test_get_session.add_all([user, new_room, new_member])
        await test_get_session.commit()
        await test_get_session.flush()

        # login user
        login_payload = {
            "password": register_input.get("password"),
            "email": email,
            "session_id": str(uuid4()),
        }

        response = await client.post(url="/api/v1/auth/login", json=login_payload)

        assert response.status_code == 200

        data: dict = response.json()

        access_token = data["data"]["access_token"]["token"]

        # create message
        new_message_data = {
            "sender_id": user.id,
            "room_id": new_room.id,
            "message": "Hello world!",
            "media_type": "text",
        }
        message_response = await client.post(
            url="/api/v1/room-messages",
            json=new_message_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert message_response.status_code == 403

        message_data = message_response.json()

        assert message_data["message"] == "Room is deactivated"

    @pytest.mark.asyncio
    async def test_d_when_sender_is_not_room_member_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when sender is not room member returns 403
        """

        # create user
        email = f"{uuid4()}@email.com"
        user = User(
            email=email,
            profile_photo="https://photo.com",
            email_verified=True,
        )
        await user.set_idempotency_key(email)
        user.set_password(register_input.get("password", ""))

        email2 = f"{uuid4()}@email.com"
        user2 = User(
            email=email2,
            profile_photo="https://photo.com",
            email_verified=True,
        )
        await user2.set_idempotency_key(email2)
        user2.set_password(register_input.get("password", ""))

        # create room and add room member
        new_room = Room(owner=user, name="Greatestest room", is_deactivated=False)
        new_member = RoomMember(
            member=user,
            is_admin=True,
            room=new_room,
            left_room=False,
        )

        test_get_session.add_all([user, new_room, new_member, user2])
        await test_get_session.commit()
        await test_get_session.flush()

        # login user
        login_payload = {
            "password": register_input.get("password"),
            "email": user2.email,
            "session_id": str(uuid4()),
        }

        response = await client.post(url="/api/v1/auth/login", json=login_payload)

        assert response.status_code == 200

        data: dict = response.json()

        access_token = data["data"]["access_token"]["token"]

        # create message
        new_message_data = {
            "sender_id": user2.id,
            "room_id": new_room.id,
            "message": "Hello world!",
            "media_type": "text",
        }
        message_response = await client.post(
            url="/api/v1/room-messages",
            json=new_message_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert message_response.status_code == 403

        message_data = message_response.json()

        assert message_data["message"] == "User not a member"

    @pytest.mark.asyncio
    async def test_e_when_user_left_room_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when user left room returns 403
        """

        # create user
        email = f"{uuid4()}@email.com"
        user = User(
            email=email,
            profile_photo="https://photo.com",
            email_verified=True,
        )
        await user.set_idempotency_key(email)
        user.set_password(register_input.get("password", ""))

        # create room and add room member
        new_room = Room(owner=user, name="Greatestest room", is_deactivated=False)
        new_member = RoomMember(
            member=user,
            is_admin=True,
            room=new_room,
            left_room=True,
        )

        test_get_session.add_all([user, new_room, new_member])
        await test_get_session.commit()
        await test_get_session.flush()

        # login user
        login_payload = {
            "password": register_input.get("password"),
            "email": email,
            "session_id": str(uuid4()),
        }

        response = await client.post(url="/api/v1/auth/login", json=login_payload)

        assert response.status_code == 200

        data: dict = response.json()

        access_token = data["data"]["access_token"]["token"]

        # create message
        new_message_data = {
            "sender_id": user.id,
            "room_id": new_room.id,
            "message": "Hello world!",
            "media_type": "text",
        }
        message_response = await client.post(
            url="/api/v1/room-messages",
            json=new_message_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert message_response.status_code == 403

        message_data = message_response.json()

        assert message_data["message"] == "User already left room"

    @pytest.mark.asyncio
    async def test_f_when_only_room_admins_can_send_messages_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when_only_room_admins_can_send_messages_returns_403
        """

        # create user
        email = f"{uuid4()}@email.com"
        user = User(
            email=email,
            profile_photo="https://photo.com",
            email_verified=True,
        )
        await user.set_idempotency_key(email)
        user.set_password(register_input.get("password", ""))

        # create room and add room member
        new_room = Room(
            owner=user,
            name="Greatestest room",
            is_deactivated=False,
            allow_admin_messages_only=True,
        )
        new_member = RoomMember(
            member=user,
            is_admin=False,
            room=new_room,
            left_room=False,
        )

        test_get_session.add_all([user, new_room, new_member])
        await test_get_session.commit()
        await test_get_session.flush()

        # login user
        login_payload = {
            "password": register_input.get("password"),
            "email": email,
            "session_id": str(uuid4()),
        }

        response = await client.post(url="/api/v1/auth/login", json=login_payload)

        assert response.status_code == 200

        data: dict = response.json()

        access_token = data["data"]["access_token"]["token"]

        # create message
        new_message_data = {
            "sender_id": user.id,
            "room_id": new_room.id,
            "message": "Hello world!",
            "media_type": "text",
        }
        message_response = await client.post(
            url="/api/v1/room-messages",
            json=new_message_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert message_response.status_code == 403

        message_data = message_response.json()

        assert message_data["message"] == "Only Room Admins can send messages"
