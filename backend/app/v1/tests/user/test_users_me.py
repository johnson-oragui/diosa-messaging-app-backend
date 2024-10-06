from app.v1.users.services import user_service
from app.v1.profile.services import profile_service
from app.utils.task_logger import create_logger

logger = create_logger("TestUserRoute")

class TestUserRoute:
    """
    Test class for user route
    """
    async def test_users_me_route(self,
                                  client,
                                  mock_user_id,
                                  mock_check_for_access_token,
                                  mock_johnson_user_dict,
                                  test_get_session,
                                  test_setup):
        """
        Test successful user-profile retrieval.
        """
        mock_johnson_user_dict["id"] = mock_user_id

        new_user = await user_service.create(mock_johnson_user_dict, test_get_session)
        new_profile = await profile_service.create({"user_id": new_user.id}, test_get_session)

        response = client.get(
            url="/api/v1/users/me",
            headers={
                "Authorization": f"Bearer {mock_check_for_access_token}"
            }
        )
        data: dict = response.json()
        print("response: ", response.json())

        assert response.status_code == 200
        assert data["status_code"] == 200
        assert data["data"]["user"]["id"] == new_user.id
        assert data["data"]["profile"]["id"] == new_profile.id

    async def test_users_me_route_without_token(self,
                                  client,
                                  mock_user_id,
                                  mock_johnson_user_dict,
                                  test_get_session,
                                  test_setup):
        """
        Test unsuccessfull user-profile retrieval.
        """
        mock_johnson_user_dict["id"] = mock_user_id

        await user_service.create(mock_johnson_user_dict, test_get_session)

        response = client.get(
            url="/api/v1/users/me",
        )
        data: dict = response.json()
        print("response: ", response.json())

        assert response.status_code == 401
        assert data["status_code"] == 401
        assert data["message"] == "Unauthorized"
        
