from fastapi import APIRouter

from app.route.v1.auth_route import auth_router

api_version_one = APIRouter(prefix="/api/v1")

api_version_one.include_router(auth_router)
