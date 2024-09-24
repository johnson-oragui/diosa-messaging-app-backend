from typing import List
from passlib.context import CryptContext
from sqlalchemy.orm import relationship

from app.database.session import (
    Base,
    ModelMixin,
    String,
    Mapped,
    mapped_column
)
from app.v1.chats import Message

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
    password: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(30), unique=True)
    idempotency_key: Mapped[str] = mapped_column(String(120), unique=True)

    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="user", cascade="all, delete-orphan"
    )

    rooms_created = relationship(
        "Room", back_populates="owner", cascade="all, delete-orphan"
    )

    rooms_belongs_to = relationship(
       "Room_Member", back_populates="member", cascade="all, delete-orphan"
    )

    def set_password(self, plain_password: str) -> None:
        """
        Sets a user password.
        """
        if not isinstance(plain_password, str) or not plain_password:
            raise Exception(f'{plain_password} must be a string')
        hashed_password = password_context.hash(plain_password)
        self.password = hashed_password

    def verify_password(self, plain_password) -> bool:
        """
        Verifies user password.
        """
        if not plain_password:
            raise Exception(f'{plain_password} must be provided')
        return password_context.verify(
            secret=plain_password,
            hash=self.password
        )
