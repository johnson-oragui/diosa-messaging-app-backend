import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


register_input = {
    "email": "jayson@gtest.com",
    "password": "Jayson1234#",
    "confirm_password": "Jayson1234#",
    "idempotency_key": "123456789012-1234-2w3e-4r5t-6y7u8i9o",
}


async def delete_user(session: AsyncSession, email: str) -> None:
    """
    Deletes a user
    """
    await session.execute(sa.delete(User).where(User.email == email))
    await session.commit()
