"""
Exception handler module
"""
from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from redis.exceptions import RedisError

from app.utils.task_logger import create_logger

logger = create_logger("Exception Handler Logger")

def get_user_ip_and_agent(request: Request) -> dict:
    """
    Retrieves user_ip and user_agent
    """
    user_ip = request.client.host
    user_agent = request.headers.get('user-agent', 'Unknown')
    return {"user_ip": user_ip, "user_agent": user_agent}

async def exception(request: Request, exc: Exception) -> JSONResponse:
    """
    Returns 500 status code
    """
    logger.error(
        msg=f"Unhandled Exception: {exc}",
        extra=get_user_ip_and_agent(request)
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "An Unexpected Error Occured" ,
            "data": {}
        }
    )

async def http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handles Http Exceptions
    """
    logger.error(
        msg=f"Http Exception: {exc.detail}",
        extra=get_user_ip_and_agent(request)
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "message": exc.detail,
            "data": {}
        }
    )

async def validation_excption_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handles request validation error
    """
    logger.error(
        msg=f"Validation error: {exc.errors()}",
        extra=get_user_ip_and_agent(request)
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "Validation Error.",
            "data": exc.errors()
        }
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handles sqlalchemy error
    """
    logger.error(
        msg=f"Sqlachemy Error: {exc}",
        extra=get_user_ip_and_agent(request)
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Internal Server Error",
            "data": {}
        }
    )

async def redis_exception_handler(request: Request, exc: RedisError) -> JSONResponse:
    """
    Handles Redis Error
    """
    logger.error(
        msg=f'Redis error: {exc}',
        extra=get_user_ip_and_agent(request)
    )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status_code": status.HTTP_503_SERVICE_UNAVAILABLE,
            "message": "A Redis Error occured",
            "data": {}
        }
    )
