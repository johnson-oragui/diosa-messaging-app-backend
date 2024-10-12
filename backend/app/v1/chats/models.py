from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.database.session import (
    Base,
    ModelMixin,
    String,
    Mapped,
    mapped_column
)
from app.v1.rooms import Room

if TYPE_CHECKING:
    from app.v1.users import User


class Message(ModelMixin, Base):
    """
    Class Message mapping users table in the database.
    """
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, unique=True, autoincrement=True
    )
    user_id: Mapped[str] = mapped_column(
        String(60), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    room_id: Mapped[str] = mapped_column(
        String(60), ForeignKey("rooms.id", ondelete="CASCADE"), index=True
    )
    content: Mapped[str] = mapped_column(String(1000))
    chat_type: Mapped[str] = mapped_column(
        Enum("public", "private", "direct_message", name="chat_type_enum", validate_strings=True, schema="chat")
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="messages", uselist=False
    )
    room: Mapped["Room"] = relationship(
        "Room", back_populates="messages", uselist=False
    )
