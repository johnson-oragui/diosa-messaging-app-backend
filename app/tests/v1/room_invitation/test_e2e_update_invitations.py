"""
Test Update Room invitations module
"""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
import pytest
from httpx import AsyncClient

# import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.v1.room_invitation import register_input, register_input_2
from app.models.room_member import RoomMember
from app.models.room import Room
from app.models.room_invitation import RoomInvitation


class TestUpdateRoomInvitation:
    """
    Test  Update Room invitations route
    """

    @pytest.mark.asyncio
    async def test_a_user_can_accept_invitation_successfully(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests user can accept invitation successfully
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
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
                user_two_id = data2["data"]["id"]

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

                user_one_access_token = data["data"]["access_token"]["token"]
                user_one_id = data["data"]["user_data"]["id"]

                # create room
                new_room = Room(name="My Dear room", owner_id=user_two_id)
                member = RoomMember(member_id=user_two_id, room=new_room, is_admin=True)
                expiration = datetime.now(timezone.utc) + timedelta(days=7)
                invitation = RoomInvitation(
                    room=new_room,
                    invitee_id=user_one_id,
                    inviter_id=user_two_id,
                    expiration=expiration,
                )
                test_get_session.add_all([new_room, member, invitation])
                await test_get_session.commit()

                # accept invitation to room
                invite_response = await client.patch(
                    url="/api/v1/room-invitations",
                    json={
                        "invitation_id": invitation.id,
                        "room_id": new_room.id,
                        "action": "accept",
                    },
                    headers={"Authorization": f"Bearer {user_one_access_token}"},
                )

                assert invite_response.status_code == 200

                invite_data: dict = invite_response.json()

                assert (
                    invite_data["message"]
                    == "Invitation request accepted successfully."
                )
                assert invite_data["data"]["invitation_status"] == "accepted"

    @pytest.mark.asyncio
    async def test_b_user_can_reject_invitation_successfully(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests user can reject invitation successfully
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
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
                user_two_id = data2["data"]["id"]

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

                user_one_access_token = data["data"]["access_token"]["token"]
                user_one_id = data["data"]["user_data"]["id"]

                # create room
                new_room = Room(name="My Dear room", owner_id=user_two_id)
                member = RoomMember(member_id=user_two_id, room=new_room, is_admin=True)
                expiration = datetime.now(timezone.utc) + timedelta(days=7)
                invitation = RoomInvitation(
                    room=new_room,
                    invitee_id=user_one_id,
                    inviter_id=user_two_id,
                    expiration=expiration,
                )
                test_get_session.add_all([new_room, member, invitation])
                await test_get_session.commit()

                # accept invitation to room
                invite_response = await client.patch(
                    url="/api/v1/room-invitations",
                    json={
                        "invitation_id": invitation.id,
                        "room_id": new_room.id,
                        "action": "decline",
                    },
                    headers={"Authorization": f"Bearer {user_one_access_token}"},
                )

                assert invite_response.status_code == 200

                invite_data: dict = invite_response.json()

                assert (
                    invite_data["message"]
                    == "Invitation request declined successfully."
                )
                assert invite_data["data"]["invitation_status"] == "declined"

    @pytest.mark.asyncio
    async def test_c_user_can_cancel_invitation_successfully(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests user can cancel invitation successfully
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
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
                user_two_id = data2["data"]["id"]

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

                user_one_access_token = data["data"]["access_token"]["token"]
                user_one_id = data["data"]["user_data"]["id"]

                # create room
                new_room = Room(name="My Dear room", owner_id=user_one_id)
                member = RoomMember(member_id=user_one_id, room=new_room, is_admin=True)
                expiration = datetime.now(timezone.utc) + timedelta(days=7)
                invitation = RoomInvitation(
                    room=new_room,
                    invitee_id=user_two_id,
                    inviter_id=user_one_id,
                    expiration=expiration,
                )
                test_get_session.add_all([new_room, member, invitation])
                await test_get_session.commit()

                # cancel invitation to room
                invite_response = await client.patch(
                    url="/api/v1/room-invitations",
                    json={
                        "invitation_id": invitation.id,
                        "room_id": new_room.id,
                        "action": "cancel",
                    },
                    headers={"Authorization": f"Bearer {user_one_access_token}"},
                )

                assert invite_response.status_code == 200

                invite_data: dict = invite_response.json()

                assert (
                    invite_data["message"]
                    == "Invitation request cancelled successfully."
                )
                assert invite_data["data"]["invitation_status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_d_when_room_not_found_returns_404(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when room not found returns 404
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
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
                user_two_id = data2["data"]["id"]

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

                user_one_access_token = data["data"]["access_token"]["token"]

                # cancel invitation to room
                invite_response = await client.patch(
                    url="/api/v1/room-invitations",
                    json={
                        "invitation_id": "31234343543546565464674",
                        "room_id": "121212121212-1212-12121-21212121",
                        "action": "cancel",
                    },
                    headers={"Authorization": f"Bearer {user_one_access_token}"},
                )

                assert invite_response.status_code == 404

                invite_data: dict = invite_response.json()

                assert invite_data["message"] == "Room not found"

    @pytest.mark.asyncio
    async def test_e_when_room_deactivated_returns_400(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when room deactivated returns 400
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
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
                user_two_id = data2["data"]["id"]

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

                user_one_access_token = data["data"]["access_token"]["token"]
                user_one_id = data["data"]["user_data"]["id"]

                # create room
                new_room = Room(
                    name="My Dear room", owner_id=user_one_id, is_deactivated=True
                )
                member = RoomMember(member_id=user_one_id, room=new_room, is_admin=True)
                expiration = datetime.now(timezone.utc) + timedelta(days=7)
                invitation = RoomInvitation(
                    room=new_room,
                    invitee_id=user_two_id,
                    inviter_id=user_one_id,
                    expiration=expiration,
                )
                test_get_session.add_all([new_room, member, invitation])
                await test_get_session.commit()

                # cancel invitation to room
                invite_response = await client.patch(
                    url="/api/v1/room-invitations",
                    json={
                        "invitation_id": invitation.id,
                        "room_id": new_room.id,
                        "action": "cancel",
                    },
                    headers={"Authorization": f"Bearer {user_one_access_token}"},
                )

                assert invite_response.status_code == 400

                invite_data: dict = invite_response.json()

                assert (
                    invite_data["message"]
                    == "Room deactivated. New Members no longer allowed"
                )

    @pytest.mark.asyncio
    async def test_f_when_invitation_not_found_returns_404(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when invitation not found returns 404
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
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
                user_two_id = data2["data"]["id"]

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

                user_one_access_token = data["data"]["access_token"]["token"]
                user_one_id = data["data"]["user_data"]["id"]

                # create room
                new_room = Room(
                    name="My Dear room", owner_id=user_one_id, is_deactivated=False
                )
                member = RoomMember(member_id=user_one_id, room=new_room, is_admin=True)
                expiration = datetime.now(timezone.utc) + timedelta(days=7)
                invitation = RoomInvitation(
                    room=new_room,
                    invitee_id=user_two_id,
                    inviter_id=user_one_id,
                    expiration=expiration,
                )
                test_get_session.add_all([new_room, member, invitation])
                await test_get_session.commit()

                # cancel invitation to room
                invite_response = await client.patch(
                    url="/api/v1/room-invitations",
                    json={
                        "invitation_id": "121212121212-1212-1212-12121212",
                        "room_id": new_room.id,
                        "action": "cancel",
                    },
                    headers={"Authorization": f"Bearer {user_one_access_token}"},
                )

                assert invite_response.status_code == 404

                invite_data: dict = invite_response.json()

                assert invite_data["message"] == "Invitation not found"

    @pytest.mark.asyncio
    async def test_g_when_current_has_no_access_to_invitation(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when current has no access to invitation returns 403
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
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
                user_two_id = data2["data"]["id"]

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

                user_one_access_token = data["data"]["access_token"]["token"]
                user_one_id = data["data"]["user_data"]["id"]

                # create room
                new_room = Room(
                    name="My Dear room", owner_id=user_two_id, is_deactivated=False
                )
                member = RoomMember(member_id=user_two_id, room=new_room, is_admin=True)
                expiration = datetime.now(timezone.utc) + timedelta(days=7)
                invitation = RoomInvitation(
                    room=new_room,
                    invitee_id=user_two_id,
                    inviter_id=user_two_id,
                    expiration=expiration,
                )
                test_get_session.add_all([new_room, member, invitation])
                await test_get_session.commit()

                # cancel invitation to room
                invite_response = await client.patch(
                    url="/api/v1/room-invitations",
                    json={
                        "invitation_id": invitation.id,
                        "room_id": new_room.id,
                        "action": "cancel",
                    },
                    headers={"Authorization": f"Bearer {user_one_access_token}"},
                )

                assert invite_response.status_code == 403

                invite_data: dict = invite_response.json()

                assert (
                    invite_data["message"]
                    == "User has not enough access to this invitation"
                )

    @pytest.mark.asyncio
    async def test_h_when_admin_already_left_room_and_cannot_cancel_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when admin already left room returns 403
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
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
                user_two_id = data2["data"]["id"]

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

                user_one_access_token = data["data"]["access_token"]["token"]
                user_one_id = data["data"]["user_data"]["id"]

                # create room
                new_room = Room(name="My Dear room", owner_id=user_one_id)
                member = RoomMember(
                    member_id=user_one_id, room=new_room, is_admin=True, left_room=True
                )
                expiration = datetime.now(timezone.utc) + timedelta(days=7)
                invitation = RoomInvitation(
                    room=new_room,
                    invitee_id=user_two_id,
                    inviter_id=user_one_id,
                    expiration=expiration,
                )
                test_get_session.add_all([new_room, member, invitation])
                await test_get_session.commit()

                # cancel invitation to room
                invite_response = await client.patch(
                    url="/api/v1/room-invitations",
                    json={
                        "invitation_id": invitation.id,
                        "room_id": new_room.id,
                        "action": "cancel",
                    },
                    headers={"Authorization": f"Bearer {user_one_access_token}"},
                )

                assert invite_response.status_code == 403

                invite_data: dict = invite_response.json()

                assert (
                    invite_data["message"]
                    == "User already left the Room.Cannot cancel invitation"
                )

    @pytest.mark.asyncio
    async def test_i_when_only_admin_can_cancel_invitation_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when only admin can cancel invitation returns 403
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
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
                user_two_id = data2["data"]["id"]

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

                user_one_access_token = data["data"]["access_token"]["token"]
                user_one_id = data["data"]["user_data"]["id"]

                # create room
                new_room = Room(
                    name="My Dear room",
                    owner_id=user_one_id,
                    allow_non_admin_invitations=False,
                )
                member = RoomMember(
                    member_id=user_one_id,
                    room=new_room,
                    is_admin=False,
                    left_room=False,
                )
                expiration = datetime.now(timezone.utc) + timedelta(days=7)
                invitation = RoomInvitation(
                    room=new_room,
                    invitee_id=user_two_id,
                    inviter_id=user_one_id,
                    expiration=expiration,
                )
                test_get_session.add_all([new_room, member, invitation])
                await test_get_session.commit()

                # cancel invitation to room
                invite_response = await client.patch(
                    url="/api/v1/room-invitations",
                    json={
                        "invitation_id": invitation.id,
                        "room_id": new_room.id,
                        "action": "cancel",
                    },
                    headers={"Authorization": f"Bearer {user_one_access_token}"},
                )

                assert invite_response.status_code == 403

                invite_data: dict = invite_response.json()

                assert invite_data["message"] == "Room only allows privileges to Admins"

    @pytest.mark.asyncio
    async def test_j_when_invitation_is_not_pending_admin_cannot_cancel_invitation_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when invitation is not pending admin cannot cancel invitation returns 403
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
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
                user_two_id = data2["data"]["id"]

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

                user_one_access_token = data["data"]["access_token"]["token"]
                user_one_id = data["data"]["user_data"]["id"]

                # create room
                new_room = Room(
                    name="My Dear room",
                    owner_id=user_one_id,
                    allow_non_admin_invitations=False,
                )
                member = RoomMember(
                    member_id=user_one_id,
                    room=new_room,
                    is_admin=True,
                    left_room=False,
                )
                expiration = datetime.now(timezone.utc) + timedelta(days=7)
                invitation = RoomInvitation(
                    room=new_room,
                    invitee_id=user_two_id,
                    inviter_id=user_one_id,
                    expiration=expiration,
                    invitation_status="accepted",
                )
                test_get_session.add_all([new_room, member, invitation])
                await test_get_session.commit()

                # cancel invitation to room
                invite_response = await client.patch(
                    url="/api/v1/room-invitations",
                    json={
                        "invitation_id": invitation.id,
                        "room_id": new_room.id,
                        "action": "cancel",
                    },
                    headers={"Authorization": f"Bearer {user_one_access_token}"},
                )

                assert invite_response.status_code == 409

                invite_data: dict = invite_response.json()

                assert (
                    invite_data["message"]
                    == "Cannot cancel request, invitation is already accepted"
                )

    @pytest.mark.asyncio
    async def test_k_when_action_is_decline_and_current_user_is_not_invitee_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when action is decline and current user is not invitee returns 403
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
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
                user_two_id = data2["data"]["id"]

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

                user_one_access_token = data["data"]["access_token"]["token"]
                user_one_id = data["data"]["user_data"]["id"]

                # create room
                new_room = Room(
                    name="My Dear room",
                    owner_id=user_one_id,
                    allow_non_admin_invitations=False,
                )
                member = RoomMember(
                    member_id=user_one_id,
                    room=new_room,
                    is_admin=True,
                    left_room=False,
                )
                expiration = datetime.now(timezone.utc) + timedelta(days=7)
                invitation = RoomInvitation(
                    room=new_room,
                    invitee_id=user_two_id,
                    inviter_id=user_one_id,
                    expiration=expiration,
                )
                test_get_session.add_all([new_room, member, invitation])
                await test_get_session.commit()

                # cancel invitation to room
                invite_response = await client.patch(
                    url="/api/v1/room-invitations",
                    json={
                        "invitation_id": invitation.id,
                        "room_id": new_room.id,
                        "action": "decline",
                    },
                    headers={"Authorization": f"Bearer {user_one_access_token}"},
                )

                assert invite_response.status_code == 403

                invite_data: dict = invite_response.json()

                assert invite_data["message"] == "Cannot decline invitation for invitee"

    @pytest.mark.asyncio
    async def test_l_when_action_is_decline_and_invitation_is_not_pending_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when action is decline and invitation is not pending returns 403
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
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
                user_two_id = data2["data"]["id"]

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

                user_one_access_token = data["data"]["access_token"]["token"]
                user_one_id = data["data"]["user_data"]["id"]

                # create room
                new_room = Room(
                    name="My Dear room",
                    owner_id=user_two_id,
                    allow_non_admin_invitations=False,
                )
                member = RoomMember(
                    member_id=user_two_id,
                    room=new_room,
                    is_admin=True,
                    left_room=False,
                )
                expiration = datetime.now(timezone.utc) + timedelta(days=7)
                invitation = RoomInvitation(
                    room=new_room,
                    invitee_id=user_one_id,
                    inviter_id=user_two_id,
                    expiration=expiration,
                    invitation_status="declined",
                )
                test_get_session.add_all([new_room, member, invitation])
                await test_get_session.commit()

                # cancel invitation to room
                invite_response = await client.patch(
                    url="/api/v1/room-invitations",
                    json={
                        "invitation_id": invitation.id,
                        "room_id": new_room.id,
                        "action": "decline",
                    },
                    headers={"Authorization": f"Bearer {user_one_access_token}"},
                )

                assert invite_response.status_code == 409

                invite_data: dict = invite_response.json()

                assert (
                    invite_data["message"]
                    == "Cannot decline invitation request, invitation is already declined"
                )

    @pytest.mark.asyncio
    async def test_m_when_action_is_accept_and_current_user_is_not_invitee_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when action is accept and current user is not invitee returns 403
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
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
                user_two_id = data2["data"]["id"]

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

                user_one_access_token = data["data"]["access_token"]["token"]
                user_one_id = data["data"]["user_data"]["id"]

                # create room
                new_room = Room(
                    name="My Dear room",
                    owner_id=user_one_id,
                    allow_non_admin_invitations=False,
                )
                member = RoomMember(
                    member_id=user_one_id,
                    room=new_room,
                    is_admin=True,
                    left_room=False,
                )
                expiration = datetime.now(timezone.utc) + timedelta(days=7)
                invitation = RoomInvitation(
                    room=new_room,
                    invitee_id=user_two_id,
                    inviter_id=user_one_id,
                    expiration=expiration,
                )
                test_get_session.add_all([new_room, member, invitation])
                await test_get_session.commit()

                # cancel invitation to room
                invite_response = await client.patch(
                    url="/api/v1/room-invitations",
                    json={
                        "invitation_id": invitation.id,
                        "room_id": new_room.id,
                        "action": "accept",
                    },
                    headers={"Authorization": f"Bearer {user_one_access_token}"},
                )

                assert invite_response.status_code == 403

                invite_data: dict = invite_response.json()

                assert invite_data["message"] == "Cannot accept invitation for invitee"

    @pytest.mark.asyncio
    async def test_n_when_action_is_accept_and_invitation_is_not_pending_returns_403(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when action is accept and invitation is not pending returns 403
        """
        login_payload = {
            "password": register_input.get("password"),
            "email": register_input.get("email"),
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
                user_two_id = data2["data"]["id"]

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

                user_one_access_token = data["data"]["access_token"]["token"]
                user_one_id = data["data"]["user_data"]["id"]

                # create room
                new_room = Room(
                    name="My Dear room",
                    owner_id=user_two_id,
                    allow_non_admin_invitations=False,
                )
                member = RoomMember(
                    member_id=user_two_id,
                    room=new_room,
                    is_admin=True,
                    left_room=False,
                )
                expiration = datetime.now(timezone.utc) + timedelta(days=7)
                invitation = RoomInvitation(
                    room=new_room,
                    invitee_id=user_one_id,
                    inviter_id=user_two_id,
                    expiration=expiration,
                    invitation_status="accepted",
                )
                test_get_session.add_all([new_room, member, invitation])
                await test_get_session.commit()

                # cancel invitation to room
                invite_response = await client.patch(
                    url="/api/v1/room-invitations",
                    json={
                        "invitation_id": invitation.id,
                        "room_id": new_room.id,
                        "action": "accept",
                    },
                    headers={"Authorization": f"Bearer {user_one_access_token}"},
                )

                assert invite_response.status_code == 409

                invite_data: dict = invite_response.json()

                assert (
                    invite_data["message"]
                    == "Cannot accept invitation request, invitation is already accepted"
                )
