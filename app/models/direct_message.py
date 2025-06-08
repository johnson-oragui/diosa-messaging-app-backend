"""
DirectMessage Model module
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import mapped_column, Mapped, relationship, validates
from sqlalchemy import DateTime, ForeignKey, Text


from app.database.session import Base, ModelMixin
from app.models.enums import message_status_enum


if TYPE_CHECKING:
    from app.models.user import User
    from app.models.direct_conversation import DirectConversation


class DirectMessage(ModelMixin, Base):
    """
    Represents the messages table in the database
    """

    __tablename__ = "chat_direct_messages"  # type: ignore

    sender_id: Mapped[str] = mapped_column(
        ForeignKey("chat_users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    recipient_id: Mapped[str] = mapped_column(
        ForeignKey("chat_users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("chat_direct_conversations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    parent_message_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("chat_direct_messages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        message_status_enum, index=True, default="sent", server_default="sent"
    )
    content: Mapped[str] = mapped_column(Text, nullable=True)
    media_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    media_type: Mapped[str] = mapped_column(default="text", server_default="text")

    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    is_deleted_for_recipient: Mapped[bool] = mapped_column(
        default=False,
        server_default="FALSE",
        comment="represents if the message is deleted for recipient user",
        nullable=False,
    )
    is_deleted_for_sender: Mapped[bool] = mapped_column(
        default=False,
        server_default="FALSE",
        comment="represents if the message is deleted for sender user",
        nullable=False,
    )
    is_edited: Mapped[bool] = mapped_column(default=False, server_default="FALSE")

    # -----------------------------relationships------------------------------------
    direct_conversation: Mapped["DirectConversation"] = relationship(
        "DirectConversation", back_populates="messages", uselist=False
    )

    sender: Mapped["User"] = relationship(
        "User",
        back_populates="direct_messages",
        passive_deletes=True,
        foreign_keys=[sender_id],
    )
    recipient: Mapped["User"] = relationship(
        "User",
        back_populates="received_direct_messages",
        passive_deletes=True,
        foreign_keys=[recipient_id],
    )

    parent_message: Mapped[Optional["DirectMessage"]] = relationship(
        "DirectMessage",
        remote_side="DirectMessage.id",
        back_populates="child_messages",
        passive_deletes=True,
    )

    child_messages: Mapped[List["DirectMessage"]] = relationship(
        "DirectMessage",
        back_populates="parent_message",
        uselist=True,
        passive_deletes=True,
    )

    @validates("status", "media_url")
    def validate_status(self, key: str, value: str) -> str:
        """
        Validates status and media_url
        """
        allowed_statuses = [
            "failed",
            "delivered",
            "read",
            "unread",
            "sent",
            "deleted",
            "edited",
        ]
        if key == "status" and value not in allowed_statuses:
            raise TypeError(
                f"Invalid status: {value}. Allowed statuses: {allowed_statuses}"
            )
        if key == "media_url":
            value = str(value)
        return value
