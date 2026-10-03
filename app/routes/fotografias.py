from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Fotografia, Planta
from app.schemas import FotografiaCreate, FotografiaRespuesta
from app.dependencies import obtener_usuario_actual

router = APIRouter(prefix="/fotografias", tags=["Fotografías"])


def _validar_edicion(planta, usuario):
    if planta is None:
        raise HTTPException(404, "Planta no encontrada")
    if planta.id_usuario != usuario.id_usuario:
        raise HTTPException(403, "No tienes permiso")
    if planta.estado_planta != "DISPONIBLE" or not planta.visible or planta.eliminada:
        raise HTTPException(403, "Solo puedes modificar fotos de una planta disponible y visible")


@router.get("", response_model=List[FotografiaRespuesta])
def listar_fotografias(
    id_planta: int,
    db: Session = Depends(get_db),
):
    planta = db.get(Planta, id_planta)
    if planta is None or not planta.visible or planta.eliminada:
        raise HTTPException(status_code=404, detail="Planta no encontrada")
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
        select(Planta).where(Planta.id_planta == datos.id_planta).with_for_update()
    ).scalar_one_or_none()

    if planta is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Planta no encontrada")

    if planta.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso")

    _validar_edicion(planta, usuario_actual)
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
        select(Planta).where(Planta.id_planta == foto.id_planta).with_for_update()
    ).scalar_one_or_none()

    if planta and planta.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso")

    _validar_edicion(planta, usuario_actual)
    otra = db.scalar(select(Fotografia.id_fotografia).where(
        Fotografia.id_planta == foto.id_planta,
        Fotografia.id_fotografia != id_fotografia,
    ).limit(1))
    if otra is None:
        raise HTTPException(409, "La publicación debe conservar al menos una fotografía")
    db.delete(foto)
    db.commit()
    return None
