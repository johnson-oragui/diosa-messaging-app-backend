import pytest

from app.v1.rooms.services import (
    room_service,
    room_member_service,
)
from app.v1.users.services import user_service


class TestRoomService:
    """
    Test class for room_service
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

        assert new_room.creator_id == new_user.id

    async def test_create_all(self,
                          mock_jayson_user_dict,
                          mock_public_room_one_dict,
                          mock_public_room_two_dict,
                          test_get_session,
                          test_setup):
        """
        Test create  multiple rooms.
        """
        new_user = await user_service.create(mock_jayson_user_dict, test_get_session)

        mock_public_room_one_dict["creator_id"] = new_user.id
        mock_public_room_two_dict["creator_id"] = new_user.id

        new_rooms = await room_service.create_all(
            [
                mock_public_room_one_dict,
                mock_public_room_two_dict
            ],
            test_get_session
        )

        assert isinstance(new_rooms, list)
        assert new_rooms[0].room_name == mock_public_room_one_dict["room_name"]
        assert new_rooms[1].room_name == mock_public_room_two_dict["room_name"]

    async def test_fetch(self,
                          mock_jayson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test fetch room.
        """
        new_user = await user_service.create(mock_jayson_user_dict, test_get_session)
        mock_public_room_one_dict["creator_id"] = new_user.id

        new_room = await room_service.create(
            mock_public_room_one_dict,
            test_get_session
        )

        fetched_room = await room_service.fetch(
            {"creator_id": new_user.id},
            test_get_session
        )

        assert fetched_room == new_room

    async def test_fetch_all(self,
                          mock_jayson_user_dict,
                          mock_public_room_one_dict,
                          mock_public_room_two_dict,
                          test_get_session,
                          test_setup):
        """
        Test fetch all rooms.
        """
        new_user = await user_service.create(mock_jayson_user_dict, test_get_session)

        mock_public_room_one_dict["creator_id"] = new_user.id
        mock_public_room_two_dict["creator_id"] = new_user.id

        new_rooms = await room_service.create_all(
            [
                mock_public_room_one_dict,
                mock_public_room_two_dict
            ],
            test_get_session
        )

        fetched_rooms = await room_service.fetch_all(
            {
                "creator_id": new_user.id
            },
            test_get_session
        )

        assert fetched_rooms == new_rooms

    async def test_delete(self,
                          mock_jayson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test delete room.
        """
        new_user = await user_service.create(mock_jayson_user_dict, test_get_session)
        mock_public_room_one_dict["creator_id"] = new_user.id

        new_room = await room_service.create(
            mock_public_room_one_dict,
            test_get_session
        )

        deleted_room = await room_service.delete(
            {"creator_id": new_user.id},
            test_get_session
        )

        fetched_room = await room_service.fetch(
            {"creator_id": new_user.id},
            test_get_session
        )

        assert fetched_room == None
        assert deleted_room.room_name == new_room.room_name

    async def test_delete_all(self,
                            mock_jayson_user_dict,
                            mock_public_room_one_dict,
                            mock_public_room_two_dict,
                            test_get_session,
                            test_setup):
        """
        Test delete all rooms.
        """
        new_user = await user_service.create(mock_jayson_user_dict, test_get_session)

        mock_public_room_one_dict["creator_id"] = new_user.id
        mock_public_room_two_dict["creator_id"] = new_user.id

        new_rooms = await room_service.create_all(
            [
                mock_public_room_one_dict,
                mock_public_room_two_dict
            ],
            test_get_session
        )

        deleted_rooms = await room_service.delete_all(session=test_get_session)

        fetched_users = await room_service.fetch_all({}, test_get_session)

        assert fetched_users == []
        assert deleted_rooms[0].room_name == new_rooms[0].room_name
        assert deleted_rooms[1].room_name == new_rooms[1].room_name

    @pytest.mark.asyncio
    async def test_update(self,
                          mock_johnson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test room_service update method.
        """
        new_user = await user_service.create(mock_johnson_user_dict, test_get_session)
        mock_public_room_one_dict["creator_id"] = new_user.id

        new_room = await room_service.create(
            mock_public_room_one_dict,
            test_get_session
        )

        updated_room = await room_service.update(
            [
                {"creator_id": new_user.id},
                {"room_name": "updated_room"}
            ],
            test_get_session
        )

        assert new_room.room_name == "updated_room"
        assert updated_room == new_room
        assert updated_room != mock_public_room_one_dict["room_name"]

    async def test_create_a_public_or_private_room(self,
                          mock_jayson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test create a public or private room
        """
        new_user = await user_service.create(mock_jayson_user_dict, test_get_session)

        new_room, room_member, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=new_user.id,
            session=test_get_session,
            room_type=mock_public_room_one_dict["room_type"],
            description=mock_public_room_one_dict["description"]
        )

        assert new_room is not None
        assert room_member is not None
        assert new_room.room_type == 'public'
        assert room_member.is_admin == True

    async def test_create_direct_message_roome(self,
                                                mock_johnson_user_dict,
                                                mock_jayson_user_dict,
                                                test_get_session,
                                                test_setup):
        """
        Test Create a direct-message-room.
        """
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)

        new_dm_room, _, _ = await room_service.create_direct_message_room(
            jayson.id,
            johnson.id,
            test_get_session
        )

        room_members = await room_member_service.fetch_all(
            {
                "room_id": new_dm_room.id
            },
            test_get_session
        )

        assert new_dm_room.room_type == "direct_message"
        assert room_members[0].is_admin == True
        assert room_members[1].is_admin == True

    async def test_search_public_rooms(self,
                                        mock_johnson_user_dict,
                                        mock_public_room_one_dict,
                                        mock_private_room_one_dict,
                                        test_get_session,
                                        test_setup):
        """
        Test search public rooms
        """
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)
        mock_private_room_one_dict["creator_id"] = johnson.id
        mock_public_room_one_dict["creator_id"] = johnson.id

        await room_service.create_all(
            [
                mock_private_room_one_dict,
                mock_public_room_one_dict
            ],
            test_get_session
        )

        public_rooms = await room_service.search_public_rooms(
            keyword="room_one",
            session=test_get_session
        )

        assert len(public_rooms) == 1
        assert public_rooms[0].room_type != "private"

    async def test_fetch_rooms_user_belongs_to(self,
                                        mock_johnson_user_dict,
                                        mock_public_room_one_dict,
                                        mock_private_room_one_dict,
                                        test_get_session,
                                        test_setup):
        """
        Test fetch_rooms_user_belongs_to method
        """
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)

        await room_service.create_a_public_or_private_room(
            room_name=mock_private_room_one_dict["room_name"],
            room_type=mock_private_room_one_dict["room_type"],
            creator_id=johnson.id,
            session=test_get_session,
            messages_deletable=False,
        )
        await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            room_type=mock_public_room_one_dict["room_type"],
            creator_id=johnson.id,
            session=test_get_session,
            messages_deletable=False,
        )

        rooms = await room_service.fetch_rooms_user_belongs_to(
            johnson.id,
            test_get_session
        )

        assert len(rooms) == 2
        assert rooms[0].room_type == "private"
        assert rooms[1].room_type == "public"

    async def test_fetch_user_direct_message_rooms(self,
                                        mock_johnson_user_dict,
                                        mock_jayson_user_dict,
                                        test_get_session,
                                        test_setup):
        """
        Test fetch_user_direct_message_rooms method
        """
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)

        _, _, _ = await room_service.create_direct_message_room(
            user_id_1=johnson.id,
            user_id_2=jayson.id,
            session=test_get_session,
        )

        rooms = await room_service.fetch_user_direct_message_rooms(
            johnson.id,
            test_get_session
        )

        assert len(rooms) == 1
        assert rooms[0].room_name.startswith("DM")
        assert rooms[0].username == jayson.username
