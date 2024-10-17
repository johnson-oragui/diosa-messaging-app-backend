from fastapi import APIRouter

api_version_one = APIRouter(prefix="/api/v1")

from app.v1.auth.routes import auth
from app.v1.users.routes import *
from app.v1.chats.routes import chats
from app.v1.rooms.routes import *

api_version_one.include_router(router=auth)
api_version_one.include_router(router=users)
api_version_one.include_router(router=chats)
api_version_one.include_router(router=rooms)
