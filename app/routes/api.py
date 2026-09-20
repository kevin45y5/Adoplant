from fastapi import APIRouter

from app.routes.auth import router as auth_router
from app.routes.usuarios import router as usuarios_router


api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(usuarios_router)
