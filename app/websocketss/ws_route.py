"""
Websocket route module
"""

import typing
from fastapi import APIRouter, WebSocket, Query, Depends
from redis.asyncio import Redis

from app.websocketss.ws_service import websocket_service
from app.core.security import validate_ws_logout_status
from app.database.redis_db import get_redis_client

ws_router = APIRouter(prefix="/ws", tags=["WEBSOCKET"])


@ws_router.websocket(path="", dependencies=[Depends(validate_ws_logout_status)])
async def connect_to_websocket(
    websocket: WebSocket,
    redis: typing.Annotated[Redis, Depends(get_redis_client)],
    subscribe_to: str = Query(
        description="Comma-separated forums/DMs (e.g., forum:general,dm:user456"
    ),
):
    """
    Websocket router
    """
    await websocket_service.connect_to_websocket(
        websocket=websocket, subscribe_to=subscribe_to, redis=redis
    )
