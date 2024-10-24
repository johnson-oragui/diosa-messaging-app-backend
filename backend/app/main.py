from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from redis.exceptions import RedisError
from typing import AsyncIterator
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

from app.core.middleware import (
    route_logger_middleware,
    set_x_frame_options_header,
    UserAgentMiddleware,
    NoSniffMiddleware
)
from app.core.error_handlers import (
    exception,
    http_exception,
    validation_excption_handler,
    sqlalchemy_exception_handler,
    redis_exception_handler
)
from app.database.session import async_engine
from app.utils.task_logger import create_logger
from app import api_version_one
from app.core.config import settings
from app.database.celery_database import setup_celery_results_db

logger = create_logger("Main App")

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    App instance lifspan
    """
    logger.info(
        msg="Starting Application"
    )
    setup_celery_results_db()
    try:
        yield
    finally:
        await async_engine.dispose()
        logger.info(
            msg="Shutting Down Application"
        )


app = FastAPI(
    lifespan=lifespan,
    debug=True,
    title="Chat App.",
    description="A chat app API.",
    version="1.0.0",
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:7001",
    "http://localhost:7001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods="*",
    allow_headers="*"
)

app.add_middleware(SessionMiddleware, secret_key=settings.secrets)

app.middleware("http")(route_logger_middleware)
app.middleware("http")(set_x_frame_options_header)
app.add_middleware(UserAgentMiddleware)
app.add_middleware(NoSniffMiddleware)

app.include_router(api_version_one)

@app.get("/", tags=['HOME'])
async def read_root() -> dict:
    """
    Read root
    """
    return {"message": "Welcome to chatroom API"}


app.add_exception_handler(HTTPException, http_exception)
app.add_exception_handler(RequestValidationError, validation_excption_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(RedisError, redis_exception_handler)
app.add_exception_handler(Exception, exception)
