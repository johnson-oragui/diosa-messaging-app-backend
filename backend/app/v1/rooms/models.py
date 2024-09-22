from typing import TYPE_CHECKING, List
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, UniqueConstraint

from app.v1.database.session import (
    Base,
    ModelMixin,
    String,
    Mapped,
    mapped_column,
    func,
    datetime,
    DateTime
)

if TYPE_CHECKING:
    from app.v1.chats import Message
    from app.v1.users import User

class Room(ModelMixin, Base):
    """
    Class representing rooms table
    """
    name: Mapped[str] = mapped_column(String(40))
    owner_id: Mapped[str] = mapped_column(
        String(60), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    is_private: Mapped[bool] = mapped_column(default=True)

    owner: Mapped["User"] = relationship(
        back_populates="rooms_created", uselist=False
    )
    messages: Mapped[List["Message"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )

    room_members: Mapped[List["Room_Member"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )


class Room_Member(ModelMixin, Base):
    """
    Class representing room_members
    """
    user_id: Mapped[str] = mapped_column(
        String(60), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    room_id: Mapped[str] = mapped_column(
        String(60), ForeignKey("rooms.id", ondelete="CASCADE"), index=True
    )
    invited_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    is_admin: Mapped[bool] = mapped_column(default=False)

    member: Mapped["User"] = relationship(
        "User", back_populates="rooms_belongs_to", uselist=False
    )
    room: Mapped["Room"] = relationship(
        "Room", back_populates="room_members", uselist=False
    )

    __table_args__ = (
        UniqueConstraint(room_id, user_id, name="uq_room_member_room_id_user_id"),
    )
