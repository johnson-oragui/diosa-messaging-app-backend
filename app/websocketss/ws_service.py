"""
Websocket manager module
"""

from fastapi import WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from app.websocketss.ws_redis_connection_manager import ws_redis_connection_manager
from app.utils.task_logger import create_logger


logger = create_logger(":: WebsocketService ::")


class WebsocketService:
    """
    Websocket connection service
    """

    async def connect_to_websocket(
        self, websocket: WebSocket, subscribe_to: str, redis: Redis
    ) -> None:
        """
        Manages connections
        """
        claims: dict = websocket.state.claims
        current_user_id = claims.get("user_id", "")

        await websocket.accept()

        await ws_redis_connection_manager.connect_user(
            websocket=websocket, user_id=current_user_id, redis=redis
        )
        # Subscribe to requested channels
        channels = ["system_presence"] + subscribe_to.split(",")

        pubsub = await ws_redis_connection_manager.subscribe(
            channels=channels, redis=redis
        )

        try:
            # Send initial presence data
            online_users = await redis.hkeys("online_users")  # type: ignore
            await websocket.send_json({"type": "presence", "users": online_users})

            while True:
                # Forward messages from Redis to WebSocket
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        await websocket.send_text(message["data"])

        except WebSocketDisconnect as exc:
            logger.error("Websocket disconnection: %s", str(exc))
            await ws_redis_connection_manager.disconnect_user(
                user_id=current_user_id, websocket=websocket, redis=redis
            )


websocket_service = WebsocketService()
