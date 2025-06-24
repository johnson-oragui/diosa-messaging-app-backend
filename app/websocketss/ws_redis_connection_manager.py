"""
Redis manager module
"""

import typing
import json
from redis.asyncio import Redis
from redis.asyncio.client import PubSub
from fastapi import WebSocket

from app.core.config import settings
from app.models.direct_message import DirectMessage

REDIS_URL: str = settings.redis_url


class WSRedisConnectionManager:
    """
    Redis connection manager
    """

    # ++++++++++++++++ USERS ++++++++++++++++++++

    async def connect_user(
        self, user_id: str, websocket: WebSocket, redis: Redis
    ) -> None:
        """
        Track user's active connections (supports multiple devices)
        """
        await redis.sadd(f"user-sockets-connected:{user_id}", websocket.client.port)  # type: ignore
        await redis.hset("online_users", user_id, "online")  # type: ignore
        await self._broadcast_presence(redis=redis)

    async def disconnect_user(
        self, user_id: str, websocket: WebSocket, redis: Redis
    ) -> None:
        """
        Removes User from Redis set
        """
        if await redis.scard(f"user-sockets-connected:{user_id}") == 0:  # type: ignore
            await redis.srem(f"user-sockets-connected:{user_id}", websocket.client.port)  # type: ignore
            await redis.hdel("online_users", user_id)  # type: ignore
            await self._broadcast_presence(redis=redis)

    async def _broadcast_presence(self, redis: Redis) -> None:
        """
        Broadcasts presence to online Users
        """
        online_users = await self.get_online_users(redis=redis)

        await redis.publish(
            "system_presence", json.dumps({"type": "presence", "users": online_users})
        )

    async def get_online_users(self, redis: Redis) -> typing.Set[str | None]:
        """
        Retrieves all online users
        """
        online_users: typing.Set[str | None] = await redis.hkeys("online_users")  # type: ignore
        return online_users

    # ++++++++++++++++++++++ DIRECT MESSAGES +++++++++++++++++++++++++++
    async def send_dm(self, direct_message: DirectMessage, redis: Redis) -> None:
        """
        Sends a Direct Message and Store in Redis Stream for history
        """

        await self.publish_message(
            channel=f"dm:{direct_message.conversation_id}",
            message=json.dumps(
                {
                    "type": "dm",
                    "from": direct_message.sender_id,
                    "to": direct_message.recipient_id,
                    "content": direct_message.content,
                    "media_type": direct_message.media_type,
                    "media_url": direct_message.media_url,
                    "created_at": direct_message.created_at.strftime(
                        "%04d-%02d-%02d %02H:%02M:02S"
                    ),
                    "is_edited": direct_message.is_edited,
                    "parent_message_id": direct_message.parent_message_id,
                    "conversation_id": direct_message.conversation_id,
                }
            ),
            redis=redis,
        )

    # +++++++++++++ roomS/CHANNELS +++++++++++++++++++++++
    async def join_room(self, user_id: str, room_id: str, redis: Redis) -> None:
        """
        Adds a user to a room
        """
        await redis.sadd(f"room:socket:{room_id}:members", user_id)  # type: ignore
        await redis.publish(
            f"room:{room_id}",
            json.dumps({"type": "system", "text": f"{user_id} joined"}),
        )  # type: ignore

    async def leave_room(self, user_id: str, room_id: str, redis: Redis) -> None:
        """
        Removes a user from room
        """
        await redis.srem(f"room:socket:{room_id}:members", user_id)  # type: ignore
        await redis.publish(
            f"room:{room_id}",
            json.dumps({"type": "system", "text": f"{user_id} left"}),
        )  # type: ignore

    async def send_room_message(
        self, user_id: str, room_id: str, message: str, redis: Redis
    ) -> None:
        """
        Sends message to rooms and Store in Redis Stream
        """
        await self.publish_message(
            f"room:{room_id}",
            json.dumps(
                {
                    "type": "message",
                    "from": user_id,
                    "text": message,
                }
            ),
            redis=redis,
        )

    # +++++++++++++++++++ SUBSCRIPTION HANDLER +++++++++++++++++++++++

    async def publish_message(self, channel: str, message: str, redis: Redis) -> None:
        """
        Publish messages
        """
        await redis.publish(channel, message)  # type: ignore

    async def subscribe(self, channels: typing.List[str], redis: Redis) -> PubSub:
        """
        Subscribe to channels
        """
        pubsub = redis.pubsub()
        await pubsub.subscribe(*channels)
        return pubsub


ws_redis_connection_manager = WSRedisConnectionManager()
