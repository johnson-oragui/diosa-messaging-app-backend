import pytest

from app.v1.rooms.services import (
    room_service,
    room_member_service,
    room_invitation_service
)
from app.v1.users.services import user_service
from app.core.custom_exceptions import (
    UserNotAnAdminError,
    InvitationNotFoundError,
)


class TestRoomInvitationService:
    """
    Test class for room_invitation_service
    """
    async def test_create(self,
                          mock_jayson_user_dict,
                          mock_public_room_one_dict,
                          mock_johnson_user_dict,
                          test_get_session,
                          test_setup):
        """
        Test create room.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)
        mock_public_room_one_dict["creator_id"] = jayson.id

        new_room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="private",
            description="a private room"
        )

        room_invitation = await room_invitation_service.create(
            {
                "room_id": new_room.id,
                "inviter_id": jayson.id,
                "invitee_id": johnson.id,
                "room_type": new_room.room_type
            },
            test_get_session
        )

        assert room_invitation.inviter_id == jayson.id
        assert room_invitation.invitee_id == johnson.id
        assert room_invitation.invitation_status == "pending"

    async def test_create_all(self,
                          mock_jayson_user_dict,
                          mock_johnson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test create  multiple room_members.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)
        jackson = await user_service.create(
            {
                "first_name": "jackson",
                "last_name": "jackson",
                "email": "jackson@gmail.com",
                "password": "Johnson1234#",
                "username": "jackson",
                "idempotency_key": "jackson0jki2jfi2",
            },
            test_get_session
        )

        mock_public_room_one_dict["creator_id"] = jayson.id

        new_room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="private",
            description="a private room"
        )

        room_invitations = await room_invitation_service.create_all(
            [
                {
                    "room_id": new_room.id,
                    "inviter_id": jayson.id,
                    "invitee_id": johnson.id,
                    "room_type": new_room.room_type
                },
                {
                    "room_id": new_room.id,
                    "inviter_id": jayson.id,
                    "invitee_id": jackson.id,
                    "room_type": new_room.room_type
                },
            ],
            test_get_session
        )

        assert isinstance(room_invitations, list)
        assert len(room_invitations) == 2

    async def test_fetch(self,
                          mock_jayson_user_dict,
                          mock_johnson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test fetch room member.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)
        mock_public_room_one_dict["creator_id"] = jayson.id

        room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            room_type="private",
            creator_id=jayson.id,
            session=test_get_session
        )

        room_invitation = await room_invitation_service.create(
            {
                "room_id": room.id,
                "inviter_id": jayson.id,
                "invitee_id": johnson.id,
                "room_type": room.room_type
            },
            test_get_session
        )

        fetched_room_invitation = await room_invitation_service.fetch(
            {"id": room_invitation.id, "inviter_id": jayson.id},
            test_get_session
        )

        assert room_invitation.id == fetched_room_invitation.id
        assert room_invitation.invitee_id == fetched_room_invitation.invitee_id
        assert room_invitation.inviter_id == fetched_room_invitation.inviter_id

    async def test_fetch_all(self,
                          mock_jayson_user_dict,
                          mock_public_room_one_dict,
                          mock_johnson_user_dict,
                          test_get_session,
                          test_setup):
        """
        Test fetch all rooms members.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)
        jackson = await user_service.create(
            {
                "first_name": "jackson",
                "last_name": "jackson",
                "email": "jackson@gmail.com",
                "password": "Johnson1234#",
                "username": "jackson",
                "idempotency_key": "jackson0jki2jfi2",
            },
            test_get_session
        )

        mock_public_room_one_dict["creator_id"] = jayson.id

        new_room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="private",
            description="a private room"
        )

        room_invitations = await room_invitation_service.create_all(
            [
                {"room_id": new_room.id, "inviter_id": jayson.id, "invitee_id": johnson.id, "room_type": new_room.room_type},
                {"room_id": new_room.id, "inviter_id": jayson.id, "invitee_id": jackson.id, "room_type": new_room.room_type},
            ],
            test_get_session
        )

        fetched_invitations = await room_invitation_service.fetch_all(
            {"inviter_id": jayson.id},
            test_get_session
        )

        assert isinstance(fetched_invitations, list)
        assert len(fetched_invitations) == 2
        assert fetched_invitations == room_invitations


    async def test_delete(self,
                          mock_jayson_user_dict,
                          mock_johnson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test delete room member.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)
        mock_public_room_one_dict["creator_id"] = jayson.id

        new_room, new_room_member, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="private",
            description="a private room"
        )

        room_invitation = await room_invitation_service.create(
            {"room_id": new_room.id, "inviter_id": jayson.id, "invitee_id": johnson.id, "room_type": new_room.room_type},
            test_get_session
        )

        assert room_invitation.inviter_id == jayson.id
        assert room_invitation.invitee_id == johnson.id
        assert room_invitation.invitation_status == "pending"

        deleted_room_inivtation = await room_invitation_service.delete(
            {"invitee_id": johnson.id},
            test_get_session
        )
        fetched_room_inivtation = await room_invitation_service.fetch(
            {"invitee_id": johnson.id},
            test_get_session
        )

        assert fetched_room_inivtation == None
        assert deleted_room_inivtation.id == room_invitation.id

    async def test_delete_all(self,
                            mock_jayson_user_dict,
                            mock_public_room_one_dict,
                            mock_johnson_user_dict,
                            test_get_session,
                            test_setup):
        """
        Test delete all rooms members.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)
        jackson = await user_service.create(
            {
                "first_name": "jackson",
                "last_name": "jackson",
                "email": "jackson@gmail.com",
                "password": "Johnson1234#",
                "username": "jackson",
                "idempotency_key": "jackson0jki2jfi2",
            },
            test_get_session
        )

        mock_public_room_one_dict["creator_id"] = jayson.id

        new_room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="private",
            description="a private room"
        )

        room_invitations = await room_invitation_service.create_all(
            [
                {"room_id": new_room.id, "inviter_id": jayson.id, "invitee_id": johnson.id, "room_type": new_room.room_type},
                {"room_id": new_room.id, "inviter_id": jayson.id, "invitee_id": jackson.id, "room_type": new_room.room_type},
            ],
            test_get_session
        )

        fetched_invitations = await room_invitation_service.fetch_all(
            {"inviter_id": jayson.id},
            test_get_session
        )

        assert isinstance(fetched_invitations, list)
        assert len(fetched_invitations) == 2
        assert fetched_invitations == room_invitations

        deleted_invitations = await room_invitation_service.delete_all(
            session=test_get_session
        )

        fetched_invitations_2 = await room_invitation_service.fetch_all(
            {"inviter_id": jayson.id},
            test_get_session
        )

        assert isinstance(fetched_invitations_2, list)
        assert len(fetched_invitations_2) == 0
        assert fetched_invitations_2 == []
        assert deleted_invitations[0].id == fetched_invitations[0].id

    @pytest.mark.asyncio
    async def test_update(self,
                          mock_johnson_user_dict,
                          mock_jayson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test room_member_service update method.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)
        mock_public_room_one_dict["creator_id"] = jayson.id

        new_room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="private",
            description="a private room"
        )

        room_invitation = await room_invitation_service.create(
            {"room_id": new_room.id, "inviter_id": jayson.id, "invitee_id": johnson.id, "room_type": new_room.room_type},
            test_get_session
        )

        assert room_invitation.invitation_status == "pending"

        updated_room_invitation = await room_invitation_service.update(
            [
                {"room_id": new_room.id, "inviter_id": jayson.id, "invitee_id": johnson.id},
                {"invitation_status": "accepted"}
            ],
            test_get_session
        )

        fetched_room_invitation = await room_invitation_service.fetch(
            {"room_id": new_room.id, "inviter_id": jayson.id, "invitee_id": johnson.id},
            test_get_session
        )

        assert fetched_room_invitation.invitation_status == updated_room_invitation.invitation_status


    async def test_invite_user_to_private_room(self,
                          mock_jayson_user_dict,
                          mock_johnson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test invite user to private room.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)

        new_room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="private",
            description="a private room"
        )

        room_invitation = await room_invitation_service.invite_user_to_room(
            invitee_id=johnson.id,
            inviter_id=jayson.id,
            room_id=new_room.id,
            session=test_get_session
        )

        assert room_invitation.inviter_id == jayson.id
        assert room_invitation.invitee_id == johnson.id

    async def test_invite_user_to_public_room(self,
                          mock_jayson_user_dict,
                          mock_johnson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test invite user to public room.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)

        new_room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="public",
            description="a public room"
        )

        room_invitation = await room_invitation_service.invite_user_to_room(
            invitee_id=johnson.id,
            inviter_id=jayson.id,
            room_id=new_room.id,
            session=test_get_session
        )

        assert room_invitation.inviter_id == jayson.id
        assert room_invitation.invitee_id == johnson.id

    async def test_invite_user_to_room_unsuccessful(self,
                          mock_jayson_user_dict,
                          mock_johnson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test invite user to room raises UserNotAnAdminError.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)

        new_room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="private",
            description="a private room"
        )

        with pytest.raises(UserNotAnAdminError):
            await room_invitation_service.invite_user_to_room(
                invitee_id=jayson.id,
                inviter_id=johnson.id,
                room_id=new_room.id,
                session=test_get_session
            )

    async def test_accept_private_room_invitations(self,
                          mock_jayson_user_dict,
                          mock_johnson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test accept private room invitations.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)

        new_room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="private",
            description="a private room"
        )

        room_invitation = await room_invitation_service.invite_user_to_room(
            invitee_id=johnson.id,
            inviter_id=jayson.id,
            room_id=new_room.id,
            session=test_get_session
        )

        assert room_invitation.invitation_status == "pending"

        johnson_not_room_member = await room_member_service.fetch(
            {"user_id": johnson.id},
            test_get_session
        )

        assert johnson_not_room_member == None

        accepted_invitation, new_room_member = await room_invitation_service.accept_room_invitations(
            invitee_id=johnson.id,
            room_id=new_room.id,
            session=test_get_session
        )

        assert accepted_invitation.invitation_status == "accepted"

        johnson_room_member = await room_member_service.fetch(
            {"user_id": johnson.id},
            test_get_session
        )

        assert johnson_room_member is not None
        assert johnson_room_member == new_room_member

    async def test_accept_public_room_invitations(self,
                          mock_jayson_user_dict,
                          mock_johnson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test accept public room invitations.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)

        new_room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="public",
            description="a public room"
        )

        room_invitation = await room_invitation_service.invite_user_to_room(
            invitee_id=johnson.id,
            inviter_id=jayson.id,
            room_id=new_room.id,
            session=test_get_session
        )

        assert room_invitation.invitation_status == "pending"

        johnson_not_room_member = await room_member_service.fetch(
            {"user_id": johnson.id},
            test_get_session
        )

        assert johnson_not_room_member == None

        accepted_invitation, new_room_member = await room_invitation_service.accept_room_invitations(
            invitee_id=johnson.id,
            room_id=new_room.id,
            session=test_get_session
        )

        assert accepted_invitation.invitation_status == "accepted"

        johnson_room_member = await room_member_service.fetch(
            {"user_id": johnson.id},
            test_get_session
        )

        assert johnson_room_member is not None
        assert johnson_room_member == new_room_member

    async def test_accept_room_invitations_unsuccessfull(self,
                          mock_jayson_user_dict,
                          mock_johnson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test accept room invitations raises InvitationNotFoundError.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)

        new_room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="private",
            description="a private room"
        )

        with pytest.raises(InvitationNotFoundError):
            _, _ = await room_invitation_service.accept_room_invitations(
                invitee_id=johnson.id,
                room_id=new_room.id,
                session=test_get_session
            )

    async def test_reject_room_invitations(self,
                          mock_jayson_user_dict,
                          mock_johnson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test reject room invitations.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)

        new_room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="public",
            description="a public room"
        )

        room_invitation = await room_invitation_service.invite_user_to_room(
            invitee_id=johnson.id,
            inviter_id=jayson.id,
            room_id=new_room.id,
            session=test_get_session
        )

        assert room_invitation.invitation_status == "pending"

        johnson_not_room_member = await room_member_service.fetch(
            {"user_id": johnson.id},
            test_get_session
        )

        assert johnson_not_room_member == None

        rejected_invitation, new_room_member = await room_invitation_service.rejects_room_invitations(
            invitee_id=johnson.id,
            room_id=new_room.id,
            session=test_get_session
        )

        assert rejected_invitation.invitation_status == "declined"

        johnson_room_member = await room_member_service.fetch(
            {"user_id": johnson.id},
            test_get_session
        )

        assert johnson_room_member is None
