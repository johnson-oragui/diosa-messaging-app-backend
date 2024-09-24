from typing import Dict, Any

responses: Dict[int | str, Dict[str, Any]] = {
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "status_code": 500,
                        "message": "Internal Server error occured",
                        "data": {}
                    }
                }
            }
        },
        405: {
            "description": "Method not allowed",
            "content": {
                "application/json": {
                    "example": {
                        "status_code": 405,
                        "message": "Method Not Allowed",
                        "data": {}
                    },
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {
                        "status_code": 400,
                        "message": "Bad Request",
                        "data": {}
                    },
                }
            }
        }
    }
