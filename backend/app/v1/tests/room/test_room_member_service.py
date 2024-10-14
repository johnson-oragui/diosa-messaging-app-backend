import pytest

from app.v1.rooms.services import (
    room_service,
    room_member_service,
)
from app.v1.users.services import user_service
from app.core.custom_exceptions import (
    RoomNotFoundError,
    UserNotAMemberError,
)


class TestRoommemberService:
    """
    Test class for room_member-service
    """
    async def test_create(self,
                          mock_jayson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test create room.
        """
        new_user = await user_service.create(mock_jayson_user_dict, test_get_session)
        mock_public_room_one_dict["creator_id"] = new_user.id

        new_room = await room_service.create(
            mock_public_room_one_dict,
            test_get_session
        )

        new_room_member = await room_member_service.create(
            {"user_id": new_user.id, "room_id": new_room.id, "is_admin": True, "room_type": new_room.room_type},
            test_get_session
        )

        assert new_room.creator_id == new_room_member.user_id

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

        mock_public_room_one_dict["creator_id"] = jayson.id

        new_room = await room_service.create(
            mock_public_room_one_dict,
            test_get_session
        )

        room_members = await room_member_service.create_all(
            [
                {"user_id": jayson.id, "is_admin": True, "room_id": new_room.id, "room_type": new_room.room_type},
                {"user_id": johnson.id, "room_id": new_room.id, "room_type": new_room.room_type}
            ],
            test_get_session
        )

        assert isinstance(room_members, list)
        assert room_members[0].is_admin == True
        assert room_members[1].is_admin == False

    async def test_fetch(self,
                          mock_jayson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test fetch room member.
        """
        new_user = await user_service.create(mock_jayson_user_dict, test_get_session)
        mock_public_room_one_dict["creator_id"] = new_user.id

        _, room_member, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            room_type="private",
            creator_id=new_user.id,
            session=test_get_session
        )

        fetched_room_member = await room_member_service.fetch(
            {"user_id": new_user.id},
            test_get_session
        )

        assert fetched_room_member.user_id == room_member.user_id

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

        mock_public_room_one_dict["creator_id"] = jayson.id

        new_room = await room_service.create(
            mock_public_room_one_dict,
            test_get_session
        )

        jayson_member = await room_member_service.create(
            {"user_id": jayson.id, "room_id": new_room.id, "room_type": new_room.room_type},
            test_get_session
        )
        johnson_member = await room_member_service.create(
            {"user_id": johnson.id, "room_id": new_room.id, "room_type": new_room.room_type},
            test_get_session
        )

        fetched_room_members = await room_member_service.fetch_all(
            {
                "room_id": new_room.id
            },
            test_get_session
        )

        assert len(fetched_room_members) == 2
        assert fetched_room_members[0] == jayson_member
        assert fetched_room_members[1] == johnson_member

    async def test_delete(self,
                          mock_jayson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test delete room member.
        """
        new_user = await user_service.create(mock_jayson_user_dict, test_get_session)
        mock_public_room_one_dict["creator_id"] = new_user.id

        new_room = await room_service.create(
            mock_public_room_one_dict,
            test_get_session
        )

        room_member = await room_member_service.create(
            {"user_id": new_user.id, "room_id": new_room.id, "room_type": new_room.room_type},
            test_get_session
        )

        assert room_member.user_id == new_user.id

        deleted_room_member = await room_member_service.delete(
            {"user_id": new_user.id},
            test_get_session
        )

        fetched_room_member = await room_member_service.fetch(
            {"user_id": new_user.id},
            test_get_session
        )

        assert fetched_room_member == None
        assert deleted_room_member.room_id == new_room.id

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

        mock_public_room_one_dict["creator_id"] = jayson.id

        new_room = await room_service.create(
            mock_public_room_one_dict,
            test_get_session
        )

        room_members = await room_member_service.create_all(
            [
                {"user_id": jayson.id, "is_admin": True, "room_id": new_room.id, "room_type": new_room.room_type},
                {"user_id": johnson.id, "room_id": new_room.id, "room_type": new_room.room_type}
            ],
            test_get_session
        )

        assert isinstance(room_members, list)
        assert room_members[0].is_admin == True
        assert room_members[1].is_admin == False

        deleted_room_members = await room_member_service.delete_all(
            session=test_get_session
        )

        fetched_room_members = await room_member_service.fetch_all(
            {
                "room_id": new_room.id
            },
            test_get_session
        )

        assert len(deleted_room_members) != 0
        assert fetched_room_members == []

    @pytest.mark.asyncio
    async def test_update(self,
                          mock_johnson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test room_member_service update method.
        """
        new_user = await user_service.create(mock_johnson_user_dict, test_get_session)
        mock_public_room_one_dict["creator_id"] = new_user.id

        new_room = await room_service.create(
            mock_public_room_one_dict,
            test_get_session
        )
        
        new_room_member = await room_member_service.create(
            {"user_id": new_user.id, "room_id": new_room.id, "room_type": new_room.room_type},
            test_get_session
        )

        assert new_room_member.is_admin == False

        updated_room_member = await room_member_service.update(
            [
                {"user_id": new_user.id},
                {"is_admin": True}
            ],
            test_get_session
        )

        assert updated_room_member.is_admin == True
        assert new_room_member == updated_room_member

    async def test_join_public_room(self,
                          mock_jayson_user_dict,
                          mock_johnson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test join public room
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)

        new_room = await room_service.create(
            {"creator_id": jayson.id, "room_type": "public", "room_name": "new-pub"},
            test_get_session
        )

        jayson_room_member = await room_member_service.join_public_room(
            user_id=jayson.id,
            room_id=new_room.id,
            session=test_get_session
        )
        johnson_room_member = await room_member_service.join_public_room(
            user_id=johnson.id,
            room_id=new_room.id,
            session=test_get_session
        )

        assert new_room is not None
        assert jayson_room_member.room_type == "public"
        assert jayson_room_member.room_type != "private"
        assert johnson_room_member.room_type == "public"
        assert johnson_room_member.room_type != "private"

    async def test_join_public_room_with_private_type(self,
                          mock_jayson_user_dict,
                          test_get_session,
                          test_setup):
        """
        Test join public room
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)

        new_room = await room_service.create(
            {"creator_id": jayson.id, "room_type": "private", "room_name": "new-pub"},
            test_get_session
        )
        with pytest.raises(RoomNotFoundError):
            jayson_room_member = await room_member_service.join_public_room(
                user_id=jayson.id,
                room_id=new_room.id,
                session=test_get_session
            )

    async def test_join_private_room(self,
                          mock_jayson_user_dict,
                          mock_johnson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test join private room
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)

        new_room = await room_service.create(
            {"creator_id": jayson.id, "room_type": "private", "room_name": "new-pub"},
            test_get_session
        )

        jayson_room_member = await room_member_service.join_private_room_by_invite(
            user_id=jayson.id,
            room_id=new_room.id,
            session=test_get_session
        )
        johnson_room_member = await room_member_service.join_private_room_by_invite(
            user_id=johnson.id,
            room_id=new_room.id,
            session=test_get_session
        )

        assert new_room is not None
        assert jayson_room_member.room_type == "private"
        assert jayson_room_member.room_type != "public"
        assert johnson_room_member.room_type == "private"
        assert johnson_room_member.room_type != "public"

    async def test_join_private_room_with_public_type(self,
                          mock_jayson_user_dict,
                          test_get_session,
                          test_setup):
        """
        Test join public room
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)

        new_room = await room_service.create(
            {"creator_id": jayson.id, "room_type": "public", "room_name": "new-pub"},
            test_get_session
        )
        with pytest.raises(RoomNotFoundError):
            await room_member_service.join_private_room_by_invite(
                user_id=jayson.id,
                room_id=new_room.id,
                session=test_get_session
            )

    @pytest.mark.asyncio
    async def test_set_user_as_admin(self,
                          mock_johnson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test room_member_service.set_user_as_admin method.
        """
        new_user = await user_service.create(mock_johnson_user_dict, test_get_session)
        mock_public_room_one_dict["creator_id"] = new_user.id

        new_room = await room_service.create(
            mock_public_room_one_dict,
            test_get_session
        )
        
        new_room_member = await room_member_service.create(
            {"user_id": new_user.id, "room_id": new_room.id, "room_type": new_room.room_type},
            test_get_session
        )

        assert new_room_member.is_admin == False

        updated_room_member = await room_member_service.set_user_as_admin(
            room_id=new_room.id,
            user_id=new_user.id,
            session=test_get_session
        )

        assert updated_room_member.is_admin == True
        assert new_room_member == updated_room_member

    @pytest.mark.asyncio
    async def test_set_non_member_user_as_admin(self,
                          mock_johnson_user_dict,
                          mock_jayson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test unsuccessful room_member_service.set_user_as_admin method.
        """
        new_user = await user_service.create(mock_johnson_user_dict, test_get_session)
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        mock_public_room_one_dict["creator_id"] = new_user.id

        new_room = await room_service.create(
            mock_public_room_one_dict,
            test_get_session
        )

        with pytest.raises(UserNotAMemberError):
            await room_member_service.set_user_as_admin(
                room_id=new_room.id,
                user_id=jayson.id,
                session=test_get_session
            )

    @pytest.mark.asyncio
    async def test_is_user_admin(self,
                          mock_johnson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test room_member_service.is_user_admin method.
        """
        new_user = await user_service.create(mock_johnson_user_dict, test_get_session)
        mock_public_room_one_dict["creator_id"] = new_user.id

        new_room = await room_service.create(
            mock_public_room_one_dict,
            test_get_session
        )
        
        new_room_member = await room_member_service.create(
            {"user_id": new_user.id, "room_id": new_room.id, "room_type": new_room.room_type},
            test_get_session
        )

        is_user_admin = await room_member_service.is_user_admin(
            room_id=new_room.id,
            user_id=new_user.id,
            session=test_get_session
        )

        assert new_room_member.is_admin == is_user_admin  # False

        updated_room_member = await room_member_service.set_user_as_admin(
            room_id=new_room.id,
            user_id=new_user.id,
            session=test_get_session
        )

        is_user_admin_2 = await room_member_service.is_user_admin(
            room_id=new_room.id,
            user_id=new_user.id,
            session=test_get_session
        )

        assert updated_room_member.is_admin == is_user_admin_2  # True
        assert new_room_member == updated_room_member

