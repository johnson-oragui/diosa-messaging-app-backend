from typing import Dict, Any

responses: Dict[int | str, Dict[str, Any]] = {
    500: {
        "description": "Internal server error",
        "content": {
            "application/json": {
                "example": {
                    "status_code": 500,
                    "message": "Internal Server error occured",
                    "data": {},
                }
            }
        },
    },
    405: {
        "description": "Method not allowed",
        "content": {
            "application/json": {
                "example": {
                    "status_code": 405,
                    "message": "Method Not Allowed",
                    "data": {},
                },
            }
        },
    },
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "example": {"status_code": 400, "message": "Bad Request", "data": {}},
            }
        },
    },
    404: {
        "description": "Not found",
        "content": {
            "application/json": {
                "example": {"status_code": 404, "message": "Not found", "data": {}},
            }
        },
    },
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "example": {"status_code": 401, "message": "Unauthorized", "data": {}},
            }
        },
    },
    403: {
        "description": "Forbidden",
        "content": {
            "application/json": {
                "example": {"status_code": 403, "message": "Forbidden", "data": {}},
            }
        },
    },
}
