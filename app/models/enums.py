from sqlalchemy.dialects import postgresql


user_status_enum = postgresql.ENUM(
    "active",
    "inactive",
    "deleted",
    "banned",
    name="user_status_enum",
    create_type=False,  # Don't auto-create in migrations
)

user_online_status_enum = postgresql.ENUM(
    "online", "away", "offline", name="user_online_status_enum", create_type=False
)

room_type_enum = postgresql.ENUM(
    "public",
    "private",
    "direct_message",
    name="room_type_enum",
    validate_strings=True,
    create_type=False,
)

chat_type_enum = postgresql.ENUM(
    "public",
    "private",
    "direct_message",
    name="chat_type_enum",
    validate_strings=True,
    create_type=False,
)

invitation_status_enum = postgresql.ENUM(
    "pending",
    "accepted",
    "declined",
    "expired",
    "cancelled",
    name="invitation_status_enum",
    validate_strings=True,
    create_type=False,
)

message_status_enum = postgresql.ENUM(
    "delivered",
    "sent",
    name="message_status_enum",
    create_type=False,
)
