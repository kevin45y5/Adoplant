from fastapi import APIRouter

from app.api.v1.endpoints import chats

api_v1_router = APIRouter()
api_v1_router.include_router(
    chats.router,
    prefix="/chats",
    tags=["Chat"],
)
