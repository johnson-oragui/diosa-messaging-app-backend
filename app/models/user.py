"""
User model module
"""

from typing import Optional, List
import hashlib

from passlib.context import CryptContext
from sqlalchemy import Index
from sqlalchemy.orm import mapped_column, Mapped, relationship


from app.database.session import Base, ModelMixin, String
from app.models.enums import user_online_status_enum, user_status_enum


from app.models.user_session import UserSession
from app.models.direct_message import DirectMessage
from app.models.direct_conversation import DirectConversation

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(ModelMixin, Base):
    """
    Class User mapping users table in the database
    """

    __tablename__ = "chat_users"  # type: ignore

    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(150), unique=True)
    password: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    username: Mapped[Optional[str]] = mapped_column(
        String(150), unique=True, nullable=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(150))
    email_verified: Mapped[bool] = mapped_column(default=False, server_default="FALSE")
    is_deleted: Mapped[bool] = mapped_column(default=False, server_default="FALSE")
    profile_photo: Mapped[Optional[str]] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(
        user_status_enum, server_default="active", default="active"
    )
    online_status: Mapped[str] = mapped_column(
        user_online_status_enum, server_default="online", default="online"
    )

    __table_args__ = (
        Index("uq_chat_users_idempotency_key", idempotency_key, unique=True),
    )

    # ---------------------------- relationships ---------------------

    sessions: Mapped[List["UserSession"]] = relationship(
        "UserSession", back_populates="user", cascade="all"
    )

    direct_messages: Mapped[List["DirectMessage"]] = relationship(
        "DirectMessage",
        back_populates="sender",
        passive_deletes=True,
        foreign_keys=[DirectMessage.sender_id],
        cascade="all, delete-orphan",
    )
    received_direct_messages: Mapped[List["DirectMessage"]] = relationship(
        "DirectMessage",
        back_populates="recipient",
        passive_deletes=True,
        foreign_keys=[DirectMessage.recipient_id],
        cascade="all, delete-orphan",
    )

    initiated_conversations: Mapped["DirectConversation"] = relationship(
        "DirectConversation",
        foreign_keys=[DirectConversation.sender_id],
        back_populates="sender",
        cascade="all",
    )

    received_conversations: Mapped["DirectConversation"] = relationship(
        "DirectConversation",
        foreign_keys=[DirectConversation.recipient_id],
        back_populates="recipient",
        cascade="all",
    )

    # ------------------ methods ------------------

    def set_password(self, plain_password: str) -> None:
        """
        Sets a user password.

        Args:
            plain_password(str): password to hash.
        """
        if not plain_password or plain_password == "":
            return
        hashed_password = password_context.hash(plain_password)
        self.password = hashed_password

    def verify_password(self, plain_password) -> bool:
        """
        Verifies user password.

        Args:
            plain_password(str): password to compare with hash.
        """
        if not plain_password:
            raise ValueError(f"{plain_password} must be provided")
        return password_context.verify(secret=plain_password, hash=self.password)

    async def set_idempotency_key(self, email: str) -> None:
        """Creates an idempotency key

        Keyword arguments:
            email(str) -- user email
        Return: None
        """
        if not email:
            raise TypeError("email cannot be None")
        self.idempotency_key = hashlib.sha256(email.encode()).hexdigest()
