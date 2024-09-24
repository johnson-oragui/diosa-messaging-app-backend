import pytest
from unittest import mock
from uuid import uuid4

from app.v1.users.schema import (
    RegisterInput,
    UserBase,
    RegisterOutput
)
from app.v1.users import User

@pytest.fixture(scope="session")
async def mock_session():
    """
    Mocks async session object
    """
    with mock.patch("app.database.session.get_session", autospec=True) as mock_session:
        mock_session = mock.AsyncMock()
        mock_session.add = mock.Mock(return_value=None)
        mock_session.commit = mock.AsyncMock(return_value=None)
        yield mock_session

@pytest.fixture
def mock_register_input_johnson():
    """
    Mock register input
    """
    register_input = RegisterInput(
        email="johnson@gmail.com",
        username="johnson1",
        first_name="johnson",
        last_name="oragui",
        password="Johnson1234@",
        confirm_password="Johnson1234@"
    )
    yield register_input

@pytest.fixture
def mock_johnson(mock_register_input_johnson):
    """
    Mock user johnson
    """
    user_dict = mock_register_input_johnson.model_dump(
            exclude={
                "confirm_password",
                "password"
            }
        )
    user_dict["id"] = str(uuid4())
    user = User(**user_dict)
    user.set_password("Johnson1234@")
    yield user

@pytest.fixture
def mock_johnson_2():
    """
    Mock user johnson
    """
    user_dict = {
        "id": str(uuid4()),
        "email": "johnso1n@gmail.com",
        "username": "johnson1",
        "first_name": "johnson",
        "last_name": "oragui",
        "password": "Johnson1234@",
    }
    user = User(**user_dict)
    user.set_password("Johnson1234@")
    yield user

@pytest.fixture
def mock_userbase_johnson(mock_johnson):
    """
    Mock user base for johnson
    """
    yield UserBase.model_validate(mock_johnson, from_attributes=True)

@pytest.fixture
def mock_register_output_johnson(mock_userbase_johnson):
    """
    Mock register output
    """
    yield RegisterOutput(
        status_code=201,
        message="User Registered Successfully",
        data=mock_userbase_johnson
    )

@pytest.fixture
def mock_register_output_johnson_idempotency(mock_userbase_johnson):
    """
    Mock register output
    """
    yield RegisterOutput(
        status_code=201,
        message="User Already Registered",
        data=mock_userbase_johnson
    )
