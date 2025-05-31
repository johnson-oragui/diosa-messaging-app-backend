import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from redis.exceptions import RedisError
from typing import AsyncIterator
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from brotli_asgi import BrotliMiddleware
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.middleware import (
    UserAgentMiddleware,
    SetHeadersMiddleware,
    RequestLoggerMiddleware,
)
from app.core.error_handlers import (
    exception,
    http_exception,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    redis_exception_handler,
    ratelimit_exception_handler,
)
from app.database.session import async_engine
from app.utils.task_logger import create_logger
from app.route.v1 import api_version_one
from app.core.config import settings
from app.database.celery_database import setup_celery_results_db

logger = create_logger("Main App")

limiter = Limiter(key_func=get_remote_address)

per_minute = "10/minute"
per_second = "1/second"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    App instance lifspan
    """
    logger.info(msg="Starting Application")
    setup_celery_results_db()
    try:
        yield
    finally:
        await async_engine.dispose()
        logger.info(msg="Shutting Down Application")


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
    allow_headers="*",
)

app.add_middleware(SessionMiddleware, secret_key=settings.secrets)
app.add_middleware(
    BrotliMiddleware, minimum_size=500
)  # compress response larger than 500 bytes
app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(UserAgentMiddleware)
app.add_middleware(RequestLoggerMiddleware)
app.add_middleware(SetHeadersMiddleware)

app.include_router(api_version_one)


@app.get("/", tags=["HOME"])
@limiter.limit(per_minute)
@limiter.limit(per_second)
async def read_root(request: Request) -> dict:
    """
    Read root
    """
    return {"message": "Welcome to chatroom API"}


app.add_exception_handler(RateLimitExceeded, ratelimit_exception_handler)
app.add_exception_handler(HTTPException, http_exception)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(RedisError, redis_exception_handler)
app.add_exception_handler(RedisError, ratelimit_exception_handler)
app.add_exception_handler(Exception, exception)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        port=7000,
        reload=True,
        timeout_keep_alive=60,
    )
