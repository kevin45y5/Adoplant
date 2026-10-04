from fastapi import APIRouter

from app.routes.auth import router as auth_router
from app.routes.categorias import router as categorias_router
from app.routes.usuarios import router as usuarios_router
from app.routes.admin_usuarios import router as admin_usuarios_router
from app.routes.solicitudes import router as solicitudes_router
from app.routes.plantas import router as plantas_router
from app.routes.fotografias import router as fotografias_router
from app.routes.notificaciones import router as notificaciones_router
from app.routes.chats import router as chats_router
from app.routes.puntos_encuentro import router as puntos_router
from app.routes.adopciones import router as adopciones_router
from app.routes.admin_panel import router as admin_panel_router
from app.routes.admin_plantas import router as admin_plantas_router
from app.routes.reportes import router as reportes_router, admin_router as admin_reportes_router

api_router = APIRouter(prefix="/api")
for router in (
    auth_router, categorias_router, usuarios_router, admin_usuarios_router, solicitudes_router,
    plantas_router, fotografias_router, notificaciones_router, chats_router, adopciones_router,
    admin_plantas_router, reportes_router, admin_reportes_router, admin_panel_router, puntos_router,
):
    api_router.include_router(router)
