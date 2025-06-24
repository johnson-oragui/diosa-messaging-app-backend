"""
Redis session module
"""

from contextlib import contextmanager, asynccontextmanager
import redis
import redis.asyncio as aio_redis
from redis.asyncio import Redis
from tenacity import retry, wait_fixed, stop_after_attempt

from app.core.config import settings
from app.utils.task_logger import create_logger

logger = create_logger(":: REDIS SESSION ::")


@contextmanager
@retry(
    wait=wait_fixed(2), stop=stop_after_attempt(5)
)  # retry after two seconds, upto 5 attempts
def get_redis_sync():
    """
    Connection to redis.
    """
    conn = redis.from_url(
        url=settings.redis_url,
        max_connections=10,
        decode_responses=True,
    )
    try:
        yield conn
    except redis.ConnectionError as exc:
        logger.error("Redis connection error: %s", str(exc))
        raise exc


@asynccontextmanager
@retry(
    wait=wait_fixed(2), stop=stop_after_attempt(5)
)  # retry after two seconds, upto 5 attempts
async def get_redis_async():
    """
    Asynchronous connection to Redis.
    """
    conn = aio_redis.from_url(
        url=settings.redis_url,
        max_connections=10,
        decode_responses=True,
    )
    try:
        yield conn
    except redis.ConnectionError as exc:
        logger.error("Redis connection error: %s", str(exc))
        raise exc
    except RuntimeError as exc:
        logger.error("Redis connection RuntimeError error: %s", str(exc))
        raise exc
    finally:
        # if conn:
        #     await conn.aclose()
        pass


async def get_redis_client() -> Redis:
    """
    Resolves the Redis client from the context manager.
    """
    try:
        async with get_redis_async() as redis_:
            return redis_
    except RuntimeError as exc:
        logger.error("Redis RuntimeError error: %s", str(exc))
        raise exc
