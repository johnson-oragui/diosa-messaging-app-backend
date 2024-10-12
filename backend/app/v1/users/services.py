from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select
from typing import Optional
from fastapi import (
    status,
)
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.utils.task_logger import create_logger
from app.v1.users import User
from app.base.services import Service
from app.v1.users import SocialRegister
from app.v1.users.schema import (
    UserMeOut,
    UserBase,
    ProfileBase,
    UserProfile
)
from app.v1.profile.services import profile_service


logger = create_logger("User Service")

class UserService(Service):
    """
    User class services
    """
    def __init__(self) -> None:
        super().__init__(User)

    async def create_social_login(self, schema: dict, session: AsyncSession) -> None:
        """Creates a new entry for the user in social login table.
        
        Keyword arguments:
            schema -- dictionary containing user fields.
            session -- Database session object
        Return: new user created.
        """
        social_login = SocialRegister(**schema)
        session.add(social_login)
        await session.commit()

    async def fetch_by_email_or_user_name(self, schema: dict, session: AsyncSession) -> Optional[User]:
        """
        Fetch a user by username or email.

        Keyword arguments:
            schema -- model containing user fields.
            session -- Database session object
        Return: user if user exists or None if user does not exist.
        """
        stmt = select(User).where(
            or_(
                User.email == schema.get("email"),
                User.username == schema.get("username", "")
            )
        )

        result = await session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_user_profile(self, user: User, session: AsyncSession) -> JSONResponse:
        """
        Fetch user data.

        Keyword arguments:
            user -- User model.
            session -- Database session object
        Return: User Data
        """
        profile = await profile_service.fetch({"user_id": user.id}, session)
        userme_out = UserMeOut(
            status_code=status.HTTP_200_OK,
            message="User data retrieved successfuly",
            data=UserProfile(
                user=UserBase.model_validate(user, from_attributes=True),
                profile=ProfileBase.model_validate(profile, from_attributes=True)
            )
        )

        response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(
                userme_out
            )
        )
        return response


user_service = UserService()
