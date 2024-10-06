import pytest

from app.v1.users.services import user_service, UserMeOut
from app.v1.profile.services import profile_service


class TestUserService:
    """
    Test class for user_service
    """
    async def test_create(self,
                          mock_jayson_user_dict,
                          test_get_session,
                          test_setup):
        """
        Test create user.
        """
        new_user = await user_service.create(mock_jayson_user_dict, test_get_session)

        assert new_user.first_name == mock_jayson_user_dict.get("first_name")

    async def test_fetch(self,
                          mock_jayson_user_dict,
                          test_get_session,
                          test_setup):
        """
        Test fetch user.
        """
        new_user = await user_service.create(mock_jayson_user_dict, test_get_session)

        fetched_user = await user_service.fetch({"email": new_user.email}, test_get_session)

        assert fetched_user.email == new_user.email

    async def test_fetch_all(self,
                          mock_jayson_user_dict,
                          mock_johnson_user_dict,
                          test_get_session,
                          test_setup):
        """
        Test fetch all users.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)

        users = [jayson, johnson]

        fetched_users = await user_service.fetch_all({}, test_get_session)

        assert fetched_users[0] == users[0]
        assert fetched_users[1] == users[1]

    async def test_delete(self,
                          mock_jayson_user_dict,
                          test_get_session,
                          test_setup):
        """
        Test delete user.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)

        fetched_user = await user_service.fetch({"id": jayson.id}, test_get_session)

        assert fetched_user == jayson

        await user_service.delete({"id": jayson.id}, test_get_session)

        fetched_user2 = await user_service.fetch({"id": jayson.id}, test_get_session)

        assert fetched_user2 == None

    async def test_delete_all(self,
                            mock_jayson_user_dict,
                            mock_johnson_user_dict,
                            test_get_session,
                            test_setup):
        """
        Test delete all users.
        """
        jayson = await user_service.create(mock_jayson_user_dict, test_get_session)
        johnson = await user_service.create(mock_johnson_user_dict, test_get_session)

        users = [jayson, johnson]

        fetched_users = await user_service.fetch_all({}, test_get_session)

        assert fetched_users == users

        await user_service.delete_all(test_get_session)

        fetched_users = await user_service.fetch_all({}, test_get_session)

        assert fetched_users == []

    @pytest.mark.asyncio
    async def test_update(self,
                          mock_johnson_user_dict,
                          test_get_session,
                          test_setup):
        """
        Test profile_service.update.
        """
        new_user = await user_service.create(mock_johnson_user_dict, test_get_session)

        await user_service.update([{"id": new_user.id}, {"last_name": "King"}], test_get_session)

        assert new_user.last_name == "King"
        assert new_user.last_name != mock_johnson_user_dict["last_name"]

    async def test_fetch_by_email_or_user_name(self,
                          mock_jayson_user_dict,
                          test_get_session,
                          test_setup):
        """
        Test fetch user by email or username.
        """
        new_user = await user_service.create(mock_jayson_user_dict, test_get_session)

        fetched_user_email = await user_service.fetch_by_email_or_user_name(
            {"email": new_user.email, "username": "fake"},
            test_get_session
        )

        fetched_user_username = await user_service.fetch_by_email_or_user_name(
            {"email": "fake", "username": new_user.username},
            test_get_session
        )

        assert fetched_user_email.email == new_user.email

        assert fetched_user_username.username == new_user.username

    async def test_get_user_profile(self,
                                    mock_johnson_user_dict,
                                    test_get_session,
                                    test_setup):
        """
        Test get user profile
        """
        new_user = await user_service.create(mock_johnson_user_dict, test_get_session)
        await profile_service.create({"user_id": new_user.id}, test_get_session)

        user_profile = await user_service.get_user_profile(new_user, test_get_session)

        assert isinstance(user_profile, UserMeOut)
        assert user_profile.status_code == 200
        assert user_profile.message == "User data retrieved successfuly"
