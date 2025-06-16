"""
Test Add Room-members module
"""

from unittest.mock import patch
import pytest
from httpx import AsyncClient
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.v1.direct_message import register_input, register_input_2
from app.models.room_member import RoomMember
from app.models.room import Room


class TestAddRoomMember:
    """
    Test Add Room-Member route
    """

    @pytest.mark.asyncio
    async def test_a_user_can_add_room_member_successfully(
        self, test_setup: None, client: AsyncClient
    ):
        """
        Tests user can add new room member successfully
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00osq00sdd0asw-pll0-00s0-3432-00asq001",
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

                # add room member
                fetch_response = await client.post(
                    url=f"/api/v1/room-members/{room_id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={"is_admin": True, "member_id": second_user_id},
                )

                assert fetch_response.status_code == 201

                data: dict = fetch_response.json()

                assert data["message"] == "Room Member added succesfully"

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
                assert second_user_id in room_members

    @pytest.mark.asyncio
    async def test_b_when_user_not_a_member_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when user not a member returns 403
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00osq00sdd0asw-pll0-00s0-3432-0000q001",
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
                new_room = Room(owner_id=second_user_id, name="Great Room")
                new_member = RoomMember(
                    member_id=second_user_id, is_admin=True, room=new_room
                )
                test_get_session.add_all([new_room, new_member])
                await test_get_session.commit()

                # add room member
                fetch_response = await client.post(
                    url=f"/api/v1/room-members/{new_room.id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={"is_admin": True, "member_id": second_user_id},
                )

                assert fetch_response.status_code == 403

                data: dict = fetch_response.json()

                assert data["message"] == "User not a member"

    @pytest.mark.asyncio
    async def test_b_when_user_not_admin_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when user not admin member returns 403
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00osq00sdd0asw-pll0-00s0-3432-0011q001",
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
                new_room = Room(owner_id=second_user_id, name="Great Room")
                new_member = RoomMember(
                    member_id=second_user_id, is_admin=True, room=new_room
                )
                new_member2 = RoomMember(
                    member_id=user_id, is_admin=False, room=new_room
                )
                test_get_session.add_all([new_room, new_member, new_member2])
                await test_get_session.commit()

                # add room member
                fetch_response = await client.post(
                    url=f"/api/v1/room-members/{new_room.id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={"is_admin": True, "member_id": second_user_id},
                )

                assert fetch_response.status_code == 403

                data: dict = fetch_response.json()

                assert data["message"] == "User not an admin"

    @pytest.mark.asyncio
    async def test_b_when_user_left_room_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when user already left room returns 403
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "54osq00sdd0asw-pll0-00s0-3432-0011q001",
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
                new_room = Room(owner_id=second_user_id, name="Great Room")

                new_member2 = RoomMember(
                    member_id=user_id, is_admin=True, room=new_room, left_room=True
                )
                test_get_session.add_all([new_room, new_member2])
                await test_get_session.commit()

                # add room member
                fetch_response = await client.post(
                    url=f"/api/v1/room-members/{new_room.id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={"is_admin": True, "member_id": second_user_id},
                )

                assert fetch_response.status_code == 403

                data: dict = fetch_response.json()

                assert data["message"] == "User already left the room"

    @pytest.mark.asyncio
    async def test_b_when_user_not_authenticated_returns_401(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when user not authenticated returns 401
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "54osq00sdd0asw-pll0-00s0-3432-sa11q001",
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

                # add room member
                fetch_response = await client.post(
                    url="/api/v1/room-members/3432-4234-5435-3453",
                    json={"is_admin": True, "member_id": "3-42342-4535-35454654"},
                )

                assert fetch_response.status_code == 401

                data: dict = fetch_response.json()

                assert data["message"] == "Missing Authorization header"
