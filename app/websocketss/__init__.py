from fastapi import APIRouter

from app.websocketss.ws_route import ws_router

websocket_router = APIRouter(prefix="/chats")

websocket_router.include_router(ws_router)
