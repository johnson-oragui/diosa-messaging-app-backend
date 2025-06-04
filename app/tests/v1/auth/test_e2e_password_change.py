"""
Password change Test module
"""

from unittest.mock import patch
from httpx import AsyncClient
import pytest

from tests.v1.auth import password_change_register_input


class TestPasswordChange:
    """
    Test class for password change route.
    """

    @pytest.mark.asyncio
    async def test_a_when_old_and_new_password_match_returns_422(
        self, client: AsyncClient, test_setup: None
    ):
        """
        Test when old and new password match
        """
        login_payload = {
            "password": password_change_register_input.get("password"),
            "email": password_change_register_input.get("email"),
            "session_id": "0000000000x0-0000-0100-0000-01011001",
        }
        # register
        with patch(
            "app.service.v1.authentication_service.AuthenticationService.send_email",
            return_value=None,
        ):
            with patch(
                "app.service.v1.authentication_service.AuthenticationService.generate_six_digit_code",
                return_value="123456",
            ):
                response = await client.post(
                    url="/api/v1/auth/register", json=password_change_register_input
                )
                assert response.status_code == 201

                await client.post(
                    url="/api/v1/auth/verify-account",
                    json={
                        "email": password_change_register_input.get("email"),
                        "code": "123456",
                    },
                )

        # login
        login_response = await client.post(url="/api/v1/auth/login", json=login_payload)

        assert login_response.status_code == 200

        data: dict = login_response.json()

        # get access token
        access_token = data["data"]["access_token"]["token"]

        password_change_data = {
            "old_password": "Johnson1234#",
            "new_password": "Johnson1234#",
            "confirm_password": "Johnson1234#",
        }
        response = await client.post(
            url="/api/v1/auth/change-password",
            json=password_change_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

        data: dict = response.json()

        assert data["status_code"] == 422
        assert data["message"] == "Validation Error."
        assert (
            data["data"]["msg"]
            == "Value error, new_password and old_password must not be same"
        )

    @pytest.mark.asyncio
    async def test_b_when_confirm_and_new_password_don_not_match_returns_422(
        self, client: AsyncClient, test_setup: None
    ):
        """
        Test when new and confirm password do not match
        """
        login_payload = {
            "password": password_change_register_input.get("password"),
            "email": password_change_register_input.get("email"),
            "session_id": "a00000000000-0000-0100-0000-01011001",
        }
        # register
        with patch(
            "app.service.v1.authentication_service.AuthenticationService.send_email",
            return_value=None,
        ):
            with patch(
                "app.service.v1.authentication_service.AuthenticationService.generate_six_digit_code",
                return_value="123456",
            ):
                response = await client.post(
                    url="/api/v1/auth/register", json=password_change_register_input
                )
                assert response.status_code == 201

                await client.post(
                    url="/api/v1/auth/verify-account",
                    json={
                        "email": password_change_register_input.get("email"),
                        "code": "123456",
                    },
                )

        # login
        login_response = await client.post(url="/api/v1/auth/login", json=login_payload)

        assert login_response.status_code == 200

        data: dict = login_response.json()

        # get access token
        access_token = data["data"]["access_token"]["token"]
        password_change_data = {
            "old_password": "Johnson1234#",
            "new_password": "OldPassword1234$",
            "confirm_password": "OldPassword123$",
        }
        response = await client.post(
            url="/api/v1/auth/change-password",
            json=password_change_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

        data: dict = response.json()

        assert data["status_code"] == 422
        assert data["message"] == "Validation Error."
        assert (
            data["data"]["msg"]
            == "Value error, confirm_password and new_password must match"
        )

    @pytest.mark.asyncio
    async def test_c_when_new_password_has_wrong_regex_returns_422(
        self, client: AsyncClient, test_setup: None
    ):
        """
        Test when new  password does not conform to right regex
        """
        login_payload = {
            "password": password_change_register_input.get("password"),
            "email": password_change_register_input.get("email"),
            "session_id": "00qqq0000q00-0000-0100-0000-01011001",
        }
        # register
        with patch(
            "app.service.v1.authentication_service.AuthenticationService.send_email",
            return_value=None,
        ):
            with patch(
                "app.service.v1.authentication_service.AuthenticationService.generate_six_digit_code",
                return_value="123456",
            ):
                response = await client.post(
                    url="/api/v1/auth/register", json=password_change_register_input
                )
                assert response.status_code == 201

                await client.post(
                    url="/api/v1/auth/verify-account",
                    json={
                        "email": password_change_register_input.get("email"),
                        "code": "123456",
                    },
                )

        # login
        login_response = await client.post(url="/api/v1/auth/login", json=login_payload)

        assert login_response.status_code == 200

        data: dict = login_response.json()

        # get access token
        access_token = data["data"]["access_token"]["token"]
        # no special char
        password_change_data = {
            "old_password": "OldPassword123$",
            "new_password": "OldPassword1234",
            "confirm_password": "OldPassword1234",
        }
        response = await client.post(
            url="/api/v1/auth/change-password",
            json=password_change_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

        data: dict = response.json()

        assert data["status_code"] == 422
        assert data["message"] == "Validation Error."
        assert (
            data["data"]["msg"]
            == "Value error, password must contain at least one of these special characters !@#&-_,."
        )
        # no digit
        password_change_data["new_password"] = "OldPassword$"
        password_change_data["confirm_password"] = "OldPassword$"
        response = await client.post(
            url="/api/v1/auth/change-password",
            json=password_change_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

        data: dict = response.json()

        assert data["status_code"] == 422
        assert data["message"] == "Validation Error."

        # no upper case
        password_change_data["new_password"] = "oldpassword2$"
        password_change_data["confirm_password"] = "oldpassword2$"
        response = await client.post(
            url="/api/v1/auth/change-password",
            json=password_change_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

        data: dict = response.json()

        assert data["status_code"] == 422
        assert data["message"] == "Validation Error."
        # no lower case
        password_change_data["new_password"] = "OLDPASSWR221$"
        password_change_data["confirm_password"] = "OLDPASSWR221$"
        response = await client.post(
            url="/api/v1/auth/change-password",
            json=password_change_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 422

        data: dict = response.json()

        assert data["status_code"] == 422
        assert data["message"] == "Validation Error."

    @pytest.mark.asyncio
    async def test_d_when_incorrect_old_password_returns_400(
        self, client: AsyncClient, test_setup: None
    ):
        """
        Test when incorrect old password
        """
        login_payload = {
            "password": password_change_register_input.get("password"),
            "email": password_change_register_input.get("email"),
            "session_id": "00d000000q00-0000-0100-sss0-01011001",
        }
        # register
        with patch(
            "app.service.v1.authentication_service.AuthenticationService.send_email",
            return_value=None,
        ):
            with patch(
                "app.service.v1.authentication_service.AuthenticationService.generate_six_digit_code",
                return_value="123456",
            ):
                response = await client.post(
                    url="/api/v1/auth/register", json=password_change_register_input
                )
                assert response.status_code == 201

                await client.post(
                    url="/api/v1/auth/verify-account",
                    json={
                        "email": password_change_register_input.get("email"),
                        "code": "123456",
                    },
                )

        # login
        login_response = await client.post(url="/api/v1/auth/login", json=login_payload)

        assert login_response.status_code == 200

        data: dict = login_response.json()

        # get access token
        access_token = data["data"]["access_token"]["token"]
        password_change_data = {
            "old_password": "Johnson1234$",
            "new_password": "Johnson12345#",
            "confirm_password": "Johnson12345#",
        }
        response = await client.post(
            url="/api/v1/auth/change-password",
            json=password_change_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

        data: dict = response.json()

        assert data["status_code"] == 400
        assert data["message"] == "Invalid credentials"

    @pytest.mark.asyncio
    async def test_e_when_successful_password_change_returns_200(
        self, client: AsyncClient, test_setup: None
    ):
        """
        Test when successful password change
        """
        login_payload = {
            "password": password_change_register_input.get("password"),
            "email": password_change_register_input.get("email"),
            "session_id": "00d000#00q00-0000-0100-0000-01011zzz1",
        }
        # register
        with patch(
            "app.service.v1.authentication_service.AuthenticationService.send_email",
            return_value=None,
        ):
            with patch(
                "app.service.v1.authentication_service.AuthenticationService.generate_six_digit_code",
                return_value="123456",
            ):
                response = await client.post(
                    url="/api/v1/auth/register", json=password_change_register_input
                )
                assert response.status_code == 201

                await client.post(
                    url="/api/v1/auth/verify-account",
                    json={
                        "email": password_change_register_input.get("email"),
                        "code": "123456",
                    },
                )

        # login
        login_response = await client.post(url="/api/v1/auth/login", json=login_payload)

        assert login_response.status_code == 200

        data: dict = login_response.json()

        # get access token
        access_token = data["data"]["access_token"]["token"]
        password_change_data = {
            "old_password": "Johnson1234#",
            "new_password": "Johnson12345#",
            "confirm_password": "Johnson12345#",
        }
        response = await client.post(
            url="/api/v1/auth/change-password",
            json=password_change_data,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        data: dict = response.json()

        assert data["status_code"] == 200
        assert data["message"] == "Password update successful"
