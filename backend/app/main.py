from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from redis.exceptions import RedisError

from app.core.middleware import (
    route_logger_middleware,
    set_header_middleware,
    set_x_frame_options_header,
)
from app.core.error_handlers import (
    exception,
    http_exception,
    validation_excption_handler,
    sqlalchemy_exception_handler,
    redis_exception_handler
)


app = FastAPI()

app.middleware("http")(route_logger_middleware)
app.middleware("http")(set_header_middleware)
app.middleware("http")(set_x_frame_options_header)

@app.get("/")
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
