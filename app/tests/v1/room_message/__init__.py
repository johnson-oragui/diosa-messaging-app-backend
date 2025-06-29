"""
Test module
"""

from uuid import uuid4

register_input = {
    "email": "jayson30@gtest.com",
    "password": "Jayson1234#",
    "confirm_password": "Jayson1234#",
    "idempotency_key": str(uuid4()),
}
register_input_2 = {
    "email": "jayson190@gtest.com",
    "password": "Jayson1234#",
    "confirm_password": "Jayson1234#",
    "idempotency_key": str(uuid4()),
}
