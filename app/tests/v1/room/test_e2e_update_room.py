"""
Test Update Room module
"""

from unittest.mock import patch
import pytest
from httpx import AsyncClient
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.v1.direct_message import register_input, register_input_2
from app.models.room_member import RoomMember
from app.models.room import Room


class TestUpdateRoom:
    """
    Test Update Room route
    """

    @pytest.mark.asyncio
    async def test_a_admin_can_update_room_successfully(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests user can update room successfully
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00saqwosdd0asw-pll0-0000-0000-00asq001",
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

                # create room
                create_response = await client.post(
                    url="/api/v1/rooms",
                    json={
                        "name": "My room again",
                        "room_icon": "https://room.com",
                        "is_private": True,
                        "messages_delete_able": False,
                        "is_deactivated": False,
                        "allow_admin_messages_only": False,
                    },
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert create_response.status_code == 201
                create_data = create_response.json()

                room_id = create_data["data"]["id"]

                # update room
                response = await client.patch(
                    url="/api/v1/rooms",
                    json={
                        "name": "My room",
                        "room_icon": "https://room.com/image.png",
                        "room_id": room_id,
                    },
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert response.status_code == 200

                room = (
                    await test_get_session.execute(
                        sa.select(Room).where(Room.id == room_id)
                    )
                ).scalar_one_or_none()

                assert room is not None
                assert room.name == "My room"
                assert room.room_icon == "https://room.com/image.png"
                assert room.is_deactivated is False

    @pytest.mark.asyncio
    async def test_b_when_invalid_room_id_returns_404(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when invalid room id returns 404
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00saqwosdd0asw-pll0-0000-0wsw-00asq001",
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

                # create room
                create_response = await client.post(
                    url="/api/v1/rooms",
                    json={
                        "name": "My room again",
                        "room_icon": "https://room.com",
                        "is_private": True,
                        "messages_delete_able": False,
                        "is_deactivated": False,
                        "allow_admin_messages_only": False,
                    },
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert create_response.status_code == 201
                create_data = create_response.json()

                # update room
                response = await client.patch(
                    url="/api/v1/rooms",
                    json={
                        "name": "My room",
                        "room_icon": "https://room.com/image.png",
                        "room_id": "2131243423453453453343",
                    },
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_c_user_not_member_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests user not member returns 403
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00saqwosdd0asw-pll0-0000-3232-00asq001",
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
                response2 = await client.post(
                    url="/api/v1/auth/register", json=register_input_2
                )
                assert response2.status_code == 201
                data_ = response2.json()
                second_user_id = data_["data"]["id"]

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

                # create room with second user_id
                new_room = Room(owner_id=second_user_id, name="some name")

                test_get_session.add(new_room)
                await test_get_session.commit()

                # try updating the new room
                response = await client.patch(
                    url="/api/v1/rooms",
                    json={
                        "name": "My room",
                        "room_icon": "https://room.com/image.png",
                        "room_id": new_room.id,
                    },
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert response.status_code == 403

                data5 = response.json()

                assert data5["message"] == "User is not a member of this room"

    @pytest.mark.asyncio
    async def test_d_user_not_an_admin_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests user not an admin returns 403
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00saqwosdd0asw-pll0-0000-3232-qqasq001",
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
                response0 = await client.post(
                    url="/api/v1/auth/register", json=register_input
                )
                assert response0.status_code == 201
                data0 = response0.json()

                first_user_id = data0["data"]["id"]

                # register second user
                response2 = await client.post(
                    url="/api/v1/auth/register", json=register_input_2
                )
                assert response2.status_code == 201
                data_ = response2.json()
                second_user_id = data_["data"]["id"]

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

                # create room with second user_id
                new_room = Room(owner_id=second_user_id, name="some name")

                test_get_session.add(new_room)
                await test_get_session.commit()
                # add first user to room
                room_member = RoomMember(member_id=first_user_id, room_id=new_room.id)
                test_get_session.add(room_member)
                await test_get_session.commit()

                # try updating the new room
                response = await client.patch(
                    url="/api/v1/rooms",
                    json={
                        "name": "My room",
                        "room_icon": "https://room.com/image.png",
                        "room_id": new_room.id,
                    },
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert response.status_code == 403

                data5 = response.json()

                assert data5["message"] == "User is not an admin"

    @pytest.mark.asyncio
    async def test_e_user_is_admin_and_left_room_returns_409(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests user is admin and left room returns 409
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00saqwosdd0asw-pll0-q230-3232-qqasq001",
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
                response0 = await client.post(
                    url="/api/v1/auth/register", json=register_input
                )
                assert response0.status_code == 201
                data0 = response0.json()

                first_user_id = data0["data"]["id"]

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

                # create room with second user_id
                new_room = Room(owner_id=first_user_id, name="some name")
                room_member = RoomMember(
                    member_id=first_user_id,
                    room=new_room,
                    is_admin=True,
                    left_room=True,
                )
                test_get_session.add_all([new_room, room_member])
                await test_get_session.commit()

                # try updating the new room
                response = await client.patch(
                    url="/api/v1/rooms",
                    json={
                        "name": "My room",
                        "room_icon": "https://room.com/image.png",
                        "room_id": new_room.id,
                    },
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert response.status_code == 409

                data5 = response.json()

                assert data5["message"] == "User already left the room"
