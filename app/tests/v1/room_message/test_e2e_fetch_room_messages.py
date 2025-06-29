"""
Test fetch room messages
"""

import pytest
from httpx import AsyncClient
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.v1.room_message import register_input, uuid4
from app.models.room_member import RoomMember
from app.models.room import Room
from app.models.room_message import RoomMessage
from app.models.user import User


class TestFetchRoomMessages:
    """
    Test fetch room message route
    """

    @pytest.mark.asyncio
    async def test_a_user_can_fetch_room_message_successfully(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests user can fetch new room message successfully
        """

        # create user
        email = f"{uuid4()}@gmail.com"
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
        room_message = RoomMessage(sender=user, content="I am the Man", room=new_room)

        test_get_session.add_all([user, new_room, new_member, room_message])
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

        message_response = await client.get(
            url=f"/api/v1/room-messages/{new_room.id}?order=desc",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert message_response.status_code == 200

        message_data = message_response.json()

        assert isinstance(message_data["data"], list)
        assert len(message_data["data"]) > 0

    @pytest.mark.asyncio
    async def test_b_when_room_not_found_returns_404(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when room not found returns 404
        """

        # create user
        email = f"{uuid4()}@gmail.com"
        user = User(
            email=email,
            profile_photo="https://photo.com",
            email_verified=True,
        )
        await user.set_idempotency_key(email)
        user.set_password(register_input.get("password", ""))

        test_get_session.add_all([user])
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

        message_response = await client.get(
            url="/api/v1/room-messages/13142423445435436564?order=desc",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert message_response.status_code == 404

        message_data = message_response.json()

        assert message_data["message"] == "Room not found"

    @pytest.mark.asyncio
    async def test_c_when_user_not_room_member_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when user not room member returns 403
        """

        # create user
        email = f"{uuid4()}@gmail.com"
        user = User(
            email=email,
            profile_photo="https://photo.com",
            email_verified=True,
        )
        await user.set_idempotency_key(email)
        user.set_password(register_input.get("password", ""))

        email2 = f"{uuid4()}@gmail.com"
        user2 = User(
            email=email2,
            profile_photo="https://photo.com",
            email_verified=True,
        )
        await user2.set_idempotency_key(email2)
        user2.set_password(register_input.get("password", ""))

        # create room and add room member
        new_room = Room(owner=user, name="Greatestest room")
        new_member = RoomMember(
            member=user,
            is_admin=True,
            room=new_room,
            left_room=False,
        )
        room_message = RoomMessage(sender=user, content="I am the Man", room=new_room)

        test_get_session.add_all([user, new_room, new_member, room_message, user2])
        await test_get_session.commit()
        await test_get_session.flush()

        # login user
        login_payload = {
            "password": register_input.get("password"),
            "email": email2,
            "session_id": str(uuid4()),
        }

        response = await client.post(url="/api/v1/auth/login", json=login_payload)

        assert response.status_code == 200

        data: dict = response.json()

        access_token = data["data"]["access_token"]["token"]

        message_response = await client.get(
            url=f"/api/v1/room-messages/{new_room.id}?order=desc",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert message_response.status_code == 403

        message_data = message_response.json()

        assert message_data["message"] == "User not Room member"

    @pytest.mark.asyncio
    async def test_d_when_user_left_room_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when user left room returns 403
        """

        # create user
        email = f"{uuid4()}@gmail.com"
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
            left_room=True,
        )
        room_message = RoomMessage(sender=user, content="I am the Man", room=new_room)

        test_get_session.add_all([user, new_room, new_member, room_message])
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

        message_response = await client.get(
            url=f"/api/v1/room-messages/{new_room.id}?order=desc",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert message_response.status_code == 403

        message_data = message_response.json()

        assert message_data["message"] == "User already left room"
