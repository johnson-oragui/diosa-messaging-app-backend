from typing import TYPE_CHECKING
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, UniqueConstraint

from app.database.session import (
    Base,
    ModelMixin,
    String,
    Mapped,
    mapped_column,
    func,
    datetime,
    DateTime
)
from app.base.enums import (
    room_type_enum,
    invitation_status_enum
)

if TYPE_CHECKING:
    from app.v1.chats import Message
    from app.v1.users import User


class Room(ModelMixin, Base):
    """
    Class representing rooms table
    """
    room_name: Mapped[str] = mapped_column(String(130))
    creator_id: Mapped[str] = mapped_column(
        String(60), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    room_type: Mapped[str] = mapped_column(room_type_enum, server_default="private")

    description: Mapped[str] = mapped_column(nullable=True)
    messages_deletable: Mapped[bool] = mapped_column(default=True)
    idempotency_key: Mapped[str] = mapped_column(nullable=True)
    is_deleted: Mapped[bool] = mapped_column(default=False, server_default="FALSE")

    owner: Mapped["User"] = relationship(
        "User", back_populates="rooms_created", uselist=False
    )
    messages: Mapped["Message"] = relationship(
        "Message", back_populates="room", cascade="all, delete-orphan"
    )

    room_members: Mapped["RoomMember"] = relationship(
        "RoomMember", back_populates="room", cascade="all, delete-orphan"
    )

    invitations: Mapped["RoomInvitation"] = relationship(
        "RoomInvitation", back_populates="room", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint(
            idempotency_key, name="uq_room_idempotency_key"
        ),
    )


class RoomMember(ModelMixin, Base):
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
    room_type: Mapped[str] = mapped_column(room_type_enum)
    is_admin: Mapped[bool] = mapped_column(default=False)
    idempotency_key: Mapped[str] = mapped_column(nullable=True)

    member: Mapped["User"] = relationship(
        "User", back_populates="rooms_belongs_to", uselist=False
    )
    room: Mapped["Room"] = relationship(
        "Room", back_populates="room_members", uselist=False
    )

    __table_args__ = (
        UniqueConstraint(room_id, user_id, name="uq_room_member_room_id_user_id"),
    )


class RoomInvitation(ModelMixin, Base):
    """
    Class representing invitations to join private rooms.
    """
    room_id: Mapped[str] = mapped_column(
        String(60), ForeignKey("rooms.id", ondelete="CASCADE"), index=True
    )
    inviter_id: Mapped[str] = mapped_column(
        String(60), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    invitee_id: Mapped[str] = mapped_column(
        String(60), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    invitation_status: Mapped[str] = mapped_column(invitation_status_enum, server_default="pending")
    room_type: Mapped[str] = mapped_column(room_type_enum)

    room: Mapped["Room"] = relationship(
        "Room", back_populates="invitations", uselist=False
    )
    inviter: Mapped["User"] = relationship(
        "User", foreign_keys=[inviter_id], back_populates="sent_invitations", uselist=False
    )
    invitee: Mapped["User"] = relationship(
        "User", foreign_keys=[invitee_id], back_populates="received_invitations", uselist=False
    )

    __table_args__ = (
        UniqueConstraint(
            room_id, invitee_id, name="uq_room_invitation_room_id_invitee_id"
        ),
    )
