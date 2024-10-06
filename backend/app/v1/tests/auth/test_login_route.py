import pytest


class TestLoginRoute:
    """
    Test class for login route
    """
    async def test_successful_login(self,
                                    client,
                                    mock_jayson_user_dict,
                                    test_setup):
        """
        Test for successful user login.
        """
        url = "/api/v1/auth"
        client.post(
            url=f"{url}/register",
            json=mock_jayson_user_dict
        )

        response = client.post(
            url=f"{url}/login",
            json={
                "username": mock_jayson_user_dict["username"],
                "password": mock_jayson_user_dict["password"]
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["message"] == "Login Successful"
        assert data["status_code"] == 200

    async def test_unsuccessful_login(self,
                                    client,
                                    test_setup):
        """
        Test for un-successful user login.
        """
        url = "/api/v1/auth"

        response = client.post(
            url=f"{url}/login",
            json={
                "username": "johnson",
                "password": "MypassWord1234@"
            }
        )

        assert response.status_code == 404
        data = response.json()

        assert data["message"] == "Invalid username/email or password"
        assert data["status_code"] == 404

