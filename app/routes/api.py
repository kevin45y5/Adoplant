from fastapi import APIRouter

from app.routes.auth import router as auth_router
from app.routes.plantas import router as plantas_router
from app.routes.fotografias import router as fotografias_router


api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(plantas_router)
api_router.include_router(fotografias_router)
