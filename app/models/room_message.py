"""
RoomMessage Model Module
"""

from typing import TYPE_CHECKING, Optional, List
from sqlalchemy import ForeignKey, TEXT
from sqlalchemy.orm import relationship

from app.database.session import Base, ModelMixin, String, Mapped, mapped_column
from app.models.enums import message_status_enum

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.room import Room


class RoomMessage(ModelMixin, Base):
    """
    Class Message mapping users table in the database.
    """

    __tablename__ = "chat_room_messages"  # type: ignore

    sender_id: Mapped[str] = mapped_column(
        String(60),
        ForeignKey("chat_users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    room_id: Mapped[str] = mapped_column(
        String(60),
        ForeignKey("chat_rooms.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    parent_message_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("chat_room_messages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    content: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)
    status: Mapped[str] = mapped_column(
        message_status_enum, default="sent", server_default="sent"
    )
    is_deleted: Mapped[bool] = mapped_column(default=False, server_default="FALSE")
    media_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    media_type: Mapped[str] = mapped_column(default="text", server_default="text")
    is_edited: Mapped[bool] = mapped_column(default=False, server_default="FALSE")

    # -------------------------- relationships ----------------------------
    sender: Mapped["User"] = relationship(
        "User", back_populates="room_messages", uselist=False
    )
    room: Mapped["Room"] = relationship(
        "Room", back_populates="room_messages", uselist=False
    )

    parent_message: Mapped[Optional["RoomMessage"]] = relationship(
        "RoomMessage",
        remote_side="RoomMessage.id",
        back_populates="child_messages",
        passive_deletes=True,
    )

    child_messages: Mapped[List["RoomMessage"]] = relationship(
        "RoomMessage",
        back_populates="parent_message",
        uselist=True,
        passive_deletes=True,
    )
