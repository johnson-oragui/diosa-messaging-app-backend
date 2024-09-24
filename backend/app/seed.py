import asyncio

from app.database.session import get_session
from app.v1.users import User
from app.v1.chats import Message
from app.v1.rooms import Room, Room_Member
from app.v1.auth.dependencies import generate_idempotency_key


async def seed():
    """
    Add users to the table
    """
    johnson_key = await generate_idempotency_key("johnson@example.com", "johnson1")
    johnson = User(
        first_name="Johnson",
        last_name="Oragui",
        email="johnson@example.com",
        username="johnson1",
        idempotency_key=johnson_key
    )
    johnson.set_password("Johnson1234#")

    jayson_key = await generate_idempotency_key("jayson@example.com", "jayson1")
    jayson = User(
        first_name="Jayson",
        last_name="Oragui",
        email="jayson@example.com",
        username="jayson1",
        idempotency_key=jayson_key
    )
    jayson.set_password("Jayson1234#")

    jackson_key = await generate_idempotency_key("jackson@example.com", "jackson1")
    jackson = User(
        first_name="Jackson",
        last_name="Oragui",
        email="jackson@example.com",
        username="jackson1",
        idempotency_key=jackson_key
    )
    jackson.set_password("Jackson1234#")

    john_key = await generate_idempotency_key("john@example.com", "john1")
    john = User(
        first_name="John",
        last_name="Oragui",
        email="john@example.com",
        username="john1",
        idempotency_key=john_key
    )
    john.set_password("John1234#")

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
            john, friends,
            friends_member_johnson,
            friends_member_jackson, friends_member_john,
            jackson_message
        ])

        await session.commit()

asyncio.run(seed())
