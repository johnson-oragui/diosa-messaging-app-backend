from fastapi import APIRouter

api_version_one = APIRouter(prefix="/api/v1")

from app.v1.auth import auth

api_version_one.include_router(router=auth)
