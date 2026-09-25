from fastapi import APIRouter

from app.routes.auth import router as auth_router
from app.routes.fotografias import router as fotografias_router
from app.routes.plantas import router as plantas_router
from app.routes.usuarios import router as usuarios_router
from app.routes.admin_usuarios import router as admin_usuarios_router
from app.routes.solicitudes import router as solicitudes_router


api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(fotografias_router)
api_router.include_router(plantas_router)
api_router.include_router(usuarios_router)
api_router.include_router(admin_usuarios_router)
api_router.include_router(solicitudes_router)
