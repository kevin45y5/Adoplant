from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Categoria, Planta, Usuario
from app.schemas import PlantaCreate, PlantaRespuesta, PlantaUpdate
from app.security import obtener_usuario_actual

router = APIRouter(prefix="/plantas", tags=["Plantas"])


@router.get("/mias", response_model=List[PlantaRespuesta])
def consultar_mias(
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
    busqueda: Optional[str] = Query(None, max_length=100),
    estado: Optional[str] = Query(None),
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
):
    consulta = select(Planta).where(Planta.id_usuario == usuario_actual.id_usuario)

    if busqueda:
        consulta = consulta.where(Planta.nombre.ilike(f"%{busqueda}%"))
    if estado:
        consulta = consulta.where(Planta.estado_planta == estado)

    offset = (pagina - 1) * limite
    total = db.execute(consulta).scalars().unique().count()
    plantas = db.execute(
        consulta.offset(offset).limit(limite)
    ).scalars().unique().all()

    return plantas


@router.patch("/{id_planta}", response_model=PlantaRespuesta)
def modificar_planta(
    id_planta: int,
    datos: PlantaUpdate,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    planta = db.execute(
        select(Planta).where(Planta.id_planta == id_planta)
    ).scalar_one_or_none()

    if planta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planta no encontrada",
        )

    if planta.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar esta publicación",
        )

    if planta.estado_planta != "DISPONIBLE" or not planta.visible or planta.eliminada:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo se pueden editar publicaciones DISPONIBLES, visibles y no eliminadas",
        )

    if datos.id_categoria is not None and datos.id_categoria != planta.id_categoria:
        categoria = db.execute(
            select(Categoria).where(
                Categoria.id_categoria == datos.id_categoria
            )
        ).scalar_one_or_none()
        if categoria is None or categoria.estado != "ACTIVA":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La categoría debe existir y estar ACTIVA",
            )

    datos_dict = datos.model_dump(exclude_unset=True)

    for campo, valor in datos_dict.items():
        setattr(planta, campo, valor)

    try:
        db.commit()
        db.refresh(planta)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar la publicación",
        )

    return planta


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
