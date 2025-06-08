"""
Router Init
"""

from fastapi import APIRouter

from app.route.v1.auth_route import auth_router
from app.route.v1.direct_conversation_route import direct_conversation_router
from app.route.v1.direct_message_route import direct_message_router
from app.route.v1.media_upload_route import media_upload_router

api_version_one = APIRouter(prefix="/api/v1")

api_version_one.include_router(auth_router)
api_version_one.include_router(direct_conversation_router)
api_version_one.include_router(direct_message_router)
api_version_one.include_router(media_upload_router)
