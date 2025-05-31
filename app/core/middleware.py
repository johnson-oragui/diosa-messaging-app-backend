"""
Exception handler module
"""

import time

from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.task_logger import create_logger

logger = create_logger("Route middleware logger")


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log user IP, user agent, and route details on each request.
    Also checks for a valid user-agent.
    """

    async def dispatch(self, request: Request, call_next):
        user_ip = request.headers.get(
            "x-forwarded-for", request.client and request.client.host or None
        )
        user_agent = request.headers.get("user-agent", "Unknown")
        if user_ip in ["193.41.206.36", "142.93.208.169", "195.178.110.164"]:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=jsonable_encoder(
                    {
                        "status_code": status.HTTP_429_TOO_MANY_REQUESTS,
                        "message": "Hey!!! Careful Now!!!",
                        "data": {},
                    }
                ),
            )

        # Check for missing user-agent
        if (
            user_agent == "Unknown"
            and not request.url.path.startswith("/api/v1/payments/flutterwave/webhook")
            and not request.url.path.startswith("/api/v1/payments/stripe/webhook")
        ):
            logger.warning(
                "Request blocked due to missing user-agent",
                extra={"user_ip": user_ip},
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=jsonable_encoder(
                    {
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": "Bad Request: Invalid",
                        "data": {},
                    }
                ),
            )

        if (
            not request.url.path.startswith("/api/v1")
            and request.url.path != "/"
            and not request.url.path.startswith("/socket.io")
            and not request.url.path.startswith("/docs")
            and not request.url.path.startswith("/favicon")
            and not request.url.path.startswith("/openapi")
        ):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=jsonable_encoder(
                    {
                        "status_code": status.HTTP_429_TOO_MANY_REQUESTS,
                        "message": "Hey!!! Careful Now!!!",
                        "data": {},
                    }
                ),
            )

        # Log initial request info, masking sensitive information
        start_time = time.time()
        try:
            payload = await request.json()
            sensitive_field = [
                "password",
                "confirm_password",
                "secret_token",
                "refresh_token",
                "access_token",
                "code",
                "token",
                "confirm_new_password",
                "new_password",
            ]
            for key in payload.keys():
                if key in sensitive_field:
                    payload[key] = "***********"
                if key == "device_info" and "device_id" in payload[key]:
                    payload[key]["device_id"] = "**************"

        except Exception:
            payload = {}
        logger.info(
            "Request received",
            extra={
                "user_ip": user_ip,
                "user_agent": user_agent,
                "path": request.url.path,
                "method": request.method,
                "payload": payload,
            },
        )

        # Retrieve authenticated user if available
        if not hasattr(request, "current_user"):
            request.current_user = None  # type: ignore

        # Process the request
        response = await call_next(request)

        # Log response status and time taken
        process_time = time.time() - start_time
        user_info = (
            request.state.current_user
            if hasattr(request.state, "current_user")
            else "Guest"
        )

        logger.info(
            "Request completed",
            extra={
                "current_user": user_info,
                "user_ip": user_ip,
                "user_agent": user_agent,
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "process_time": f"{process_time:.2f}s",
            },
        )

        return response


class UserAgentMiddleware(BaseHTTPMiddleware):
    """
    Class for UserAgent middleware
    """

    async def dispatch(self, request: Request, call_next):
        """
        Checks for user agent.
        """
        user_agent = request.headers.get("user-agent", "Unknown")
        if user_agent == "Unknown":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Bad Request!",
                    "data": {},
                },
            )

        response = await call_next(request)
        return response


class SetHeadersMiddleware(BaseHTTPMiddleware):
    """
    Sets headers
    """

    async def dispatch(self, request: Request, call_next):
        """
        Set header middleware class.
        """
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Sets the X-Frame-Options header to prevent the page from being
        # embedded in an iframe, protecting against clickjacking attacks.
        response.headers["X-Frame-Options"] = "DENY"
        # Sets the Expect-CT header, which enforces certificate transparency (CT).
        # It ensures that the site's SSL certificates are logged in public CT logs,
        # making it harder to use rogue certificates.
        response.headers["Expect-CT"] = "enforce; max-age=604800"
        # Sets the Referrer-Policy header to control how much of the referrer URL is shared when
        # navigating across sites. This can help limit exposure of sensitive information.
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Sets the X-XSS-Protection header to enable the browser's built-in XSS filter,
        # blocking content if an XSS attack is detected.
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
        return response
