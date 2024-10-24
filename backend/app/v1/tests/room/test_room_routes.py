import pytest

from app.v1.users.services import user_service
from app.v1.rooms.services import room_service
from app.v1.rooms.services import room_member_service
from app.v1.profile.services import profile_service
from app.v1.chats.services import message_service


class TestPrivatePublicRoomRoute:
    """
    Test class for public or private room route
    """

    @pytest.mark.asyncio
    async def test_create_private_room_success(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test create private room success.
        """
        mock_johnson_user_dict["id"] = mock_user_id

        _ = await user_service.create(mock_johnson_user_dict, test_get_session)

        response = client.post(
            url="/api/v1/rooms/create",
            json={
                "room_name": "new-room",
                "room_type": "private",
                "messages_deletable": True
            },
            headers={
                "Authorization": f"Bearer fake"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Room Created Successfully"
        assert isinstance(data["data"]["room"], dict)
        assert isinstance(data["data"]["room_members"], list)

    @pytest.mark.asyncio
    async def test_create_private_room_idempotency(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test create private room idempotency.
        """
        mock_johnson_user_dict["id"] = mock_user_id

        _ = await user_service.create(mock_johnson_user_dict, test_get_session)

        response = client.post(
            url="/api/v1/rooms/create",
            json={
                "room_name": "new-room",
                "room_type": "private",
                "messages_deletable": True
            },
            headers={
                "Authorization": f"Bearer fake"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Room Created Successfully"
        assert isinstance(data["data"]["room"], dict)
        assert isinstance(data["data"]["room_members"], list)

        response2 = client.post(
            url="/api/v1/rooms/create",
            json={
                "room_name": "new-room",
                "room_type": "private",
                "messages_deletable": True
            },
            headers={
                "Authorization": f"Bearer fake"
            }
        )

        assert response2.status_code == 201
        data = response2.json()
        assert data["message"] == "Room already exists"
        assert isinstance(data["data"]["room"], dict)
        assert isinstance(data["data"]["room_members"], list)

    @pytest.mark.asyncio
    async def test_create_public_room_success(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test create public room success.
        """
        mock_johnson_user_dict["id"] = mock_user_id

        _ = await user_service.create(mock_johnson_user_dict, test_get_session)

        response = client.post(
            url="/api/v1/rooms/create",
            json={
                "room_name": "new-room",
                "room_type": "public",
                "messages_deletable": True
            },
            headers={
                "Authorization": f"Bearer fake"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Room Created Successfully"
        assert isinstance(data["data"]["room"], dict)
        assert isinstance(data["data"]["room_members"], list)

    @pytest.mark.asyncio
    async def test_public_room_name_validation_errors(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test create public room_name validation_errors.
        """
        mock_johnson_user_dict["id"] = mock_user_id

        _ = await user_service.create(mock_johnson_user_dict, test_get_session)

        response = client.post(
            url="/api/v1/rooms/create",
            json={
                "room_name": "new room",
                "room_type": "public",
                "messages_deletable": True
            },
            headers={
                "Authorization": f"Bearer fake"
            }
        )

        assert response.status_code == 422
        data = response.json()

        assert data["message"] == 'Validation Error.'
        assert data["data"]["msg"] == 'Value error, Only special characters #-_ are allowed in room_name'

    @pytest.mark.asyncio
    async def test_public_room_type_validation_errors(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test create public room_type validation_errors.
        """
        mock_johnson_user_dict["id"] = mock_user_id

        _ = await user_service.create(mock_johnson_user_dict, test_get_session)

        response = client.post(
            url="/api/v1/rooms/create",
            json={
                "room_name": "new-room",
                "room_type": "direct",
                "messages_deletable": True
            },
            headers={
                "Authorization": f"Bearer fake"
            }
        )

        assert response.status_code == 422
        data = response.json()

        assert data["message"] == 'Validation Error.'
        assert data["data"]["msg"] == 'Value error, room_type must be either public or private'

    @pytest.mark.asyncio
    async def test_missing_room_type_errors(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test missing room_type validation_errors.
        """
        mock_johnson_user_dict["id"] = mock_user_id

        _ = await user_service.create(mock_johnson_user_dict, test_get_session)

        response = client.post(
            url="/api/v1/rooms/create",
            json={
                "room_name": "new-room",
                "messages_deletable": True
            },
            headers={
                "Authorization": f"Bearer fake"
            }
        )

        assert response.status_code == 422
        data = response.json()

        assert data["message"] == 'Validation Error.'
        assert data["data"]["msg"] == 'Value error, room_type must be either public or private'

    @pytest.mark.asyncio
    async def test_missing_room_name_errors(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test missing room_name validation_errors.
        """
        mock_johnson_user_dict["id"] = mock_user_id

        _ = await user_service.create(mock_johnson_user_dict, test_get_session)

        response = client.post(
            url="/api/v1/rooms/create",
            json={
                "room_type": "private",
                "room_name": "",
                "messages_deletable": True
            },
            headers={
                "Authorization": f"Bearer fake"
            }
        )

        assert response.status_code == 422
        data = response.json()

        assert data["message"] == 'Validation Error.'
        assert data["data"]["msg"] == 'Value error, room_name cannot bu null'

    @pytest.mark.asyncio
    async def test_missing_messages_deletable_errors(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test missing messages_deletable validation_errors.
        """
        mock_johnson_user_dict["id"] = mock_user_id

        _ = await user_service.create(mock_johnson_user_dict, test_get_session)

        response = client.post(
            url="/api/v1/rooms/create",
            json={
                "room_type": "public",
                "room_name": "new-room"
            },
            headers={
                "Authorization": f"Bearer fake"
            }
        )

        assert response.status_code == 422
        data = response.json()

        assert data["message"] == 'Validation Error.'
        assert data["data"]["msg"] == 'Value error, messages_deletable must be either true of false'

    @pytest.mark.asyncio
    async def test_get_rooms_route(self,
                                   client,
                                   mock_johnson_user_dict,
                                   mock_user_id,
                                   test_get_session,
                                   test_setup):
        """
        Test get_rooms route.
        """
        mock_johnson_user_dict["id"] = mock_user_id

        _ = await user_service.create(mock_johnson_user_dict, test_get_session)

        response = client.post(
            url="/api/v1/rooms/create",
            json={
                "room_name": "new-room",
                "room_type": "public",
                "messages_deletable": True
            },
            headers={
                "Authorization": f"Bearer fake"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Room Created Successfully"
        assert isinstance(data["data"]["room"], dict)
        assert isinstance(data["data"]["room_members"], list)

        response2 = client.get(
            url="/api/v1/rooms",
            headers={
                "Authorization": "Bearer fake",
            }
        )

        assert response2.status_code == 200

        data2 = response2.json()

        assert data2["message"] == "Rooms Retrieved Successfully"
        assert data2["data"][0] == data["data"]["room"]

    @pytest.mark.asyncio
    async def test_delete_public_room_message_route_success(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_jayson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test delete public room messsage route, admin only.
        Only Admin can delete room messages in a non-deletable-messages-room.
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

        # jayson and johnson creates messages.
        messages = await message_service.create_all(
            [
                {
                    "room_id": new_room.id,
                    "user_id": jayson.id,
                    "content": "Hello johnson",
                    "chat_type": "public",
                },
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


        # assertions
        jayson_message_one = messages[0]
        jayson_message_two = messages[1]
        johnson_message_one = messages[2]
        assert jayson_message_one.user_id == jayson.id
        assert jayson_message_two.user_id == jayson.id
        assert johnson_message_one.user_id == johnson.id

        # admin johnson can delete jayson message
        response3 = client.delete(
            url=f'/api/v1/rooms/{new_room.id}/messages/{jayson_message_one.id}',
            headers={
                "Authorization": "Bearer fake"
            }
        )
        assert response3.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_public_room_message_route_failure_non_admin(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_jayson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test delete public room messsage route failure.
        where another user tries to delete a message in a non deletable-messages-room.
        """
        # create jayson user
        mock_jayson_user_dict["id"] = mock_user_id
        jayson = await user_service.create(
            mock_jayson_user_dict,
            test_get_session
        )
        _ = await profile_service.create(
            {"user_id": jayson.id},
            test_get_session
        )

        # create johnson user
        johnson = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )
        _ = await profile_service.create(
            {"user_id": johnson.id},
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

        # jayson and johnson creates messages.
        messages = await message_service.create_all(
            [
                {
                    "room_id": new_room.id,
                    "user_id": jayson.id,
                    "content": "Hello johnson",
                    "chat_type": "public",
                },
                {
                    "room_id": new_room.id,
                    "user_id": jayson.id,
                    "content": "Hello johnson",
                    "chat_type": "public",
                },
                {
                    "room_id": new_room.id,
                    "user_id": johnson.id,
                    "content": "Hello Jayson",
                    "chat_type": "public",
                }
            ],
            test_get_session
        )

        # assertions
        jayson_message_one = messages[0]
        jayson_message_two = messages[1]
        johnson_message_one = messages[2]
        assert jayson_message_one.user_id == jayson.id
        assert jayson_message_two.user_id == jayson.id
        assert johnson_message_one.user_id == johnson.id

        # non-admin jayson can not delete his own message
        response3 = client.delete(
            url=f'/api/v1/rooms/{new_room.id}/messages/{jayson_message_one.id}',
            headers={
                "Authorization": "Bearer fake"
            }
        )
        assert response3.status_code == 400
        assert response3.json() == {
            'status_code': 400,
            'message': 'User is not allowed to delete the message',
            'data': {}
        }

    @pytest.mark.asyncio
    async def test_delete_public_room_messages_route_success(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_jayson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test delete public room messsages route, admin only.
        Batch delete.
        Only Admin can delete room messages in a non-deletable-messages-room.
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

        # jayson and johnson creates messages.
        messages = await message_service.create_all(
            [
                {
                    "room_id": new_room.id,
                    "user_id": jayson.id,
                    "content": "Hello johnson",
                    "chat_type": "public",
                },
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


        # assertions
        jayson_message_one = messages[0]
        jayson_message_two = messages[1]
        johnson_message_one = messages[2]
        assert jayson_message_one.user_id == jayson.id
        assert jayson_message_two.user_id == jayson.id
        assert johnson_message_one.user_id == johnson.id

        # admin johnson can delete jayson message, and all messages
        response3 = client.request(
            method="DELETE",
            url=f'/api/v1/rooms/{new_room.id}/messages',
            json={
                "message_ids": [1, 2, 3]
            },
            headers={
                "Authorization": "Bearer fake"
            }
        )
        assert response3.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_public_room_messages_route_failure_non_admin(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_jayson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test delete public room messsage route failure.
        Non-admin cannot batch delete in a non-messages-deletable.
        where another user tries to delete messages in a non deletable-messages-room.
        """
        # create jayson user
        mock_jayson_user_dict["id"] = mock_user_id
        jayson = await user_service.create(
            mock_jayson_user_dict,
            test_get_session
        )
        _ = await profile_service.create(
            {"user_id": jayson.id},
            test_get_session
        )

        # create johnson user
        johnson = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )
        _ = await profile_service.create(
            {"user_id": johnson.id},
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

        # jayson and johnson creates messages.
        messages = await message_service.create_all(
            [
                {
                    "room_id": new_room.id,
                    "user_id": jayson.id,
                    "content": "Hello johnson",
                    "chat_type": "public",
                },
                {
                    "room_id": new_room.id,
                    "user_id": jayson.id,
                    "content": "Hello johnson",
                    "chat_type": "public",
                },
                {
                    "room_id": new_room.id,
                    "user_id": johnson.id,
                    "content": "Hello Jayson",
                    "chat_type": "public",
                }
            ],
            test_get_session
        )

        # assertions
        jayson_message_one = messages[0]
        jayson_message_two = messages[1]
        johnson_message_one = messages[2]
        assert jayson_message_one.user_id == jayson.id
        assert jayson_message_two.user_id == jayson.id
        assert johnson_message_one.user_id == johnson.id

        # non-admin jayson can not delete any message
        response3 = client.request(
            method="DELETE",
            url=f'/api/v1/rooms/{new_room.id}/messages',
            json={
                "message_ids": [1, 2, 3]
            },
            headers={
                "Authorization": "Bearer fake"
            }
        )
        assert response3.status_code == 400
        assert response3.json() == {
            'status_code': 400,
            'message': 'User is not allowed to delete the message',
            'data': {}
        }

    @pytest.mark.asyncio
    async def test_update_room_fields_route(self,
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

        print("new_room: ", new_room.id)
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

    @pytest.mark.asyncio
    async def test_delete_room_route(self,
                                   client,
                                   mock_johnson_user_dict,
                                   mock_user_id,
                                   test_get_session,
                                   test_setup):
        """
        Test get_rooms route.
        """
        mock_johnson_user_dict["id"] = mock_user_id

        _ = await user_service.create(mock_johnson_user_dict, test_get_session)

        response = client.post(
            url="/api/v1/rooms/create",
            json={
                "room_name": "new-room",
                "room_type": "public",
                "messages_deletable": True
            },
            headers={
                "Authorization": f"Bearer fake"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Room Created Successfully"
        assert isinstance(data["data"]["room"], dict)
        assert isinstance(data["data"]["room_members"], list)

        response2 = client.get(
            url="/api/v1/rooms",
            headers={
                "Authorization": "Bearer fake",
            }
        )

        assert response2.status_code == 200

        data2 = response2.json()

        assert data2["message"] == "Rooms Retrieved Successfully"
        assert data2["data"][0] == data["data"]["room"]

        response3 = client.delete(
            url=f'/api/v1/rooms/{data["data"]["room"]["id"]}',
            headers={
                "Authorization": "Bearer fake",
            }
        )

        assert response3.status_code == 204

        response4 = client.get(
            url="/api/v1/rooms",
            headers={
                "Authorization": "Bearer fake",
            }
        )

        assert response4.status_code == 200

        data4 = response4.json()

        assert data4["data"] == []

    @pytest.mark.asyncio
    async def test_update_room_messages_route_success(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test update room messsages route.
        """
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

        new_room, _, _ =await room_service.create_a_public_or_private_room(
            room_name="public-room-name",
            creator_id=johnson.id,
            session=test_get_session,
            messages_deletable=False,
            room_type="public"
        )

        message = await message_service.create(
            {
                "room_id": new_room.id,
                "user_id": mock_johnson_user_dict["id"],
                "content": "Hello Jayson",
                "chat_type": "public",
            },
            test_get_session
        )

        response = client.patch(
            url=f'/api/v1/rooms/{new_room.id}/messages/{message.id}',
            json={
                "message": "updated message."
            },
            headers={
                "Authorization": "Bearer fake"
            }
        )
        assert response.status_code == 200

        data = response.json()

        assert data["message"] == "Message updated successfully."
        assert data["data"]["content"] == "updated message."

    @pytest.mark.asyncio
    async def test_update_room_messages_route_unsuccess(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_jayson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test update room message route unsuccessfull by another user..
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

        new_room, _, _ =await room_service.create_a_public_or_private_room(
            room_name="public-room-name",
            creator_id=jayson.id,
            session=test_get_session,
            messages_deletable=False,
            room_type="public"
        )

        message = await message_service.create(
            {
                "room_id": new_room.id,
                "user_id": jayson.id,
                "content": "Hello Jayson",
                "chat_type": "public",
            },
            test_get_session
        )

        response = client.patch(
            url=f'/api/v1/rooms/{new_room.id}/messages/{message.id}',
            json={
                "message": "johnson is updating..."
            },
            headers={
                "Authorization": "Bearer fake"
            }
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_update_room_messages_route_validation(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test update room messages route validation.
        """
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

        new_room, _, _ =await room_service.create_a_public_or_private_room(
            room_name="public-room-name",
            creator_id=johnson.id,
            session=test_get_session,
            messages_deletable=False,
            room_type="public"
        )

        message = await message_service.create(
            {
                "room_id": new_room.id,
                "user_id": mock_johnson_user_dict["id"],
                "content": "Hello Jayson",
                "chat_type": "public",
            },
            test_get_session
        )

        response3 = client.patch(
            url=f'/api/v1/rooms/{new_room.id}/messages/{message.id}',
            json={
                "message": ""
            },
            headers={
                "Authorization": "Bearer fake"
            }
        )
        assert response3.status_code == 422

        response3 = client.patch(
            url=f'/api/v1/rooms/{new_room.id}/messages/{message.id}',
            json={
                "message": " "
            },
            headers={
                "Authorization": "Bearer fake"
            }
        )
        assert response3.status_code == 422

        response3 = client.patch(
            url=f'/api/v1/rooms/{new_room.id}/messages/{message.id}',
            json={
                "message": "."
            },
            headers={
                "Authorization": "Bearer fake"
            }
        )
        assert response3.status_code == 200


class TestCreateDirectMessageRoomRoute:
    """
    Test class for create direct-message room route
    """

    @pytest.mark.asyncio
    async def test_create_direct_message_room_success(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_jayson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test create direct messsage room success.
        """
        jayson_response = client.post(
            url="/api/v1/auth/register",
            json=mock_jayson_user_dict
        )

        assert jayson_response.status_code == 201
        jayson_id = jayson_response.json()["data"]["user"]["id"]

        mock_johnson_user_dict["id"] = mock_user_id

        johnson_user = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )

        response = client.post(
            url="/api/v1/rooms/create/dm",
            json={
                "receiver_id": jayson_id,
            },
            headers={
                "Authorization": "Bearer none"
            }
        )

        assert response.status_code == 201

        data = response.json()

        assert data["status_code"] == 201
        assert data["message"] == "Room Created Successfully"
        assert isinstance(data["data"]["room"], dict)
        assert isinstance(data["data"]["room_members"], list)

    @pytest.mark.asyncio
    async def test_create_direct_message_room_idempotency(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_jayson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test create direct messsage room idempotency success.
        """
        jayson_response = client.post(
            url="/api/v1/auth/register",
            json=mock_jayson_user_dict
        )

        assert jayson_response.status_code == 201
        jayson_id = jayson_response.json()["data"]["user"]["id"]

        mock_johnson_user_dict["id"] = mock_user_id

        _ = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )

        response = client.post(
            url="/api/v1/rooms/create/dm",
            json={
                "receiver_id": jayson_id,
            },
            headers={
                "Authorization": "Bearer none"
            }
        )

        assert response.status_code == 201

        data = response.json()

        assert data["status_code"] == 201
        assert data["message"] == "Room Created Successfully"
        assert isinstance(data["data"]["room"], dict)
        assert isinstance(data["data"]["room_members"], list)

        response2 = client.post(
            url="/api/v1/rooms/create/dm",
            json={
                "receiver_id": jayson_id,
            },
            headers={
                "Authorization": "Bearer none"
            }
        )

        assert response2.status_code == 201

        data = response2.json()

        assert data["status_code"] == 201
        assert data["message"] == "Room already exists"
        assert isinstance(data["data"]["room"], dict)
        assert isinstance(data["data"]["room_members"], list)

    @pytest.mark.asyncio
    async def test_raise_UserNotFoundError(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test User not found error..
        """
        mock_johnson_user_dict["id"] = mock_user_id

        johnson_user = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )

        response = client.post(
            url="/api/v1/rooms/create/dm",
            json={
                "receiver_id": johnson_user.id,
            },
            headers={
                "Authorization": "Bearer none"
            }
        )

        assert response.status_code == 400

        data = response.json()

        assert data["status_code"] == 400
        assert data["message"] == f"User {johnson_user.id} and User {johnson_user.id} cannot be the same"

    @pytest.mark.asyncio
    async def test_raise_UserNotFoundError2(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test User not found error2..
        """
        mock_johnson_user_dict["id"] = mock_user_id

        _ = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )

        response = client.post(
            url="/api/v1/rooms/create/dm",
            json={
                "receiver_id": "fake_id",
            },
            headers={
                "Authorization": "Bearer none"
            }
        )

        assert response.status_code == 400

        data = response.json()

        assert data["status_code"] == 400
        assert data["message"] == "User fake_id does not exists"

    @pytest.mark.asyncio
    async def test_create_dm_validation_error(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test create dm validation error..
        """
        mock_johnson_user_dict["id"] = mock_user_id

        _ = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )

        response = client.post(
            url="/api/v1/rooms/create/dm",
            json={
                "receiver_id": "",
            },
            headers={
                "Authorization": "Bearer none"
            }
        )

        assert response.status_code == 422

        data = response.json()

        assert data["status_code"] == 422
        assert data["message"] == "Validation Error."
        assert data["data"]["msg"] == "Value error, receiver_id cannot be null"

    @pytest.mark.asyncio
    async def test_get_direct_message_room_route(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_jayson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test get direct messsage room route.
        """
        jayson_response = client.post(
            url="/api/v1/auth/register",
            json=mock_jayson_user_dict
        )

        assert jayson_response.status_code == 201
        jayson_id = jayson_response.json()["data"]["user"]["id"]

        mock_johnson_user_dict["id"] = mock_user_id

        _ = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )

        response = client.post(
            url="/api/v1/rooms/create/dm",
            json={
                "receiver_id": jayson_id,
            },
            headers={
                "Authorization": "Bearer none"
            }
        )

        assert response.status_code == 201

        data = response.json()

        assert data["status_code"] == 201
        assert data["message"] == "Room Created Successfully"
        assert isinstance(data["data"]["room"], dict)
        assert isinstance(data["data"]["room_members"], list)

        response2 = client.get(
            url="/api/v1/rooms/dm",
            headers={
                "Authorization": "Bearer fake"
            },
        )

        assert response2.status_code == 200

        data2 = response2.json()

        assert data2["message"] == "Rooms Retrieved Successfully"
        assert data2["data"][0]["username"] == mock_jayson_user_dict["username"]

    @pytest.mark.asyncio
    async def test_get_room_messages_route(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_jayson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test get room messsages route.
        """
        jayson_response = client.post(
            url="/api/v1/auth/register",
            json=mock_jayson_user_dict
        )

        assert jayson_response.status_code == 201
        jayson_id = jayson_response.json()["data"]["user"]["id"]

        mock_johnson_user_dict["id"] = mock_user_id

        _ = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )
        _ = await profile_service.create(
            {"user_id": mock_user_id},
            test_get_session
        )

        response = client.post(
            url="/api/v1/rooms/create/dm",
            json={
                "receiver_id": jayson_id,
            },
            headers={
                "Authorization": "Bearer none"
            }
        )

        assert response.status_code == 201

        data = response.json()

        assert data["status_code"] == 201
        assert data["message"] == "Room Created Successfully"
        assert isinstance(data["data"]["room"], dict)
        assert isinstance(data["data"]["room_members"], list)

        messages = await message_service.create_all(
            [
                {
                    "room_id": data["data"]["room"]["id"],
                    "user_id": jayson_id,
                    "content": "Hello johnson",
                    "chat_type": "direct_message",
                },
                {
                    "room_id": data["data"]["room"]["id"],
                    "user_id": mock_johnson_user_dict["id"],
                    "content": "Hello Jayson",
                    "chat_type": "direct_message",
                }
            ],
            test_get_session
        )

        response2 = client.get(
           url=f'/api/v1/rooms/{data["data"]["room"]["id"]}/messages',
           headers={
               "Authorization": "Bearer fake"
            }
        )

        assert response2.status_code == 200

        data = response2.json()

        assert data["message"] == "Messages Retrieved Successfully"
        assert data["data"][0]["content"] == messages[0].content
        assert data["data"][0]["username"] == "jayson"
        assert data["data"][0]["room_id"] == messages[1].room_id
        assert data["data"][1]["content"] == messages[1].content
        assert data["data"][1]["username"] == "johnson"
        assert data["data"][1]["room_id"] == messages[1].room_id

    @pytest.mark.asyncio
    async def test_delete_room_message_route_success(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_jayson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test delete direct-message room messsage route.
        """
        # create user jayson
        jayson = await user_service.create(
            mock_jayson_user_dict,
            test_get_session
        )
        _ = await profile_service.create(
            {"user_id": jayson.id},
            test_get_session
        )

        # create user johnson
        mock_johnson_user_dict["id"] = mock_user_id

        johnson = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )
        _ = await profile_service.create(
            {"user_id": mock_user_id},
            test_get_session
        )

        # user johnson creates room
        new_room, _, _ = await room_service.create_direct_message_room(
            user_id_1=johnson.id,
            user_id_2=jayson.id,
            session=test_get_session
        )

        # both users create messages
        messages = await message_service.create_all(
            [
                {
                    "room_id": new_room.id,
                    "user_id": jayson.id,
                    "content": "Hello johnson",
                    "chat_type": "direct_message",
                },
                {
                    "room_id": new_room.id,
                    "user_id": johnson.id,
                    "content": "Hello Jayson",
                    "chat_type": "direct_message",
                }
            ],
            test_get_session
        )

        # johnson makes request and deletes his own message.
        response = client.delete(
            url=f'/api/v1/rooms/{new_room.id}/messages/{messages[1].id}',
            headers={
                "Authorization": "Bearer fake"
            }
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_room_message_route_failure(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_jayson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test delete direct-message room messsage route failure.
        where another user tries to delete another user message in a direct-message.
        """
        jayson = await user_service.create(
            mock_jayson_user_dict,
            test_get_session
        )
        _ = await profile_service.create(
            {"user_id": jayson.id},
            test_get_session
        )

        mock_johnson_user_dict["id"] = mock_user_id

        johnson = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )
        _ = await profile_service.create(
            {"user_id": mock_user_id},
            test_get_session
        )

        new_room, _, _ = await room_service.create_direct_message_room(
            user_id_1=johnson.id,
            user_id_2=jayson.id,
            session=test_get_session
        )


        messages = await message_service.create_all(
            [
                {
                    "room_id": new_room.id,
                    "user_id": jayson.id,
                    "content": "Hello johnson",
                    "chat_type": "direct_message",
                },
                {
                    "room_id": new_room.id,
                    "user_id": johnson.id,
                    "content": "Hello Jayson",
                    "chat_type": "direct_message",
                }
            ],
            test_get_session
        )

        assert messages[1].user_id == johnson.id

        # johnson makes a request to delete jayson message.
        response3 = client.delete(
            url=f'/api/v1/rooms/{new_room.id}/messages/{messages[0].id}',
            headers={
                "Authorization": "Bearer fake"
            }
        )
        assert response3.status_code == 400

    @pytest.mark.asyncio
    async def test_delete_room_messages_route_success(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_jayson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test delete directm-message room messsages route.
        for batch messages.
        """
        jayson = await user_service.create(
            mock_jayson_user_dict,
            test_get_session
        )
        _ = await profile_service.create(
            {"user_id": jayson.id},
            test_get_session
        )

        mock_johnson_user_dict["id"] = mock_user_id

        johnson = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )
        _ = await profile_service.create(
            {"user_id": mock_user_id},
            test_get_session
        )

        new_room, _, _ = await room_service.create_direct_message_room(
            user_id_1=johnson.id,
            user_id_2=jayson.id,
            session=test_get_session
        )

        messages = await message_service.create_all(
            [
                {
                    "room_id": new_room.id,
                    "user_id": jayson.id,
                    "content": "Hello johnson",
                    "chat_type": "direct_message",
                },
                {
                    "room_id": new_room.id,
                    "user_id": johnson.id,
                    "content": "Hello Jayson",
                    "chat_type": "direct_message",
                },
                {
                    "room_id": new_room.id,
                    "user_id": johnson.id,
                    "content": "How are you?",
                    "chat_type": "direct_message",
                }
            ],
            test_get_session
        )

        # johnson makes a request and batch deletes his two messages.
        response3 = client.request(
            method="DELETE",
            url=f'/api/v1/rooms/{new_room.id}/messages',
            json={
                "message_ids": [2, 3]
            },
            headers={
                "Authorization": "Bearer fake"
            }
        )
        assert response3.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_room_messages_route_failure(self,
                                               client,
                                               mock_johnson_user_dict,
                                               mock_jayson_user_dict,
                                               mock_user_id,
                                               test_get_session,
                                               test_setup):
        """
        Test delete directm-message room messsages route failure.
        where another user tries to delete another user message in a direct-message.
        """
        jayson = await user_service.create(
            mock_jayson_user_dict,
            test_get_session
        )
        _ = await profile_service.create(
            {"user_id": jayson.id},
            test_get_session
        )

        mock_johnson_user_dict["id"] = mock_user_id

        johnson = await user_service.create(
            mock_johnson_user_dict,
            test_get_session
        )
        _ = await profile_service.create(
            {"user_id": mock_user_id},
            test_get_session
        )

        new_room, _, _ = await room_service.create_direct_message_room(
            user_id_1=johnson.id,
            user_id_2=jayson.id,
            session=test_get_session
        )

        messages = await message_service.create_all(
            [
                {
                    "room_id": new_room.id,
                    "user_id": jayson.id,
                    "content": "Hello johnson",
                    "chat_type": "direct_message",
                },
                {
                    "room_id": new_room.id,
                    "user_id": johnson.id,
                    "content": "Hello Jayson",
                    "chat_type": "direct_message",
                },
                {
                    "room_id": new_room.id,
                    "user_id": johnson.id,
                    "content": "How are you?",
                    "chat_type": "direct_message",
                }
            ],
            test_get_session
        )

        # johnson makes a request tries to batch delete jayson message.
        response3 = client.request(
            method="DELETE",
            url=f'/api/v1/rooms/{new_room.id}/messages',
            json={
                "message_ids": [1]
            },
            headers={
                "Authorization": "Bearer fake"
            }
        )
        assert response3.status_code == 400
