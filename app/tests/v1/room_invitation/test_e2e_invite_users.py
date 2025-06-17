"""
Test Invite Users to Room module
"""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
import pytest
from httpx import AsyncClient
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.v1.room_invitation import register_input, register_input_2
from app.models.room_member import RoomMember
from app.models.room import Room
from app.models.room_invitation import RoomInvitation


class TestCreateRoomInvitation:
    """
    Test Invite Users to Room route
    """

    @pytest.mark.asyncio
    async def test_a_user_can_invite_users_successfully(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests user can invite users successfully
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
                new_room = Room(name="My Dear room", owner_id=user_id)
                member = RoomMember(member_id=user_id, room=new_room, is_admin=True)
                test_get_session.add_all([new_room, member])
                await test_get_session.commit()

                # invite to room
                invite_response = await client.post(
                    url="/api/v1/room-invitations",
                    json={"invitee_id": second_user_id, "room_id": new_room.id},
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert invite_response.status_code == 201

                invite_data: dict = invite_response.json()

                assert invite_data["message"] == "Invitation sent successfully"
                assert invite_data["data"]["invitee_id"] == second_user_id

    @pytest.mark.asyncio
    async def test_b_when_self_invitation_returns_400(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when self invitation returns 400
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
                new_room = Room(name="My Dear room", owner_id=user_id)
                member = RoomMember(member_id=user_id, room=new_room, is_admin=True)
                test_get_session.add_all([new_room, member])
                await test_get_session.commit()

                # invite to room
                invite_response = await client.post(
                    url="/api/v1/room-invitations",
                    json={"invitee_id": user_id, "room_id": new_room.id},
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert invite_response.status_code == 400

                invite_data: dict = invite_response.json()

                assert invite_data["message"] == "Cannot invite self to room"

    @pytest.mark.asyncio
    async def test_c_when_room_does_not_exist_returns_404(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when Room does not exist. returns 400
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
                new_room = Room(name="My Dear room", owner_id=user_id)
                member = RoomMember(member_id=user_id, room=new_room, is_admin=True)
                test_get_session.add_all([new_room, member])
                await test_get_session.commit()

                # invite to room
                invite_response = await client.post(
                    url="/api/v1/room-invitations",
                    json={
                        "invitee_id": second_user_id,
                        "room_id": "3094329483289539430239",
                    },
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert invite_response.status_code == 404

                invite_data: dict = invite_response.json()

                assert invite_data["message"] == "Room does not exist."

    @pytest.mark.asyncio
    async def test_d_when_user_not_member_returns_404(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when current user is not room member returns 400
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
                new_room = Room(name="My Dear room", owner_id=second_user_id)
                member = RoomMember(
                    member_id=second_user_id, room=new_room, is_admin=True
                )
                test_get_session.add_all([new_room, member])
                await test_get_session.commit()

                # invite to room
                invite_response = await client.post(
                    url="/api/v1/room-invitations",
                    json={"invitee_id": second_user_id, "room_id": new_room.id},
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert invite_response.status_code == 404

                invite_data: dict = invite_response.json()

                assert invite_data["message"] == "User not part of the Room."

    @pytest.mark.asyncio
    async def test_e_when_room_is_admin_invitations_only_returns_404(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when user is not admin and room allows invitation by admins only returns 400
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
                new_room = Room(
                    name="My Dear room",
                    owner_id=user_id,
                    allow_non_admin_invitations=False,
                )
                member = RoomMember(member_id=user_id, room=new_room, is_admin=False)
                test_get_session.add_all([new_room, member])
                await test_get_session.commit()

                # invite to room
                invite_response = await client.post(
                    url="/api/v1/room-invitations",
                    json={"invitee_id": second_user_id, "room_id": new_room.id},
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert invite_response.status_code == 403

                invite_data: dict = invite_response.json()

                assert invite_data["message"] == "Invitation only alowed for Admins"

    @pytest.mark.asyncio
    async def test_f_when_invited_user_already_member_returns_409(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when invited user already member returns 409
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
                new_room = Room(
                    name="My Dear room",
                    owner_id=user_id,
                    allow_non_admin_invitations=False,
                )
                member = RoomMember(member_id=user_id, room=new_room, is_admin=True)
                member2 = RoomMember(
                    member_id=second_user_id, room=new_room, is_admin=False
                )
                test_get_session.add_all([new_room, member, member2])
                await test_get_session.commit()

                # invite to room
                invite_response = await client.post(
                    url="/api/v1/room-invitations",
                    json={"invitee_id": second_user_id, "room_id": new_room.id},
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert invite_response.status_code == 409

                invite_data: dict = invite_response.json()

                assert invite_data["message"] == "Invited User is already a member"

    @pytest.mark.asyncio
    async def test_g_when_invited_user_already_left_room_returns_201(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when invited user already left room returns 201
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
                new_room = Room(
                    name="My Dear room",
                    owner_id=user_id,
                    allow_non_admin_invitations=False,
                )
                member = RoomMember(member_id=user_id, room=new_room, is_admin=True)
                member2 = RoomMember(
                    member_id=second_user_id,
                    room=new_room,
                    is_admin=False,
                    left_room=True,
                )
                test_get_session.add_all([new_room, member, member2])
                await test_get_session.commit()

                # invite to room
                invite_response = await client.post(
                    url="/api/v1/room-invitations",
                    json={"invitee_id": second_user_id, "room_id": new_room.id},
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert invite_response.status_code == 201

                invite_data: dict = invite_response.json()

                assert invite_data["data"]["invitee_id"] == second_user_id
                invitation_id = invite_data["data"]["id"]

                invitation = (
                    await test_get_session.execute(
                        sa.select(RoomInvitation).where(
                            RoomInvitation.id == invitation_id
                        )
                    )
                ).scalar_one_or_none()
                assert invitation is not None

                assert invitation.invitation_status == "pending"

    @pytest.mark.asyncio
    async def test_h_when_user_has_existing_invitation_returns_201(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when user has existing invitation returns 201
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
                new_room = Room(
                    name="My Dear room",
                    owner_id=user_id,
                    allow_non_admin_invitations=False,
                )
                member = RoomMember(member_id=user_id, room=new_room, is_admin=True)
                test_get_session.add_all([new_room, member])
                await test_get_session.commit()

                # invite to room
                expiration = datetime.now(timezone.utc) + timedelta(days=7)
                new_invitation = RoomInvitation(
                    room_id=new_room.id,
                    inviter_id=user_id,
                    invitee_id=second_user_id,
                    expiration=expiration,
                    invitation_status="pending",
                )
                test_get_session.add(new_invitation)
                await test_get_session.commit()

                # invite to room again
                invite_response = await client.post(
                    url="/api/v1/room-invitations",
                    json={"invitee_id": second_user_id, "room_id": new_room.id},
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert invite_response.status_code == 409

                invite_data: dict = invite_response.json()

                assert (
                    invite_data["message"]
                    == "Invitee already has an Invitation to this room."
                )

    @pytest.mark.asyncio
    async def test_i_when_user_invitation_canceled_returns_201(
        self, test_setup: None, client: AsyncClient, test_get_session: AsyncSession
    ):
        """
        Tests when user has existing canceled/rejected/expired invitation returns 201
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
                new_room = Room(
                    name="My Dear room",
                    owner_id=user_id,
                    allow_non_admin_invitations=False,
                )
                member = RoomMember(member_id=user_id, room=new_room, is_admin=True)
                test_get_session.add_all([new_room, member])
                await test_get_session.commit()

                # invite to room

                expiration = datetime.now(timezone.utc) + timedelta(days=7)
                new_invitation = RoomInvitation(
                    room=new_room,
                    inviter_id=user_id,
                    invitee_id=second_user_id,
                    expiration=expiration,
                    invitation_status="cancelled",
                )
                test_get_session.add(new_invitation)
                await test_get_session.commit()

                # invite to room again
                invite_response = await client.post(
                    url="/api/v1/room-invitations",
                    json={"invitee_id": second_user_id, "room_id": new_room.id},
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                assert invite_response.status_code == 201

                invite_data: dict = invite_response.json()

                assert invite_data["data"]["id"] == new_invitation.id

                await test_get_session.refresh(new_invitation)

                invitation = (
                    await test_get_session.execute(
                        sa.select(RoomInvitation).where(
                            RoomInvitation.id == new_invitation.id
                        )
                    )
                ).scalar_one_or_none()
                assert invitation is not None

                assert invitation.invitation_status == "pending"
