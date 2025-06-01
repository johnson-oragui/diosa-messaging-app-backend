"""
Register Test module
"""

from httpx import AsyncClient
import pytest

from tests.v1.auth import register_input, delete_user, AsyncSession


class TestRegisterRoute:
    """
    Test class for register route.
    """

    @pytest.mark.asyncio
    async def test_a_register(
        self, client: AsyncClient, test_setup: None, test_get_session: AsyncSession
    ):
        """
        Test successful register user route
        """
        response = await client.post(url="/api/v1/auth/register", json=register_input)

        assert response.status_code == 201

        data: dict = response.json()

        assert data["status_code"] == 201
        assert data["message"] == "User Registered Successfully"
        assert data.get("data", {})["email"] == "jayson@gtest.com"

        response = await client.post(url="/api/v1/auth/register", json=register_input)

        assert response.status_code == 201

        data: dict = response.json()

        assert data["status_code"] == 201
        assert data["message"] == "User already Registered"
        assert data.get("data", {})["email"] == "jayson@gtest.com"

        await delete_user(test_get_session, "jayson@gtest.com")

    @pytest.mark.asyncio
    async def test_b_missing_email(self, client: AsyncClient):
        """
        Test missing email in user registration
        """
        register_input["email"] = None  # type: ignore
        response = await client.post(url="/api/v1/auth/register", json=register_input)

        assert response.status_code == 422

        data: dict = response.json()

        assert data["status_code"] == 422
        assert data["message"] == "Validation Error."
        assert data["data"]["msg"].endswith(" email must be provided")

    @pytest.mark.asyncio
    async def test_c_missing_password(self, client: AsyncClient):
        """
        Test missing password in user registration
        """
        register_input["password"] = None  # type: ignore
        response = await client.post(url="/api/v1/auth/register", json=register_input)

        assert response.status_code == 422

        data: dict = response.json()

        assert data["status_code"] == 422
        assert data["message"] == "Validation Error."
        assert data["data"]["msg"].endswith(" password must be provided")

    @pytest.mark.asyncio
    async def test_d_missing_confirm_password(self, client: AsyncClient):
        """
        Test missing confirm password in user registration
        """
        register_input["confirm_password"] = None  # type: ignore
        register_input["password"] = "Jayson1234#"
        response = await client.post(url="/api/v1/auth/register", json=register_input)

        assert response.status_code == 422

        data: dict = response.json()

        assert data["status_code"] == 422
        assert data["message"] == "Validation Error."
        assert data["data"]["msg"].endswith(" Passwords must match")

    @pytest.mark.asyncio
    async def test_e_not_matching_passwords(self, client: AsyncClient):
        """
        Test not matching paswords
        """
        register_input["confirm_password"] = "notmath"
        register_input["password"] = "Jayson1234#"

        response = await client.post(url="/api/v1/auth/register", json=register_input)

        assert response.status_code == 422

        data: dict = response.json()

        assert data["status_code"] == 422
        assert data["message"] == "Validation Error."
        assert data["data"]["msg"].endswith(" Passwords must match")

    @pytest.mark.asyncio
    async def test_f_missing_idempotency_key(self, client: AsyncClient):
        """
        Test missing idempotency_key in user registration
        """
        register_input["confirm_password"] = "Jayson1234#"
        register_input["idempotency_key"] = None  # type: ignore
        register_input["email"] = "jayson@gtest.com"

        response = await client.post(url="/api/v1/auth/register", json=register_input)

        assert response.status_code == 422

        data: dict = response.json()

        assert data["status_code"] == 422
        assert data["message"] == "Validation Error."
        assert data["data"]["msg"].endswith("Input should be a valid string")
