from typing import Annotated
import json
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    Query,
    Request
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.v1.chats.websocket import (
    ws_connection_manager,
)
from app.utils.task_logger import create_logger
from app.v1.auth.dependencies import (
    check_for_access_token,
    get_current_active_user,
)
from app.database.session import get_session
from app.v1.rooms.services import room_service

logger = create_logger("Web Socket Route")

chats = APIRouter(prefix="/ws")


@chats.websocket("/{room_id}")
async def public_chat(websocket: WebSocket,
                             room_id: str,
                             token: Annotated[str, Depends(check_for_access_token)],
                             session: Annotated[AsyncSession, Depends(get_session)],
                             chat_type: str = Query(examples=["public"])):
    """
    Connects to websocket
    """
    user = get_current_active_user(
        access_token=token,
        request=websocket,
        session=session)

    await ws_connection_manager.connect(user.id, websocket)

    try:
        while True:
            data = await websocket.receive()
            # check if data is str or file(image/video) before sending.
            if "text" in data:
                message: str = data["text"]

                await ws_connection_manager.broadcast_to_room(
                    room_id,
                    user.id,
                    message,
                    chat_type,
                    session
                )
    except WebSocketDisconnect as exc:
        logger.error(msg=f"Client #{user.id} disconnected: {exc}")

        await ws_connection_manager.broadcast_to_room(
            room_id,
            user.id,
            f"{user.username} left the chat",
            chat_type,
            session
        )
        await ws_connection_manager.handle_disconnection(websocket, user.id)

@chats.websocket("/private/{room_id}")
async def private_chat(websocket: WebSocket,
                             room_id: str,
                             token: Annotated[str, Depends(check_for_access_token)],
                             session: Annotated[AsyncSession, Depends(get_session)],
                             chat_type: str = Query(examples=["private"])):
    await websocket.accept()

@chats.websocket("/ws/direct_message")
async def direct_message_chat(websocket: WebSocket,
                              room_id: str,
                             token: Annotated[str, Depends(check_for_access_token)],
                             session: Annotated[AsyncSession, Depends(get_session)],
                             chat_type: str = Query(examples=["direct-message"])):
    await websocket.accept()

# @chats.websocket("/direct-message/{recipient_id}")
# async def direct_message_endpoint(websocket: WebSocket, recipient_id: int):
#     await ws_connection_manager.connect(websocket)
#     try:
#         while True:
#             data = await websocket.receive_text()
#             # Assume data is a JSON string with a message and recipient
#             message_data = json.loads(data)
#             message = message_data["message"]
#             recipient_id = message_data["recipient_id"]

#             # Find the recipient's WebSocket connection
#             recipient_connection = next((conn for conn in ws_connection_manager.active_connections if conn.client_id == recipient_id), None)

#             if recipient_connection:
#                 await ws_connection_manager.send_personal_text(
#                     f"Direct message from {websocket.client_id}: {message}",
#                     websocket
#                 )
#             else:
#                 await ws_connection_manager.send_personal_text(
#                     "User not found",
#                     websocket
#                 )
#     except WebSocketDisconnect:
#         ws_connection_manager.disconnect(websocket)
