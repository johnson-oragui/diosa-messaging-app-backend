"""
Test Update Room-members module
"""

from unittest.mock import patch
import pytest
from httpx import AsyncClient
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.v1.direct_message import register_input, register_input_2
from app.models.room_member import RoomMember
from app.models.room import Room


class TestUpdateRoomMember:
    """
    Test Update Room-Members route
    """

    @pytest.mark.asyncio
    async def test_a_user_can_update_room_member_successfully(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests user can update room member successfully
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00osqwosdd0asw-pll0-00s0-3432-00aswww1",
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
                new_room = Room(owner_id=user_id, name="Great room")
                new_member = RoomMember(member_id=user_id, is_admin=True, room=new_room)
                new_member2 = RoomMember(
                    member_id=second_user_id, is_admin=False, room=new_room
                )

                test_get_session.add_all([new_room, new_member, new_member2])
                await test_get_session.commit()

                # update room member
                fetch_response = await client.put(
                    url=f"/api/v1/room-members/{new_room.id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={"member_id": second_user_id, "is_admin": True},
                )

                assert fetch_response.status_code == 200

                data: dict = fetch_response.json()

                assert data["message"] == "Room Member updated succesfully"
                await test_get_session.refresh(new_member2)

                member = await test_get_session.get(
                    entity=RoomMember, ident=new_member2.id
                )
                assert member is not None

                assert member.is_admin is True

    @pytest.mark.asyncio
    async def test_b_user_not_member_returns_404(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests user not member returns 404
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00osqwosdd0asw-pll0-00s0-3432-qwaswww1",
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
                new_room = Room(owner_id=user_id, name="Great room")
                new_member = RoomMember(member_id=user_id, is_admin=True, room=new_room)

                test_get_session.add_all([new_room, new_member])
                await test_get_session.commit()

                # update room member
                fetch_response = await client.put(
                    url=f"/api/v1/room-members/{new_room.id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={"member_id": second_user_id, "is_admin": True},
                )

                assert fetch_response.status_code == 404

                data: dict = fetch_response.json()

                assert data["message"] == "Cannot update User. User is not a member"

    @pytest.mark.asyncio
    async def test_c_when_user_already_removed_returns_409(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when user already removed returns 409
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00osqwosdddesw-pll0-00s0-3432-00aswww1",
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
                new_room = Room(owner_id=user_id, name="Great room")
                new_member = RoomMember(member_id=user_id, is_admin=True, room=new_room)
                new_member2 = RoomMember(
                    member_id=second_user_id,
                    is_admin=False,
                    room=new_room,
                    left_room=True,
                )

                test_get_session.add_all([new_room, new_member, new_member2])
                await test_get_session.commit()

                # update room member
                fetch_response = await client.put(
                    url=f"/api/v1/room-members/{new_room.id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={"member_id": second_user_id, "remove_member": True},
                )

                assert fetch_response.status_code == 409

                data: dict = fetch_response.json()

                assert (
                    data["message"]
                    == "Cannot remove User. User already removed from room"
                )

    @pytest.mark.asyncio
    async def test_d_when_user_already_removed_returns_409(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when user already an admin returns 409
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00osqwosdddesw-psa0-00s0-3432-00aswww1",
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
                new_room = Room(owner_id=user_id, name="Great room")
                new_member = RoomMember(member_id=user_id, is_admin=True, room=new_room)
                new_member2 = RoomMember(
                    member_id=second_user_id,
                    is_admin=True,
                    room=new_room,
                )

                test_get_session.add_all([new_room, new_member, new_member2])
                await test_get_session.commit()

                # update room member
                fetch_response = await client.put(
                    url=f"/api/v1/room-members/{new_room.id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={"member_id": second_user_id, "is_admin": True},
                )

                assert fetch_response.status_code == 409

                data: dict = fetch_response.json()

                assert data["message"] == "User already an admin"

    @pytest.mark.asyncio
    async def test_e_when_current_user_not_admin_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when user already an admin returns 409
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00osqwosddazsw-psa0-00s0-3432-00aswww1",
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
                new_room = Room(owner_id=user_id, name="Great room")
                new_member = RoomMember(
                    member_id=user_id, is_admin=False, room=new_room
                )
                new_member2 = RoomMember(
                    member_id=second_user_id,
                    is_admin=False,
                    room=new_room,
                )

                test_get_session.add_all([new_room, new_member, new_member2])
                await test_get_session.commit()

                # update room member
                fetch_response = await client.put(
                    url=f"/api/v1/room-members/{new_room.id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={"member_id": second_user_id, "is_admin": True},
                )

                assert fetch_response.status_code == 403

                data: dict = fetch_response.json()

                assert (
                    data["message"]
                    == "Oops! You have not enough access to perform this action"
                )

    @pytest.mark.asyncio
    async def test_f_when_current_user_left_room_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when user already left room returns 403
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
            "session_id": "00osqwosddazsw-psa0-qps0-3432-00aswww1",
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
                new_room = Room(owner_id=user_id, name="Great room")
                new_member = RoomMember(
                    member_id=user_id,
                    is_admin=True,
                    room=new_room,
                    left_room=True,
                )
                new_member2 = RoomMember(
                    member_id=second_user_id,
                    is_admin=False,
                    room=new_room,
                )

                test_get_session.add_all([new_room, new_member, new_member2])
                await test_get_session.commit()

                # update room member
                fetch_response = await client.put(
                    url=f"/api/v1/room-members/{new_room.id}",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={"member_id": second_user_id, "is_admin": True},
                )

                assert fetch_response.status_code == 403

                data: dict = fetch_response.json()

                assert data["message"] == "Oops! You already left the room"
