from contextlib import contextmanager, asynccontextmanager
import redis
import redis.asyncio as aio_redis
from tenacity import retry, wait_fixed, stop_after_attempt

from app.core.config import settings


REDIS_URL: str = settings.redis_url


@contextmanager
@retry(
    wait=wait_fixed(2), stop=stop_after_attempt(5)
)  # retry after two seconds, upto 5 attempts
def get_redis_sync():
    """
    Connection to redis.
    """
    conn = redis.from_url(
        url=REDIS_URL,
        max_connections=10,
        decode_responses=True,
    )
    try:
        yield conn
    except redis.ConnectionError as exc:
        print(f"Redis connection error: {exc}")
        raise


@asynccontextmanager
@retry(
    wait=wait_fixed(2), stop=stop_after_attempt(5)
)  # retry after two seconds, upto 5 attempts
async def get_redis_async():
    """
    Asynchronous connection to Redis.
    """
    conn = aio_redis.from_url(
        url=REDIS_URL,
        max_connections=10,
        decode_responses=True,
    )
    try:
        yield conn
    except redis.ConnectionError as exc:
        print(f"Redis connection error: {exc}")
        raise
    finally:
        await conn.aclose()
