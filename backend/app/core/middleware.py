"""
Exception handler module
"""
from fastapi import Request, HTTPException, status
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.task_logger import create_logger

logger = create_logger("Route middleware logger")

async def route_logger_middleware(request: Request, call_next):
    """
    Middleware to log user IP and user agent on each route call.
    """
    user_ip = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")

    # Log with extra fields for user_ip and user_agent
    logger.info(
        "Request Received",
        extra={
            "user_ip": user_ip,
            "user_agent": user_agent,
            "path": request.url.path,
            "method": request.method
        }
    )
    response = await call_next(request)

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
                    "message": "Missing user-agent",
                    "data": {}
                }
            )

        response = await call_next(request)
        return response

async def set_header_middleware(request: Request, call_next):
    """
    Sets the Content-Type header of the response to specify that the content is JSON,
    using UTF-8 encoding, and instructs the browser not to sniff the content type (no-sniff).

    Key Header:
        Content-Type: Defines the media type of the response.
        no-sniff: Protects against certain types of attacks by ensuring the browser respects
                    the declared content type and doesn't attempt to guess it.
    """
    response = await call_next(request)

    response.headers['Content-Type'] = "charset=utf-8; no-sniff"
    return response

async def set_hsts_header(request: Request, call_next):
    """
    Sets the Strict-Transport-Security header to force the browser to communicate only over HTTPS.
    It prevents HTTP communication after the browser's first visit to the site.

    Key Header:
        Strict-Transport-Security:

        max-age: Enforce HTTPS for 1 year (31,536,000 seconds).
        includeSubDomains: Apply this rule to all subdomains as well.
        preload: Allows the site to be included in the browser's HSTS preload list, meaning it
                will default to HTTPS without needing a prior visit.
    """
    response = await call_next(request)

    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    return response

async def set_csp_header(request: Request, call_next):
    """
    Sets the Content-Security-Policy (CSP) header, which restricts which resources the browser can 
    load (scripts, styles, images, etc.), protecting against attacks like
    Cross-Site Scripting (XSS).

    Key Header:
        Content-Security-Policy:

        default-src 'self': Only allow resources from the site's origin.
        script-src 'self' 'unsafe-inline': Allow scripts from the site's origin, but also allow
                    inline scripts (which can be a risk but may be needed in some cases).
    """
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'"
    return response

async def set_x_frame_options_header(request: Request, call_next):
    """
    Sets the X-Frame-Options header to prevent the page from being embedded in an iframe,
    protecting against clickjacking attacks.

    Key Header:
        X-Frame-Options:

        DENY: Disallows the page from being displayed in an iframe on any other site.
    """
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    return response

async def set_x_xss_protection_header(request: Request, call_next):
    """
    Sets the X-XSS-Protection header to enable the browser's built-in XSS filter, blocking content
    if an XSS attack is detected.

    Key Header:
        X-XSS-Protection:

        1: Enables XSS filtering.
        mode=block: Prevents the browser from rendering the page if an XSS attack is detected.
    """
    response = await call_next(request)
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

async def set_referrer_policy_header(request: Request, call_next):
    """
    Sets the Referrer-Policy header to control how much of the referrer URL is shared when
    navigating across sites. This can help limit exposure of sensitive information.

    Key Header:
        Referrer-Policy:
        strict-origin-when-cross-origin: Sends the full URL only for same-origin requests and only
                the origin for cross-origin requests.
    """
    response = await call_next(request)
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

async def set_expect_ct_header(request: Request, call_next):
    """
    Sets the Expect-CT header, which enforces certificate transparency (CT). It ensures that the
    site's SSL certificates are logged in public CT logs, making it harder to use rogue certificates.

    Key Header:
        Expect-CT:
        enforce: Enforces that the browser rejects connections that don't comply with CT.
        max-age=604800: The browser should enforce CT for 7 days.
        report-uri: Provides a URL where non-compliance with CT should be reported.
    """
    response = await call_next(request)
    response.headers["Expect-CT"] = "enforce; max-age=604800; report-uri=http://127.0.0.1:7001/logs"
    return response
