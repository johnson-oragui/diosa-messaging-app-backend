"""
RoomInvitation Model Module
"""

from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from app.database.session import (
    Base,
    ModelMixin,
    String,
    Mapped,
    mapped_column,
    DateTime,
)

from app.models.enums import invitation_status_enum

if TYPE_CHECKING:
    from app.models.room import Room
    from app.models.user import User


class RoomInvitation(ModelMixin, Base):
    """
    Class representing invitations to join private rooms.
    """

    __tablename__ = "chat_room_invitations"  # type: ignore
    room_id: Mapped[str] = mapped_column(
        String(60),
        ForeignKey("chat_rooms.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    inviter_id: Mapped[str] = mapped_column(
        String(60),
        ForeignKey("chat_users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    invitee_id: Mapped[str] = mapped_column(
        String(60),
        ForeignKey("chat_users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    invitation_status: Mapped[str] = mapped_column(
        invitation_status_enum, server_default="pending", default="pending"
    )

    expiration: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # --------------------------- relationships ------------------------
    room: Mapped["Room"] = relationship(
        "Room", back_populates="invitations", uselist=False
    )
    inviter: Mapped["User"] = relationship(
        "User",
        foreign_keys=[inviter_id],
        back_populates="sent_invitations",
        uselist=False,
    )
    invitee: Mapped["User"] = relationship(
        "User",
        foreign_keys=[invitee_id],
        back_populates="received_invitations",
        uselist=False,
    )

    __table_args__ = (
        UniqueConstraint(
            room_id, invitee_id, name="uq_room_invitation_room_id_invitee_id"
        ),
    )
