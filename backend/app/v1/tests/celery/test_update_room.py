import time
import pytest

from app.v1.users.services import user_service
from app.v1.rooms.services import room_service
from app.v1.rooms.services import room_member_service
from app.v1.profile.services import profile_service
from app.v1.chats.services import message_service



class TestCelery:
    """
    Tests Celery app.
    """
    @pytest.mark.skip("needs celery to be running in a different process.")
    @pytest.mark.asyncio
    async def test_update_room_fields_route_with_celery(self,
                                                        celery_app,
                                                        client,
                                                        mock_johnson_user_dict,
                                                        mock_jayson_user_dict,
                                                        mock_user_id,
                                                        test_get_session,
                                                        test_setup):
        """
        Tests successfull updating of roo-field route.
        """
        # create jayson user
        jayson = await user_service.create(
            mock_jayson_user_dict,
            test_get_session
        )
        _ = await profile_service.create(
            {"user_id": jayson.id},
            test_get_session
        )

        mock_johnson_user_dict["id"] = mock_user_id

        # create johnson user
        johnson = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )
        _ = await profile_service.create(
            {"user_id": mock_user_id},
            test_get_session
        )

        # jayson creates room, and messages are not deletable
        new_room, _, _ =await room_service.create_a_public_or_private_room(
            room_name="public-room-name",
            creator_id=johnson.id,
            session=test_get_session,
            messages_deletable=False,
            room_type="public"
        )

        await room_member_service.create(
            {
                "room_id": new_room.id,
                "user_id": jayson.id,
                "room_type": "public",
            },
            test_get_session
        )

        for _ in range(50):
            # jayson and johnson creates messages.
            _ = await message_service.create_all(
                [
                    {
                        "room_id": new_room.id,
                        "user_id": jayson.id,
                        "content": "Hello johnson",
                        "chat_type": "public",
                    },
                    {
                        "room_id": new_room.id,
                        "user_id": mock_johnson_user_dict["id"],
                        "content": "Hello Jayson",
                        "chat_type": "public",
                    }
                ],
                test_get_session
            )

        # request to update room.messages_deletable and room_type
        response = client.put(
            url=f"/api/v1/rooms/{new_room.id}",
            json={
                "messages_deletable": True,
                "room_type": "private",
                "description": "great one",
            },
            headers={
                "Authorization": "Bearer fake",
            }
        )

        assert response.status_code == 201
        data = response.json()

        assert data["data"]["room_type"] == "private"
        assert data["data"]["messages_deletable"] == True
        assert data["data"]["description"] == "great one"

        time.sleep(5)

        # fetch messages as private chat-type
        johnson_messages = await message_service.fetch_all(
            {
                "room_id": new_room.id,
                "chat_type": "private",
                "user_id": johnson.id
            },
            test_get_session
        )
        jayson_messages = await message_service.fetch_all(
            {
                "room_id": new_room.id,
                "chat_type": "private",
                "user_id": jayson.id,

            },
            test_get_session
        )

        assert len(johnson_messages) == 50
        assert len(jayson_messages) == 50
