import os
from typing import Optional
import pytest
from unittest import mock
from fastapi.testclient import TestClient
from fastapi import Request, Header, Cookie
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import StaticPool
import uuid

# Set TEST environment variable before importing app
os.environ["TEST"] = "TEST"
from app.main import app

from app.database.session import Base, get_session, DATABASE_URL
from app.v1.users.schema import (
    RegisterInput,
)
from app.core.config import social_oauth
from app.v1.auth.dependencies import (
    check_for_access_token,
    generate_jwt_token
)

user_id = str(uuid.uuid4())

test_engine = create_async_engine(
    url=DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

@pytest.fixture(scope="session")
def client():
    """
    Replaces the instance of the main app
    """
    client = TestClient(app)
    yield client


async def override_get_session():
    """
    Overrides get_session generator for app testing.
    """
    session = TestSessionLocal()
    yield session
    await session.close()

# create database session for overriding app dependencies
@pytest.fixture(scope="function")
async def test_get_session():
    """
    Replaces get_session function for method testing.
    """
    session = TestSessionLocal()
    yield session
    await session.close()

@pytest.fixture(scope="function")
async def mock_check_for_access_token():
    """
    Generates and returns access_token for check_access_token dependency function
    used for Authorization headers.
    """
    global user_id
    request = mock.AsyncMock(spec=Request)
    request.headers.get.retunr_value = "testclient"
    request.client.host.return_value = "testclient"
    access_token = await generate_jwt_token({
        "user_ip": "testclient",
        "user_agent": "testclient",
        "user_id": user_id
    })
    yield access_token

async def override_check_for_access_token(access_token: Optional[str] = Cookie(None),
                                          Authorization: Optional[str] = Header(None)):
    """
    Generates and returns access_token for check_access_token dependency function
    for the app.
    """
    if not access_token and not Authorization:
        yield
    global user_id
    request = mock.AsyncMock(spec=Request)
    request.headers.get.retunr_value = "testclient"
    request.client.host.return_value = "testclient"
    access_token = await generate_jwt_token({
        "user_ip": "testclient",
        "user_agent": "testclient",
        "user_id": user_id
    })
    yield access_token

# override get_session dependency with sqlite session
app.dependency_overrides[get_session] = override_get_session
# override check_for_access_token dependency
app.dependency_overrides[check_for_access_token] = override_check_for_access_token


# Restore environment variable after tests
@pytest.fixture(scope="session", autouse=True)
def restore_test_env():
    """
    Restore environment variable after tests
    """
    yield
    os.environ["TEST"] = ""


# create database session for testing service classes
@pytest.fixture(scope="function")
async def test_setup():
    """
    create database session for testing service classes
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
def mock_user_id():
    """
    mock for a general user_id
    """
    global user_id
    yield user_id

@pytest.fixture(scope="function")
def mock_register_input_johnson():
    """
    Mock register input for johnson user
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

@pytest.fixture(scope="function")
def mock_johnson_user_dict():
    """
    Mock dict input for johnson user
    """
    register_input = {
        "email": "johnson@gmail.com",
        "username": "johnson",
        "first_name": "johnson",
        "last_name": "oragui",
        "password": "Johnson1234@",
        "idempotency_key": "johnson_idempotency-key"
    }
    yield register_input

@pytest.fixture(scope="function")
def mock_register_input_jayson():
    """
    Mock register input for jayson user
    """
    register_input = RegisterInput(
        email="jayson@gmail.com",
        username="jayson",
        first_name="jayson",
        last_name="oragui",
        password="Jayson1234@",
        confirm_password="Jayson1234@"
    )
    yield register_input

@pytest.fixture(scope="function")
def mock_jayson_user_dict():
    """
    Mock dict input for jayson
    """
    register_input = {
        "email": "jayson@gmail.com",
        "username": "jayson",
        "first_name": "jayson",
        "last_name": "oragui",
        "password": "Jayson1234@",
        "confirm_password": "Jayson1234@",
        "idempotency_key": "fake_idempotency-key"
    }
    yield register_input

@pytest.fixture(scope="function")
def mock_google_response():
    """
    Mock google oauth2 response on callback route
    """
    return_value = {
        'access_token': 'EVey7-4DYZRDXTg493-w0171...',
        'expires_in': 3599,
        'scope': 'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email openid',
        'token_type': 'Bearer',
        'id_token': 'eyJhbGciOiJSUcoL9_mGQBw...',
        'expires_at': 1721492909,
        'userinfo': {
            'iss': 'https://accounts.google.com',
            'azp': '209678677159-sro71tn72puotnppasrtgv52j829cq8g.apps.googleusercontent.com',
            'aud': '209678677159-sro71tn72puotnppas0jnmj52j829cq8g.apps.googleusercontent.com',
            'sub': '114132989973144532376',
            'email': 'jackson@gmail.com',
            'email_verified': True,
            'at_hash': 'hD_Uuf9ibTsxXsDP1_ePgw',
            'nonce': 'aEbk4yA7wZtXazvBrmyL',
            'name': 'jackson jackson',
            'picture': 'https://lh3.googleusercontent.com/a/ACg8rdfcvg0cK-dwE_fcjV9yj7yhnjiWCDl1PnXbWw56dq-qZKN52Q=s96-c',
            'given_name': 'jackson',
            'family_name': 'jackson',
            'iat': 1721489311,
            'exp': 1721492911
            }
    }
    yield return_value


@pytest.fixture(scope="function")
def mock_google_oauth2(mock_google_response):
    """
    Mock google oauth2
    """
    with mock.patch.object(social_oauth.google, "authorize_redirect") as mock_authorize_redirect:
        with mock.patch.object(social_oauth.google, "authorize_access_token") as mock_authorize_access_token:

            mock_authorize_redirect.return_value = "http://testserver/api/v1/auth/register/social"
            mock_authorize_access_token.return_value = mock_google_response

            yield mock_authorize_redirect, mock_authorize_access_token

@pytest.fixture(scope="function")
def mock_github_response():
    """
    Mock github oauth2 response
    """
    return_value = {
        "access_token": "fake_access_token",
        "type": "bearer",
        "scope": "user",
        "userinfo": {
            "login": "johnson-king",
            "id": "123456",
            "node_id": "dun2349funo4fnifq3",
            "avatar_url": "https://someurl.com",
            "url": "someurl",
            "html_url": "some url",
            "followers_url": "some url",
            "following_url": "some url",
            "gists_url": "some url",
            "starred_url": "some url",
            "subscriptions_url": "some url",
            "organizations_url": "some url",
            "repos_url": "some url",
            "events_url": "some url",
            "received_events_url": "some url",
            "Type": "User",
            "site_admin": False,
            "name": "johnson king",
            "company": None,
            "blog": "",
            "location": "Denver, CO",
            "email": "johnson-king@gmail.com",
            "hireable": True,
            "bio": None,
            "twitter_username": None,
            "public_repos": 56,
            "public_gists": 0,
            "followers":4,
            "following": 0,
            "created_at": "2019-11-12T16:18:56Z",
            "updated_at": "2024-01-12T16:11:16Z",
        }
    }
    yield return_value

@pytest.fixture(scope="function")
def mock_github_oauth2(mock_github_response):
    """
    Mock github oauth2
    """
    with mock.patch.object(social_oauth.github, "authorize_redirect") as mock_authorize_redirect:
        with mock.patch.object(social_oauth.github, "authorize_access_token") as mock_authorize_access_token:

            mock_authorize_redirect.return_value = "http://testserver/api/v1/auth/register/social"
            mock_authorize_access_token.return_value = mock_github_response

            yield mock_authorize_redirect, mock_authorize_access_token

@pytest.fixture(scope="function")
def mock_public_room_one_dict():
    """
    Room one dict
    """
    room = {
        "room_name": "public_room_one",
        "room_type": "public",
        "description": "public room",
        "creator_id": "",
    }
    yield room

@pytest.fixture(scope="function")
def mock_public_room_two_dict():
    """
    Room two dict
    """
    room = {
        "room_name": "public_room_two",
        "room_type": "public",
        "description": "public room",
        "creator_id": "",
    }
    yield room

@pytest.fixture(scope="function")
def mock_private_room_one_dict():
    """
    Room one dict
    """
    room = {
        "room_name": "private_room_one",
        "room_type": "private",
        "description": "public room",
        "creator_id": "",
    }
    yield room

@pytest.fixture(scope="function")
def mock_private_room_two_dict():
    """
    Room two dict
    """
    room = {
        "room_name": "private_room_two",
        "room_type": "private",
        "description": "public room",
        "creator_id": "",
    }
    yield room

@pytest.fixture(scope="function")
def mock_direct_message_one_dict():
    """
    Room one dict
    """
    room = {
        "room_name": "direct_message_one",
        "room_type": "direct_message",
        "description": "public room",
        "creator_id": "",
    }
    yield room

@pytest.fixture(scope="function")
def mock_direct_message_two_dict():
    """
    Room two dict
    """
    room = {
        "room_name": "direct_message_two",
        "room_type": "direct_message",
        "description": "public room",
        "creator_id": "",
    }
    yield room
