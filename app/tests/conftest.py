"""
Conftest module
"""

from typing import AsyncGenerator
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy import StaticPool
from fastapi.testclient import TestClient

from main import app
from app.core.config import settings
from app.database.session import get_async_session, Base
from app.database.redis_db import get_redis_client
from app.database.redis_db import get_redis_async


# SQLite-specific configuration for local testing
test_engine = create_async_engine(
    url=settings.db_url_test,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)


TestSessionLocalMemory = async_sessionmaker(
    bind=test_engine, autoflush=False, autocommit=False, expire_on_commit=False
)


@pytest.fixture(scope="function")
async def test_get_session():
    """
    Replaces get_session function for method testing.
    """
    async with TestSessionLocalMemory() as session:
        yield session
        await session.close()


@pytest.fixture(scope="function")
async def test_get_redis_client():
    """
    Replaces get_session function for method testing.
    """
    redis = await get_redis_client()
    yield redis
    # await redis.aclose()


async def override_get_async_session():
    """
    Overrides get_async_session generator in app instance.
    """
    async with TestSessionLocalMemory() as session:
        yield session
        await session.close()


async def override_get_redis_async_client():
    """
    Overrides get_async_session generator in app instance.
    """
    redis = await get_redis_client()
    yield redis
    # if redis:
    #     await redis.aclose()


async def override_get_redis_async_session():
    """
    Overrides get_async_session generator in app instance.
    """
    async with get_redis_async() as redis:

        yield redis
        # if redis:
        #     await redis.aclose()


app.dependency_overrides[get_async_session] = override_get_async_session
app.dependency_overrides[get_redis_client] = override_get_redis_async_client
app.dependency_overrides[get_redis_async] = override_get_redis_async_session


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    HTTPX async test client fixture
    """
    async with AsyncClient(app=app, base_url="http://test") as clients:
        yield clients


@pytest.fixture(scope="function")
async def app_client() -> AsyncGenerator[TestClient, None]:
    """
    Sync test client for websocket connection tests
    """
    with TestClient(app) as app_clients:
        yield app_clients


# create database session for testing service classes
@pytest.fixture(scope="function")
async def test_setup():
    """
    create database session for testing service classes
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield
