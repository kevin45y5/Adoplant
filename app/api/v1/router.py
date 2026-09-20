from fastapi import APIRouter

from app.api.v1.endpoints import reportes

api_v1_router = APIRouter()
api_v1_router.include_router(
    reportes.router,
    prefix="/reportes",
    tags=["Reportes"],
)
api_v1_router.include_router(
    reportes.admin_router,
    prefix="/admin/reportes",
    tags=["Administración"],
)
