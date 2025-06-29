"""
Test delete room messages
"""

from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.v1.room_message import register_input, uuid4
from app.models.room_member import RoomMember
from app.models.room import Room
from app.models.room_message import RoomMessage
from app.models.user import User


class TestDeleteRoomMessages:
    """
    Test delete room message route
    """

    @pytest.mark.asyncio
    async def test_a_user_can_delete_room_message_successfully(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests user can delete new room message successfully
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
        new_room = Room(owner=user, name="Greatestest room", messages_delete_able=True)
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

        # delete room message

        message_response = await client.put(
            url=f"/api/v1/room-messages/{new_room.id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"message_ids": [room_message.id]},
        )

        assert message_response.status_code == 200

        message_data = message_response.json()

        assert message_data["message"] == "message(s) deleted successfully"

        await test_get_session.refresh(room_message)

        assert room_message.is_deleted is True

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

        message_response = await client.put(
            url="/api/v1/room-messages/13142423445435436564",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "message_ids": ["12321-3423-54354-55654"],
            },
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
        new_room = Room(owner=user, name="Greatestest room", messages_delete_able=True)
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

        message_response = await client.put(
            url=f"/api/v1/room-messages/{new_room.id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"message_ids": [room_message.id]},
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
        new_room = Room(owner=user, name="Greatestest room", messages_delete_able=True)
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

        message_response = await client.put(
            url=f"/api/v1/room-messages/{new_room.id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"message_ids": [room_message.id]},
        )

        assert message_response.status_code == 403

        message_data = message_response.json()

        assert message_data["message"] == "User already left room"

    @pytest.mark.asyncio
    async def test_e_when_message_not_found_returns_404(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when message not found returns 404
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
        new_room = Room(owner=user, name="Greatestest room", messages_delete_able=True)
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

        # delete room message

        message_response = await client.put(
            url=f"/api/v1/room-messages/{new_room.id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "message_ids": ["fake-message_id-eeeqq2133"],
            },
        )

        assert message_response.status_code == 404

        message_data = message_response.json()

        assert (
            message_data["message"]
            == "Message with id fake-message_id-eeeqq2133 not found"
        )

    @pytest.mark.asyncio
    async def test_f_when_message_is_already_deleted_returns_404(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when message is already deleted returns 404
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
        new_room = Room(owner=user, name="Greatestest room", messages_delete_able=True)
        new_member = RoomMember(
            member=user,
            is_admin=True,
            room=new_room,
            left_room=False,
        )
        room_message = RoomMessage(
            sender=user, content="I am the Man", room=new_room, is_deleted=True
        )

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

        # delete room message

        message_response = await client.put(
            url=f"/api/v1/room-messages/{new_room.id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"message_ids": [room_message.id]},
        )

        assert message_response.status_code == 404

        message_data = message_response.json()

        assert (
            message_data["message"]
            == f"Message with id {room_message.id} was not found"
        )

    @pytest.mark.asyncio
    async def test_g_when_user_deletes_another_user_message_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when user deletes another user message returns 403
        """

        # create user1
        email = f"{uuid4()}@gmail.com"
        user = User(
            email=email,
            profile_photo="https://photo.com",
            email_verified=True,
        )
        await user.set_idempotency_key(email)
        user.set_password(register_input.get("password", ""))
        # create user2
        email2 = f"{uuid4()}@gmail.com"
        user2 = User(
            email=email2,
            profile_photo="https://photo.com",
            email_verified=True,
        )
        await user2.set_idempotency_key(email2)
        user2.set_password(register_input.get("password", ""))

        # create room and add room member
        new_room = Room(owner=user, name="Greatestest room", messages_delete_able=True)
        new_member = RoomMember(
            member=user,
            is_admin=False,
            room=new_room,
            left_room=False,
        )
        new_member2 = RoomMember(
            member=user2,
            is_admin=False,
            room=new_room,
            left_room=False,
        )
        room_message = RoomMessage(sender=user, content="I am the Man", room=new_room)

        test_get_session.add_all(
            [user, new_room, new_member, room_message, user2, new_member2]
        )
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

        # delete room message

        message_response = await client.put(
            url=f"/api/v1/room-messages/{new_room.id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"message_ids": [room_message.id]},
        )

        assert message_response.status_code == 403

        message_data = message_response.json()

        assert message_data["message"] == "User has not enough Privilege"

    @pytest.mark.asyncio
    async def test_h_when_updating_message_passed_15_minutes_returns_400(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when updating message passed 15 minutes returns 400
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
        new_room = Room(owner=user, name="Greatestest room", messages_delete_able=True)
        new_member = RoomMember(
            member=user,
            is_admin=True,
            room=new_room,
            left_room=False,
        )
        room_message = RoomMessage(
            sender=user,
            content="I am the Man",
            room=new_room,
            created_at=datetime.now(timezone.utc) - timedelta(minutes=20),
        )

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

        # delete room message

        message_response = await client.put(
            url=f"/api/v1/room-messages/{new_room.id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"message_ids": [room_message.id]},
        )

        assert message_response.status_code == 400

        message_data = message_response.json()

        assert (
            message_data["message"]
            == "Cannot delete after 15 minutes of sending a message"
        )

    @pytest.mark.asyncio
    async def test_j_when_messages_delete_able_is_False_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when messages delete able is False returns 403
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
        new_room = Room(owner=user, name="Greatestest room", messages_delete_able=False)
        new_member = RoomMember(
            member=user,
            is_admin=False,
            room=new_room,
            left_room=False,
        )
        room_message = RoomMessage(
            sender=user,
            content="I am the Man",
            room=new_room,
            created_at=datetime.now(timezone.utc) - timedelta(minutes=20),
        )

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

        # delete room message

        message_response = await client.put(
            url=f"/api/v1/room-messages/{new_room.id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"message_ids": [room_message.id]},
        )

        assert message_response.status_code == 403

        message_data = message_response.json()

        assert (
            message_data["message"] == "Admin privilege is needed for message deletion."
        )

    @pytest.mark.asyncio
    async def test_k_when_is_admin_can_delete_any_message_successfully(
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
        new_room = Room(
            owner=user,
            name="Greatestest room",
            messages_delete_able=False,
            is_deactivated=True,
        )
        new_member = RoomMember(
            member=user,
            is_admin=False,
            room=new_room,
            left_room=False,
        )
        new_member2 = RoomMember(
            member=user2,
            is_admin=True,
            room=new_room,
            left_room=False,
        )
        room_message = RoomMessage(sender=user, content="I am the Man", room=new_room)

        test_get_session.add_all(
            [user, new_room, new_member, room_message, user2, new_member2]
        )
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

        message_response = await client.put(
            url=f"/api/v1/room-messages/{new_room.id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"message_ids": [room_message.id]},
        )

        assert message_response.status_code == 200
