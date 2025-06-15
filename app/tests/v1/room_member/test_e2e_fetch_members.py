"""
Test Fetch Room-members module
"""

from unittest.mock import patch
import pytest
from httpx import AsyncClient
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.v1.direct_message import register_input, register_input_2
from app.models.room_member import RoomMember
from app.models.room import Room


class TestFetchRoomMember:
    """
    Test Fetch Room-Members route
    """

    @pytest.mark.asyncio
    async def test_a_user_can_fetch_room_members_successfully(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests user can fetch room members successfully
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00osqwosdd0asw-pll0-00s0-3432-00asq001",
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
                room_response = await client.post(
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

                assert room_response.status_code == 201
                room_data = room_response.json()
                room_id = room_data["data"]["id"]

                # fetch room members
                fetch_response = await client.get(
                    url=f"/api/v1/room-members/{room_id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert fetch_response.status_code == 200

                data: dict = fetch_response.json()

                assert data["message"] == "Room Members fetched succesfully"
                assert len(data["data"]) > 0
                room_members = []
                for member in data["data"]:
                    room_members.append(member["member_id"])
                assert user_id in room_members

    @pytest.mark.asyncio
    async def test_b_when_user_not_part_of_room_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when user not part of room returns 403
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "090909090909-pll0-00s0-3432-00asq001",
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
                data2 = response2.json()
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
                user_id = data["data"]["user_data"]["id"]

                # create room
                new_room = Room(owner_id=second_user_id, name="Second room")
                new_member = RoomMember(
                    room=new_room, member_id=second_user_id, is_admin=True
                )
                test_get_session.add_all([new_room, new_member])
                await test_get_session.commit()

                # fetch room members
                fetch_response = await client.get(
                    url=f"/api/v1/room-members/{new_room.id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert fetch_response.status_code == 403

                data: dict = fetch_response.json()

                assert data["message"] == "User not a member"

    @pytest.mark.asyncio
    async def test_c_when_user_already_left_room_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when user already left room returns 403
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "090909090999-pll0-00s0-3432-00asq001",
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
                new_room = Room(owner_id=user_id, name="Second room")
                new_member = RoomMember(
                    room=new_room, member_id=user_id, is_admin=True, left_room=True
                )
                test_get_session.add_all([new_room, new_member])
                await test_get_session.commit()

                # fetch room members
                fetch_response = await client.get(
                    url=f"/api/v1/room-members/{new_room.id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert fetch_response.status_code == 403

                data: dict = fetch_response.json()

                assert data["message"] == "User already left the room"

    @pytest.mark.asyncio
    async def test_d_when_invalid_room_id_returns_404(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when invalid room id returns 404
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "090999090999-pll0-00s0-3432-00asq001",
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

                # fetch room members
                fetch_response = await client.get(
                    url=f"/api/v1/room-members/123-34234-34-44-435345",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert fetch_response.status_code == 404

                data: dict = fetch_response.json()

                assert data["message"] == "Room not found"
