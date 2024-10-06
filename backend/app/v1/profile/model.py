from typing import TYPE_CHECKING
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

from app.database.session import (
    Base,
    ModelMixin,
    String,
    Mapped,
    mapped_column
)
from datetime import date


if TYPE_CHECKING:
    from app.v1.users import User

    
class Profile(ModelMixin, Base):
    """
    Represents the profile table in the database
    """
    user_id: Mapped[str] = mapped_column(
        String(60), ForeignKey("users.id", ondelete="CASCADE"), index=True, unique=True
    )
    recovery_email: Mapped[str] = mapped_column(nullable=True)
    bio: Mapped[str] = mapped_column(String(500), nullable=True)
    profession: Mapped[str] = mapped_column(String(50), nullable=True)
    gender: Mapped[str] = mapped_column(String(20), nullable=True)
    DOB: Mapped[date] = mapped_column(nullable=True)
    avatar_url: Mapped[str] = mapped_column(String(200), nullable=True)
    facebook_link: Mapped[str] = mapped_column(String(200), nullable=True)
    x_link: Mapped[str] = mapped_column(String(200), nullable=True)
    instagram_link: Mapped[str] = mapped_column(String(200), nullable=True)

    user: Mapped["User"] = relationship(
        "User", back_populates="profile", uselist=False
    )
