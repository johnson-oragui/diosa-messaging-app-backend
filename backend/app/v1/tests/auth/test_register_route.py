import pytest

class TestRegisterRoute:
    """
    Test class for register route.
    """
    @pytest.mark.asyncio
    async def test_register(self,
                            client,
                            mock_johnson_user_dict,
                            test_setup):
        """
        Test successful register user route
        """
        mock_johnson_user_dict["confirm_password"] = mock_johnson_user_dict["password"]
        response = client.post(
            url="/api/v1/auth/register",
            json=mock_johnson_user_dict
        )

        assert response.status_code == 201

        data = response.json()

        assert data["status_code"] == 201
        assert data["message"] == "User Registered Successfully"
        assert "data" in data
        assert "user" in data["data"]
        assert "profile" in data["data"]

    @pytest.mark.asyncio
    async def test_register_idempotency(self,
                            client,
                            mock_johnson_user_dict,
                            test_setup):
        """
        Test register user route idempotency.
        """
        mock_johnson_user_dict["confirm_password"] = mock_johnson_user_dict["password"]
        response = client.post(
            url="/api/v1/auth/register",
            json=mock_johnson_user_dict
        )

        assert response.status_code == 201

        data = response.json()

        assert data["status_code"] == 201
        assert data["message"] == "User Registered Successfully"
        assert "data" in data
        assert "user" in data["data"]
        assert "profile" in data["data"]

        response2 = client.post(
            url="/api/v1/auth/register",
            json=mock_johnson_user_dict
        )

        assert response2.status_code == 201

        data2 = response2.json()

        assert data2["status_code"] == 201
        assert data2["message"] == "User Already Registered"
        assert "data" in data2
        assert "user" in data2["data"]
        assert "profile" in data2["data"]

    @pytest.mark.asyncio
    async def test_missing_email(self,
                                 client):
        """
        Test missing email in user registration
        """
        user_input = {
            "username": "username",
            "first_name": "Johnson",
            "last_name": "Johnson",
            "password": "Johnson1234#",
            "confirm_password": "Johnson1234#",
            "idempotency_key": "1234567890"
        }

        response = client.post(
            url="/api/v1/auth/register",
            json=user_input
        )

        assert response.status_code == 422

        data = response.json()
        print("data: ", data["data"])

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            'type': 'value_error',
            'loc': ['body'],
            'msg': 'Value error, email must be provided',
            'input': {
                'username': 'username',
                'first_name': 'Johnson',
                'last_name': 'Johnson',
                'password': 'Johnson1234#',
                'confirm_password': 'Johnson1234#',
                'idempotency_key': '1234567890'
            },
            'ctx': {
                'error': {}
            }
        }
    @pytest.mark.asyncio
    async def test_missing_username(self,
                                 client):
        """
        Test missing username in user registration
        """
        user_input = {
            "email": "johnson@gmail.com",
            "first_name": "Johnson",
            "last_name": "Johnson",
            "password": "Johnson1234#",
            "confirm_password": "Johnson1234#",
            "idempotency_key": "1234567890"
        }

        response = client.post(
            url="/api/v1/auth/register",
            json=user_input
        )

        assert response.status_code == 422

        data = response.json()
        print("data: ", data["data"])

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            'type': 'string_too_short',
            'loc': ['body', 'username'],
            'msg': 'String should have at least 3 characters',
            'input': '',
            'ctx': {
                'min_length': 3
            }
        }

    @pytest.mark.asyncio
    async def test_missing_first_name(self,
                                 client):
        """
        Test missing first_name in user registration
        """
        user_input = {
            "username": "username",
            "email": "Johnson@gmail.com",
            "last_name": "Johnson",
            "password": "Johnson1234#",
            "confirm_password": "Johnson1234#",
            "idempotency_key": "1234567890"
        }

        response = client.post(
            url="/api/v1/auth/register",
            json=user_input
        )

        assert response.status_code == 422

        data = response.json()
        print("data: ", data["data"])

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            'type': 'string_too_short',
            'loc': ['body', 'first_name'],
            'msg': 'String should have at least 3 characters',
            'input': '',
            'ctx': {
                'min_length': 3
            }
        }

    @pytest.mark.asyncio
    async def test_missing_last_name(self,
                                 client):
        """
        Test missing last_name in user registration
        """
        user_input = {
            "username": "username",
            "first_name": "Johnson",
            "email": "Johnson@gmail.com",
            "password": "Johnson1234#",
            "confirm_password": "Johnson1234#",
            "idempotency_key": "1234567890"
        }

        response = client.post(
            url="/api/v1/auth/register",
            json=user_input
        )

        assert response.status_code == 422

        data = response.json()
        print("data: ", data["data"])

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            'type': 'string_too_short',
            'loc': ['body', 'last_name'],
            'msg': 'String should have at least 3 characters',
            'input': '',
            'ctx': {
                'min_length': 3
            }
        }

    @pytest.mark.asyncio
    async def test_missing_password(self,
                                 client):
        """
        Test missing password in user registration
        """
        user_input = {
            "username": "username",
            "first_name": "Johnson",
            "last_name": "Johnson",
            "email": "Johnson@gmail.com",
            "confirm_password": "Johnson1234#",
            "idempotency_key": "1234567890"
        }

        response = client.post(
            url="/api/v1/auth/register",
            json=user_input
        )

        assert response.status_code == 422

        data = response.json()
        print("data: ", data["data"])

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            'type': 'value_error',
            'loc': ['body'],
            'msg': 'Value error, Passwords must match',
            'input': {
                'username': 'username',
                'first_name': 'Johnson',
                'last_name': 'Johnson',
                'email': 'Johnson@gmail.com',
                'confirm_password': 'Johnson1234#',
                'idempotency_key': '1234567890'
            },
            'ctx': {
                'error': {}
                }
        }

    @pytest.mark.asyncio
    async def test_missing_confirm_password(self,
                                 client):
        """
        Test missing confirm_password in user registration
        """
        user_input = {
            "username": "username",
            "first_name": "Johnson",
            "last_name": "Johnson",
            "email": "Johnson@gmail.com",
            "email": "Johnson@gmail.com",
            "idempotency_key": "1234567890"
        }

        response = client.post(
            url="/api/v1/auth/register",
            json=user_input
        )

        assert response.status_code == 422

        data = response.json()
        print("data: ", data["data"])

        assert data["message"] == "Validation Error."
        assert data["data"] == {
            'type': 'value_error',
            'loc': ['body'],
            'msg': 'Value error,  must contain at least one lowercase letter',
            'input': {
                'username': 'username',
                'first_name': 'Johnson',
                'last_name': 'Johnson',
                'email': 'Johnson@gmail.com',
                'idempotency_key': '1234567890'
            },
            'ctx': {
                'error': {}
                }
        }

    @pytest.mark.asyncio
    async def test_missing_idempotency_key(self,
                                            client,
                                            test_setup):
        """
        Test missing idempotency_key in user registration
        """
        user_input = {
            "username": "username",
            "first_name": "Johnson",
            "last_name": "Johnson",
            "email": "Johnson@gmail.com",
            "password": "Johnson1234#",
            "confirm_password": "Johnson1234#",
            "email": "johnson@gmail.com"
        }

        response = client.post(
            url="/api/v1/auth/register",
            json=user_input
        )

        assert response.status_code == 201

        data = response.json()
        print("data: ", data["data"])

        assert data["status_code"] == 201
