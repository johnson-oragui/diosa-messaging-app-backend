"""
Room model module
"""

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey

from app.database.session import Base, ModelMixin
from app.models.room_member import RoomMember
from app.models.room_invitation import RoomInvitation
from app.models.room_message import RoomMessage

if TYPE_CHECKING:
    from app.models.user import User


class Room(ModelMixin, Base):
    """
    Represents the romms table in the database
    """

    __tablename__ = "chat_rooms"  # type: ignore

    owner_id: Mapped[str] = mapped_column(
        ForeignKey("chat_users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    name: Mapped[str] = mapped_column(index=True, unique=False)
    room_icon: Mapped[Optional[str]] = mapped_column(nullable=True)
    messages_delete_able: Mapped[bool] = mapped_column(
        default=False, server_default="FALSE"
    )
    is_deactivated: Mapped[bool] = mapped_column(default=False, server_default="FALSE")
    allow_admin_messages_only: Mapped[bool] = mapped_column(
        default=False, server_default="FALSE"
    )
    is_private: Mapped[bool] = mapped_column(default=False, server_default="FALSE")
    allow_non_admin_invitations: Mapped[bool] = mapped_column(
        default=True, server_default="TRUE"
    )

    # ------------------- relationships -------------------------

    owner: Mapped["User"] = relationship(
        "User",
        back_populates="created_rooms",
        passive_deletes=True,
        foreign_keys=[owner_id],
    )

    room_members: Mapped[List["RoomMember"]] = relationship(
        "RoomMember",
        back_populates="room",
    )

    invitations: Mapped[List["RoomInvitation"]] = relationship(
        "RoomInvitation", back_populates="room", uselist=True
    )

    room_messages: Mapped["RoomMessage"] = relationship(
        "RoomMessage", back_populates="room", uselist=False
    )
