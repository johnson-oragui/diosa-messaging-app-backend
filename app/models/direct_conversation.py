"""
DirectCOnversationModel module
"""

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, Index


from app.database.session import Base, ModelMixin
from app.models.direct_message import DirectMessage


if TYPE_CHECKING:
    from app.models.user import User


class DirectConversation(ModelMixin, Base):
    """
    Represents the direct_conversations table in the database
    """

    __tablename__ = "chat_direct_conversations"  # type: ignore

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
    is_deleted_for_sender: Mapped[bool] = mapped_column(
        default=False,
        server_default="FALSE",
        nullable=False,
    )
    is_deleted_for_recipient: Mapped[bool] = mapped_column(
        default=False,
        server_default="FALSE",
        nullable=False,
    )

    # ---------------------------- relationships -----------------------------
    sender: Mapped["User"] = relationship(
        "User", foreign_keys=[sender_id], back_populates="initiated_conversations"
    )
    recipient: Mapped["User"] = relationship(
        "User", foreign_keys=[recipient_id], back_populates="received_conversations"
    )

    messages: Mapped[List["DirectMessage"]] = relationship(
        "DirectMessage",
        back_populates="direct_conversation",
        cascade="all",
    )

    __table_args__ = (
        Index(
            "ix_unique_conversations_sender_id_recipient_id",
            "sender_id",
            "recipient_id",
            unique=True,
        ),
    )
