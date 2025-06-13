"""
RoomMember Model Module
"""

from typing import TYPE_CHECKING
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, UniqueConstraint


from app.database.session import (
    Base,
    ModelMixin,
    String,
    Mapped,
    mapped_column,
)


if TYPE_CHECKING:
    from app.models.room import Room
    from app.models.user import User


class RoomMember(ModelMixin, Base):
    """
    Class representing room_members
    """

    __tablename__ = "chat_room_members"  # type: ignore
    member_id: Mapped[str] = mapped_column(
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

    is_admin: Mapped[bool] = mapped_column(default=False, server_default="FALSE")
    left_room: Mapped[bool] = mapped_column(default=False, server_default="FALSE")

    # ------------------------------ relationships ------------------
    member: Mapped["User"] = relationship(
        "User", back_populates="membered_rooms", uselist=False
    )
    room: Mapped["Room"] = relationship(
        "Room", back_populates="room_members", uselist=False
    )

    __table_args__ = (
        UniqueConstraint(room_id, member_id, name="uq_room_member_room_id_user_id"),
    )
