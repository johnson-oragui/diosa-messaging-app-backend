"""
Exception handler module
"""

import typing

from fastapi import HTTPException, Request, status, WebSocketException, WebSocket
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError
from redis.exceptions import RedisError
from slowapi.errors import RateLimitExceeded

from app.utils.task_logger import create_logger

logger = create_logger("Exception Handler Logger")


def get_user_ip_and_agent(request: typing.Union[Request, WebSocket]) -> dict:
    """
    Retrieves user_ip and user_agent
    """
    if isinstance(request, Request):
        user_ip = request.client and request.client.host or None
        user_agent = request.headers.get("user-agent", "Unknown")
        path = request.url.path
        method = request.method
        current_user = (
            request.state.current_user
            if hasattr(request.state, "current_user")
            else "Guest"
        )
        return {
            "user_ip": user_ip,
            "user_agent": user_agent,
            "path": path,
            "method": method,
            "current_user": current_user,
        }
    if isinstance(request, WebSocket):
        user_ip = request.client and request.client.host or None
        user_agent = request.headers.get("user-agent", "Unknown")
        path = request.url.path
        method = "websocket"
        current_user = (
            request.state.current_user
            if hasattr(request.state, "current_user")
            else "Guest"
        )
        return {
            "user_ip": user_ip,
            "user_agent": user_agent,
            "path": path,
            "method": method,
            "current_user": current_user,
        }


async def exception(request: Request, exc: Exception) -> JSONResponse:
    """
    Returns 500 status code
    """
    logger.error(
        msg=f"Unhandled Exception: {exc}", extra=get_user_ip_and_agent(request)
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            {
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An Unexpected Error Occured",
                "data": {},
            }
        ),
    )


async def http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handles Http Exceptions
    """
    logger.error(
        msg=f"Http Exception: {exc.detail}", extra=get_user_ip_and_agent(request)
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            {"status_code": exc.status_code, "message": exc.detail, "data": {}}
        ),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handles request validation error
    """
    error = exc.errors()[0] if exc.errors() else "No Error message to extract from"

    sensitive_words = [
        "password",
        "confirm_password",
        "secret_token",
        "new_password",
        "old_password",
    ]

    if isinstance(error, dict) and len(error) > 0:

        for key in error.keys():
            if key == "input":
                input = error.get("input")
                if isinstance(input, dict):
                    for k in input.keys():
                        if k in sensitive_words:
                            error["input"][k] = "************"
                        if k == "device_info" and "device_id" in error["input"][k]:
                            error["input"][k]["device_id"] = "*************"

    logger.error(msg=f"Validation error: {error}", extra=get_user_ip_and_agent(request))

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "Validation Error.",
                "data": error,
            }
        ),
    )


async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """
    Handles sqlalchemy error
    """
    logger.error(msg=f"Sqlachemy Error: {exc}", extra=get_user_ip_and_agent(request))

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            {
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Internal Server Error",
                "data": {},
            }
        ),
    )


async def redis_exception_handler(request: Request, exc: RedisError) -> JSONResponse:
    """
    Handles Redis Error
    """
    logger.error(msg=f"Redis error: {exc}", extra=get_user_ip_and_agent(request))
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=jsonable_encoder(
            {
                "status_code": status.HTTP_503_SERVICE_UNAVAILABLE,
                "message": "A Redis Error occured",
                "data": {},
            }
        ),
    )


async def websocket_exception_handler(
    websocket: WebSocket, exc: WebSocketException
) -> JSONResponse:
    """
    Handles WebSocketException Error
    """
    logger.error(
        msg=f"WebSocketException error: {exc}", extra=get_user_ip_and_agent(websocket)
    )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=jsonable_encoder(
            {
                "status_code": status.HTTP_503_SERVICE_UNAVAILABLE,
                "message": "A Websocket Error occured",
                "data": {},
            }
        ),
    )


async def ratelimit_exception_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """
    Handles ratelimit Error
    """
    logger.error(msg=f"RateLimit error: {exc}", extra=get_user_ip_and_agent(request))
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=jsonable_encoder(
            {
                "status_code": status.HTTP_429_TOO_MANY_REQUESTS,
                "message": "Too many login attempts. Please try again later.",
                "data": {},
            }
        ),
    )
