from typing import List
from passlib.context import CryptContext
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Enum

from app.database.session import (
    Base,
    ModelMixin,
    String,
    Mapped,
    mapped_column
)
from app.v1.chats import Message
from app.v1.profile import Profile
from app.v1.rooms import RoomInvitation
from app.base.enums import user_online_status_enum, user_status_enum

password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

class User(ModelMixin, Base):
    """
    Class User mapping users table in the database
    """
    # from app.chats.models import Message
    first_name: Mapped[str] = mapped_column(String(30), nullable=True)
    last_name: Mapped[str] = mapped_column(String(30), nullable=True)
    email: Mapped[str] = mapped_column(String(30), unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    idempotency_key: Mapped[str] = mapped_column(String(120), unique=True)
    email_verified: Mapped[bool] = mapped_column(default=False)
    status: Mapped[str] = mapped_column(user_status_enum, server_default="active")
    online_status: Mapped[str] = mapped_column(user_online_status_enum, server_default="online")

    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="user", cascade="all, delete-orphan"
    )

    rooms_created = relationship(
        "Room", back_populates="owner", cascade="all, delete-orphan"
    )

    rooms_belongs_to = relationship(
       "RoomMember", back_populates="member", cascade="all, delete-orphan"
    )
    profile: Mapped["Profile"] = relationship(
       "Profile", back_populates="user", cascade="all, delete-orphan", uselist=False
    )

    sent_invitations: Mapped[List["RoomInvitation"]] = relationship(
        "RoomInvitation", back_populates="inviter", foreign_keys=[RoomInvitation.inviter_id], cascade="all, delete-orphan"
    )

    received_invitations: Mapped[List["RoomInvitation"]] = relationship(
        "RoomInvitation", back_populates="invitee", foreign_keys=[RoomInvitation.invitee_id], cascade="all, delete-orphan"
    )

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
            raise Exception(f'{plain_password} must be provided')
        return password_context.verify(
            secret=plain_password,
            hash=self.password
        )

class SocialRegister(ModelMixin, Base):
    """
    SocialRegister Model(Table)
    """
    user_id: Mapped[str] = mapped_column(
        String(60), ForeignKey("users.id", ondelete="CASCADE")
    )
    # Social login provider (e.g., "google", "facebook", "github")
    provider: Mapped[str] = mapped_column()
    # Unique identifier for the user on the social login provider
    sub: Mapped[str] = mapped_column(String(60))
    access_token: Mapped[str] = mapped_column()
    id_token: Mapped[str] = mapped_column(nullable=True)
    refresh_token: Mapped[str] = mapped_column(nullable=True)
