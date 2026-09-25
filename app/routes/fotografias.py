from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Fotografia, Planta
from app.schemas import FotografiaCreate, FotografiaRespuesta
from app.dependencies import obtener_usuario_actual

router = APIRouter(prefix="/fotografias", tags=["Fotografías"])


@router.get("", response_model=List[FotografiaRespuesta])
def listar_fotografias(
    id_planta: int,
    db: Session = Depends(get_db),
):
    fotos = db.execute(
        select(Fotografia).where(Fotografia.id_planta == id_planta)
    ).scalars().all()
    return fotos


@router.post("", response_model=FotografiaRespuesta, status_code=status.HTTP_201_CREATED)
def subir_fotografia(
    datos: FotografiaCreate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual),
):
    planta = db.execute(
        select(Planta).where(Planta.id_planta == datos.id_planta)
    ).scalar_one_or_none()

    if planta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Planta no encontrada")

    if planta.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso")

    foto = Fotografia(**datos.model_dump())
    db.add(foto)
    db.commit()
    db.refresh(foto)
    return foto


@router.delete("/{id_fotografia}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_fotografia(
    id_fotografia: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(obtener_usuario_actual),
):
    foto = db.execute(
        select(Fotografia).where(Fotografia.id_fotografia == id_fotografia)
    ).scalar_one_or_none()

    if foto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fotografía no encontrada")

    planta = db.execute(
        select(Planta).where(Planta.id_planta == foto.id_planta)
    ).scalar_one_or_none()

    if planta and planta.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso")

    db.delete(foto)
    db.commit()
    return None