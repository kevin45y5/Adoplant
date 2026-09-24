from fastapi import APIRouter

from app.routes.auth import router as auth_router
from app.routes.notificaciones import router as notificaciones_router
from app.routes.solicitudes import router as solicitudes_router


api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(notificaciones_router)
api_router.include_router(solicitudes_router)
