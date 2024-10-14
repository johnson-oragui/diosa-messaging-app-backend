import pytest

from app.v1.rooms.services import (
    room_service,
)
from app.v1.chats.services import message_service
from app.v1.users.services import user_service
from app.core.custom_exceptions import CannotDeleteMessageError


class TestMessageService:
    """
    Test class for message service class
    """
    async def test_create(self,
                          mock_jayson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test create a message.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        mock_public_room_one_dict["creator_id"] = jayson.id

        new_room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="private",
            description="a private room"
        )

        johnson_message = await message_service.create(
            {
                "user_id": jayson.id,
                "room_id": new_room.id,
                "content": "What is happening?",
                "chat_type": new_room.room_type,
            },
            test_get_session
        )

        assert johnson_message.content == "What is happening?"
        assert johnson_message.chat_type == new_room.room_type

    async def test_create_all(self,
                          mock_jayson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test create  multiple messages.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)

        mock_public_room_one_dict["creator_id"] = jayson.id

        new_room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="private",
            description="a private room"
        )

        johnson_messages = await message_service.create_all(
            [
                {
                    "user_id": jayson.id,
                    "room_id": new_room.id,
                    "content": "What is happening?",
                    "chat_type": new_room.room_type,
                },
                {
                    "user_id": jayson.id,
                    "room_id": new_room.id,
                    "content": "Anybody here!!!!!",
                    "chat_type": new_room.room_type,
                },
            ],
            test_get_session
        )

        assert johnson_messages[0].content == "What is happening?"
        assert johnson_messages[1].content == "Anybody here!!!!!"

    async def test_fetch(self,
                          mock_jayson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test fetch room message.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        mock_public_room_one_dict["creator_id"] = jayson.id

        new_room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="private",
            description="a private room"
        )

        johnson_message = await message_service.create(
            {
                "user_id": jayson.id,
                "room_id": new_room.id,
                "content": "What is happening?",
                "chat_type": new_room.room_type,
            },
            test_get_session
        )

        fetched_johnson_message = await message_service.fetch(
            {
                "user_id": jayson.id,
                "room_id": new_room.id,
                "content": "What is happening?",
                "chat_type": new_room.room_type,
            },
            test_get_session
        )

        assert johnson_message.content == fetched_johnson_message.content
        assert johnson_message.chat_type == fetched_johnson_message.chat_type

    async def test_fetch_all(self,
                          mock_jayson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test fetch all rooms messages.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)

        mock_public_room_one_dict["creator_id"] = jayson.id

        new_room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="private",
            description="a private room"
        )

        johnson_messages = await message_service.create_all(
            [
                {
                    "user_id": jayson.id,
                    "room_id": new_room.id,
                    "content": "What is happening?",
                    "chat_type": new_room.room_type,
                },
                {
                    "user_id": jayson.id,
                    "room_id": new_room.id,
                    "content": "Anybody here!!!!!",
                    "chat_type": new_room.room_type,
                },
            ],
            test_get_session
        )

        fetch_johnson_messages = await message_service.fetch_all(
            {
                "user_id": jayson.id,
                "room_id": new_room.id,
                "chat_type": new_room.room_type,
            },
            test_get_session
        )

        assert johnson_messages[0].content == fetch_johnson_messages[0].content
        assert johnson_messages[1].content == fetch_johnson_messages[1].content
        


    async def test_delete(self,
                          mock_jayson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test delete room member.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        mock_public_room_one_dict["creator_id"] = jayson.id

        new_room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="private",
            description="a private room"
        )

        johnson_message = await message_service.create(
            {
                "user_id": jayson.id,
                "room_id": new_room.id,
                "content": "What is happening?",
                "chat_type": new_room.room_type,
            },
            test_get_session
        )

        assert johnson_message.content == "What is happening?"
        assert johnson_message.chat_type == new_room.room_type

        await message_service.delete(
            {
                "user_id": jayson.id,
                "room_id": new_room.id,
            },
            test_get_session
        )
        
        fetched_johnson_message = await message_service.fetch(
            {
                "user_id": jayson.id,
                "room_id": new_room.id,
            },
            test_get_session
        )

        assert fetched_johnson_message == None

    async def test_delete_all(self,
                            mock_jayson_user_dict,
                            mock_public_room_one_dict,
                            test_get_session,
                            test_setup):
        """
        Test delete all rooms messages.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)

        mock_public_room_one_dict["creator_id"] = jayson.id

        new_room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="private",
            description="a private room"
        )

        johnson_messages = await message_service.create_all(
            [
                {
                    "user_id": jayson.id,
                    "room_id": new_room.id,
                    "content": "What is happening?",
                    "chat_type": new_room.room_type,
                },
                {
                    "user_id": jayson.id,
                    "room_id": new_room.id,
                    "content": "Anybody here!!!!!",
                    "chat_type": new_room.room_type,
                },
            ],
            test_get_session
        )

        assert len(johnson_messages) == 2

        

        await message_service.delete_all(
            session=test_get_session
        )

        fetch_johnson_messages = await message_service.fetch_all(
            {
                "user_id": jayson.id,
                "room_id": new_room.id,
                "chat_type": new_room.room_type,
            },
            test_get_session
        )

        assert len(fetch_johnson_messages) == 0

    @pytest.mark.asyncio
    async def test_update(self,
                          mock_jayson_user_dict,
                          mock_public_room_one_dict,
                          test_get_session,
                          test_setup):
        """
        Test message service update method.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        mock_public_room_one_dict["creator_id"] = jayson.id

        new_room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="private",
            description="a private room"
        )

        johnson_message = await message_service.create(
            {
                "user_id": jayson.id,
                "room_id": new_room.id,
                "content": "What is happening?",
                "chat_type": new_room.room_type,
            },
            test_get_session
        )

        assert johnson_message.content == "What is happening?"
        assert johnson_message.chat_type == new_room.room_type

        updated_message = await message_service.update(
            [
                {"user_id": jayson.id, "room_id": new_room.id},
                {"content": "Yeah, I changed my mind"}
            ],
            test_get_session
        )

        fetched_message = await message_service.fetch(
            {"user_id": jayson.id, "room_id": new_room.id},
            test_get_session
        )

        assert fetched_message.content == "Yeah, I changed my mind"
        assert fetched_message == updated_message

    async def test_delete_message_success(self, mock_johnson_user_dict,
                                          mock_jayson_user_dict,
                                          mock_public_room_one_dict,
                                          test_get_session,
                                          test_setup):
        """
        Tests room messages deletable
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

        assert new_room.messages_deletable == True

        johnson_message = await message_service.create(
            {
                "user_id": johnson.id,
                "room_id": new_room.id,
                "content": "What is happening?",
                "chat_type": new_room.room_type,
            },
            test_get_session
        )

        await message_service.delete_message(
            new_room.id,
            johnson.id,
            johnson_message.id,
            test_get_session
        )

        fetched_message = await message_service.fetch(
            {
                "id": johnson_message.id
            },
            test_get_session
        )

        assert fetched_message == None

    async def test_delete_message_success_for_admin_only(self, mock_johnson_user_dict,
                                          mock_jayson_user_dict,
                                          mock_public_room_one_dict,
                                          test_get_session,
                                          test_setup):
        """
        Tests room messages deletable success for admin.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)
        mock_public_room_one_dict["creator_id"] = jayson.id

        new_room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_public_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="private",
            description="a private room",
            messages_deletable=False
        )

        assert new_room.messages_deletable == False

        johnson_message = await message_service.create(
            {
                "user_id": johnson.id,
                "room_id": new_room.id,
                "content": "What is happening?",
                "chat_type": new_room.room_type,
            },
            test_get_session
        )
        with pytest.raises(CannotDeleteMessageError):
            await message_service.delete_message(
                new_room.id,
                johnson.id,
                johnson_message.id,
                test_get_session
            )

        await message_service.delete_message(
            room_id=new_room.id,
            user_id=jayson.id,
            message_id=johnson_message.id,
            session=test_get_session
        )

        fetched_message = await message_service.fetch(
            {
                "id": johnson_message.id
            },
            test_get_session
        )

        assert fetched_message == None

    async def test_delete_direct_messages_message_success(self, mock_johnson_user_dict,
                                          mock_jayson_user_dict,
                                          mock_public_room_one_dict,
                                          test_get_session,
                                          test_setup):
        """
        Tests room messages deletable success for direct messages.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)
        mock_public_room_one_dict["creator_id"] = jayson.id

        new_room, _, _ = await room_service.create_direct_message_room(
            user_id_1=jayson.id,
            user_id_2=johnson.id,
            session=test_get_session,
        )

        assert new_room.messages_deletable == True

        johnson_message = await message_service.create(
            {
                "user_id": johnson.id,
                "room_id": new_room.id,
                "content": "What is happening?",
                "chat_type": new_room.room_type,
            },
            test_get_session
        )
        with pytest.raises(CannotDeleteMessageError):
            await message_service.delete_message(
                new_room.id,
                jayson.id,
                johnson_message.id,
                test_get_session
            )

        await message_service.delete_message(
            new_room.id,
            johnson.id,
            johnson_message.id,
            test_get_session
        )

        fetched_message = await message_service.fetch(
            {
                "id": johnson_message.id
            },
            test_get_session
        )

        assert fetched_message == None

    async def test_delete_message_unsuccessful(self, mock_johnson_user_dict,
                                          mock_jayson_user_dict,
                                          mock_private_room_one_dict,
                                          test_get_session,
                                          test_setup):
        """
        Tests room messages deletable unsuccessful
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)
        mock_private_room_one_dict["creator_id"] = jayson.id

        new_room, _, _ = await room_service.create_a_public_or_private_room(
            room_name=mock_private_room_one_dict["room_name"],
            creator_id=jayson.id,
            session=test_get_session,
            room_type="private",
            description="a private room",
            messages_deletable=False
        )

        assert new_room.messages_deletable == False

        johnson_message = await message_service.create(
            {
                "user_id": johnson.id,
                "room_id": new_room.id,
                "content": "What is happening?",
                "chat_type": new_room.room_type,
            },
            test_get_session
        )

        with pytest.raises(CannotDeleteMessageError):
            await message_service.delete_message(
                new_room.id,
                johnson.id,
                johnson_message.id,
                test_get_session
            )

