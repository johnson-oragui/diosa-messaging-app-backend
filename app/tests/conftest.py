from typing import AsyncGenerator
from httpx import AsyncClient
import pytest
from fastapi import FastAPI

from main import app
from app.utils.celery_setup.setup import make_celery
from app.core.config import settings
from app.database.celery_database import setup_celery_results_db
from app.database.session import get_async_session


@pytest.fixture(scope="session")
def main_app() -> FastAPI:
    """
    Returns FastAPI app instance for testing
    """
    return app


@pytest.fixture(scope="function")
async def client(main_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """
    HTTPX async test client fixture
    """
    async with AsyncClient(app=main_app, base_url="http://test") as client_:
        yield client_


@pytest.fixture(scope="function")
async def test_session():
    """
    Removes test users
    """
    async for session in get_async_session():
        yield session


@pytest.fixture(scope="session")
def celery_app():
    """
    Configures celery
    """
    setup_celery_results_db()
    celery_app = make_celery(
        broker_url=settings.celery_broker_url_test,
        result_backend=settings.celery_result_backend_test,
    )
    return celery_app
