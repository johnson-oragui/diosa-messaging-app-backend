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
    "ignored",
    name="invitation_status_enum",
    validate_strings=True,
    create_type=False,
)

message_status_enum = postgresql.ENUM(
    "read",
    "unread",
    "delivered",
    "failed",
    "sent",
    "deleted",
    "edited",
    name="message_status_enum",
    create_type=False,
)


__all__ = [
    "user_online_status_enum",
    "user_status_enum",
    "room_type_enum",
    "chat_type_enum",
    "invitation_status_enum",
    "message_status_enum",
]
