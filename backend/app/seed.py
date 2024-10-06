import asyncio

from app.database.session import get_session
from app.v1.users import User
from app.v1.chats import Message
from app.v1.rooms import Room, Room_Member
from app.v1.profile import Profile
from app.v1.auth.dependencies import generate_idempotency_key


async def seed():
    """
    Add users to the table
    """
    johnson_key = await generate_idempotency_key("johnson@gmail.com", "johnson1")
    johnson = User(
        first_name="Johnson",
        last_name="Oragui",
        email="johnson@gmail.com",
        username="johnson1",
        idempotency_key=johnson_key,
        email_verified=True
    )
    johnson.set_password("Johnson1234#")
    johnson_profile = Profile(
        user=johnson,
    )

    jayson_key = await generate_idempotency_key("jayson@gmail.com", "jayson1")
    jayson = User(
        first_name="Jayson",
        last_name="Oragui",
        email="jayson@gmail.com",
        username="jayson1",
        idempotency_key=jayson_key,
        email_verified=True
    )
    jayson.set_password("Jayson1234#")
    jayson_profile = Profile(
        user=jayson
    )

    jackson_key = await generate_idempotency_key("jackson@gmail.com", "jackson1")
    jackson = User(
        first_name="Jackson",
        last_name="Oragui",
        email="jackson@gmail.com",
        username="jackson1",
        idempotency_key=jackson_key,
        email_verified=True
    )
    jackson.set_password("Jackson1234#")
    jackson_profile = Profile(user=jackson)

    john_key = await generate_idempotency_key("john@gmail.com", "john1")
    john = User(
        first_name="John",
        last_name="Oragui",
        email="john@gmail.com",
        username="john1",
        idempotency_key=john_key,
        email_verified=True
    )
    john.set_password("John1234#")
    john_profile = Profile(user=john)

    friends = Room(
        name="friends",
        owner=johnson,
    )

    friends_member_johnson = Room_Member(
        member=johnson,
        room=friends,
        is_admin=True
    )

    friends_member_jackson = Room_Member(
        member=jackson,
        room=friends,
        is_admin=True
    )

    friends_member_john = Room_Member(
        member=john,
        room=friends,
    )

    jackson_message = Message(
        user=jackson,
        room=friends,
        content="I am here now",
        chat_type="private"
    )

    async for session in get_session():
        session.add_all([
            johnson, jackson, jayson,
            john, johnson_profile, jackson_profile,
            jayson_profile, john_profile, friends,
            friends_member_johnson,
            friends_member_jackson, friends_member_john,
            jackson_message
        ])

        await session.commit()

asyncio.run(seed())
