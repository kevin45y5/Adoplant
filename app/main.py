import logging
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.routes.api import api_router

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
VIEWS_DIR = BASE_DIR / "views"
INDEX_PATH = VIEWS_DIR / "index.html"

app = FastAPI(
    title="AdopPlant API",
    description="API para la adopción de plantas.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/views", StaticFiles(directory=VIEWS_DIR), name="views")


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(request, error):
    errores = []

    for detalle in error.errors():
        errores.append(
            {
                "loc": list(detalle["loc"]),
                "msg": detalle["msg"],
                "type": detalle["type"],
            }
        )

    return JSONResponse(
        status_code=422,
        content={"detail": errores},
    )


@app.get("/")
def inicio():
    return {"mensaje": "La API de AdopPlant está funcionando"}


@app.get("/", response_class=FileResponse, include_in_schema=False)
def inicio():
    return FileResponse(INDEX_PATH)


@api_router.get("/prueba-db", tags=["Pruebas"])
def probar_base_datos(db: Session = Depends(get_db)):
    try:
        nombre_bd = db.execute(
            text("SELECT current_database()")
        ).scalar_one()

        total_usuarios = db.execute(
            text("SELECT COUNT(*) FROM public.usuario")
        ).scalar_one()

        return {
            "mensaje": "Conexión con PostgreSQL correcta",
            "base_de_datos": nombre_bd,
            "total_usuarios": total_usuarios,
        }

    except SQLAlchemyError:
        logger.exception("Falló la prueba de PostgreSQL")

        raise HTTPException(
            status_code=503,
            detail="No se pudo consultar la base de datos",
        ) from None


app.include_router(api_router)