import logging

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database import get_db
from app.routes.api import api_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AdopPlant API",
    description="API para la adopción de plantas.",
    version="0.1.0",
)


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


@app.get("/prueba-db", include_in_schema=False)
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
