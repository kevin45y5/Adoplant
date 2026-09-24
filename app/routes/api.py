from fastapi import APIRouter

from app.routes.auth import router as auth_router
 feature/SCRUM-14-Notificaciones
from app.routes.notificaciones import router as notificaciones_router

from app.routes.usuarios import router as usuarios_router
from app.routes.admin_usuarios import router as admin_usuarios_router
 Main
from app.routes.solicitudes import router as solicitudes_router


api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
 feature/SCRUM-14-Notificaciones
api_router.include_router(notificaciones_router)

api_router.include_router(usuarios_router)
api_router.include_router(admin_usuarios_router)
 Main
api_router.include_router(solicitudes_router)
