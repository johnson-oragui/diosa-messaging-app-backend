"""
UserSession module
"""

from typing import TYPE_CHECKING, Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.database.session import Base, ModelMixin

if TYPE_CHECKING:
    from app.models.user import User


class UserSession(ModelMixin, Base):
    """
    Represents user sessins in the database
    """

    __tablename__ = "chat_user_sessions"  # type: ignore

    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("chat_users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    session_id: Mapped[str] = mapped_column(index=True)
    is_logged_out: Mapped[bool] = mapped_column(
        default=False, server_default="FALSE", index=True
    )
    jti: Mapped[str] = mapped_column()
    location: Mapped[str] = mapped_column()
    ip_address: Mapped[str] = mapped_column()
    logged_out_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # --------------------- relationships -------------------------
    user: Mapped["User"] = relationship(
        "User", back_populates="sessions", cascade="all"
    )
