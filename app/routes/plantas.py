from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Categoria, Planta, Usuario
from app.schemas import PlantaCreate, PlantaRespuesta
from app.security import obtener_usuario_actual

router = APIRouter(prefix="/plantas", tags=["Plantas"])


@router.post("/", response_model=PlantaRespuesta, status_code=status.HTTP_201_CREATED)
def crear_planta(
    datos: PlantaCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    categoria = db.execute(
        select(Categoria).where(Categoria.id_categoria == datos.id_categoria)
    ).scalar_one_or_none()

    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada",
        )

    planta = Planta(
        **datos.model_dump(),
        id_usuario=usuario_actual.id_usuario,
    )

    db.add(planta)
    db.commit()
    db.refresh(planta)

    return planta