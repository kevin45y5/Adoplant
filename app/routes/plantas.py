from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Categoria, Planta, Usuario
from app.schemas import CatalogoResponse, PlantaCreate, PlantaRespuesta, PlantaUpdate
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


@router.get("/", response_model=CatalogoResponse)
def catalogo(
    db: Session = Depends(get_db),
    busqueda: Optional[str] = Query(None, max_length=100),
    tamano: Optional[str] = Query(None, max_length=50),
    nivel_cuidado: Optional[str] = Query(None, max_length=50),
    orden: str = Query("fecha_publicacion_desc", pattern="^(fecha_publicacion|nombre)(_desc|_asc)?$"),
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
):
    consulta = select(Planta).where(
        Planta.estado_planta == "DISPONIBLE",
        Planta.visible.is_(True),
        Planta.eliminada.is_(False),
    )

    if busqueda and busqueda.strip():
        consulta = consulta.where(Planta.nombre.ilike(f"%{busqueda.strip()}%"))
    if tamano and tamano.strip():
        consulta = consulta.where(Planta.tamano == tamano.strip())
    if nivel_cuidado and nivel_cuidado.strip():
        consulta = consulta.where(Planta.nivel_cuidado == nivel_cuidado.strip())

    columna_orden = Planta.fecha_publicacion if orden.startswith("fecha") else Planta.nombre
    direccion = "desc" if orden.endswith("_desc") else "asc"
    if direccion == "desc":
        consulta = consulta.order_by(columna_orden.desc())
    else:
        consulta = consulta.order_by(columna_orden.asc())

    total = db.execute(consulta).scalars().unique().count()
    total_paginas = (total + limite - 1) // limite

    offset = (pagina - 1) * limite
    plantas = db.execute(
        consulta.offset(offset).limit(limite)
    ).scalars().unique().all()

    return CatalogoResponse(
        items=plantas,
        total=total,
        pagina=pagina,
        limite=limite,
        total_paginas=total_paginas,
        tiene_mas=pagina < total_paginas,
    )


@router.get("/{id_planta}", response_model=PlantaRespuesta)
def consultar_planta(
    id_planta: int,
    db: Session = Depends(get_db),
):
    planta = db.execute(
        select(Planta)
        .options(joinedload(Planta.categoria))
        .where(Planta.id_planta == id_planta)
    ).scalar_one_or_none()

    if planta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planta no encontrada",
        )

    if not planta.visible or planta.eliminada:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta publicación no está disponible",
        )

    fotografia_url = db.execute(
        text("SELECT url FROM public.fotografia WHERE id_planta = :id ORDER BY fecha_carga ASC LIMIT 1")
    ).params(id=id_planta).scalar_one_or_none()

    planta.fotografia_url = fotografia_url
    planta.puede_solicitar = planta.estado_planta == "DISPONIBLE"

    return planta


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


@router.delete("/{id_planta}")
def retirar_planta(
    id_planta: int,
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
            detail="No tienes permiso para retirar esta publicación",
        )

    if planta.estado_planta != "DISPONIBLE" or not planta.visible or planta.eliminada:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo se pueden retirar publicaciones DISPONIBLES, visibles y no eliminadas",
        )

    adopcion_en_curso = db.execute(
        text("SELECT 1 FROM public.adopcion WHERE id_planta = :id AND estado IN ('EN_PROCESO', 'COMPLETADA') LIMIT 1")
    ).params(id=id_planta).scalar_one_or_none()

    if adopcion_en_curso is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se puede retirar una planta con adopción en curso o completada",
        )

    try:
        db.execute(
            text("UPDATE public.solicitud_adopcion SET estado = 'RECHAZADA' WHERE id_planta = :id AND estado = 'PENDIENTE'")
        ).params(id=id_planta)

        planta.eliminada = True
        planta.visible = False

        db.commit()
        db.refresh(planta)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al retirar la publicación",
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
