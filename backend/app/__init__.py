from fastapi import APIRouter

api_version_one = APIRouter(prefix="/api/v1")

from app.v1.auth.routes import auth
from app.v1.users.routes import *

api_version_one.include_router(router=auth)
api_version_one.include_router(router=users)
