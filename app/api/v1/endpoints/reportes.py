from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import es_administrador, obtener_usuario_actual
from app.database import get_db
from app.models import Administrador, Reporte, Usuario
from app.schemas import (
    ReporteCrear,
    ReporteEstadoActualizar,
    ReporteRespuesta,
)


ESTADOS_REPORTE = ("EN_REVISION", "RESUELTO")

router = APIRouter()
admin_router = APIRouter()


def _validar_estado(valor: str | None) -> str | None:
    if valor is None:
        return None
    normalizado = valor.strip().upper()
    if normalizado not in ESTADOS_REPORTE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El estado debe ser 'EN_REVISION' o 'RESUELTO'",
        )
    return normalizado


@router.post(
    "",
    response_model=ReporteRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Reportar a un usuario",
)
def crear_reporte(
    datos: ReporteCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    """Registra un reporte en estado EN_REVISION.

    El reportante se obtiene del token. No permite reportarse a sí mismo
    ni reportar un usuario inexistente.
    """
    if datos.id_reportado == usuario.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes reportarte a ti mismo",
        )

    reportado = db.execute(
        select(Usuario).where(Usuario.id_usuario == datos.id_reportado)
    ).scalar_one_or_none()

    if reportado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario reportado no encontrado",
        )

    reporte = Reporte(
        motivo=datos.motivo.strip(),
        estado="EN_REVISION",
        id_reportante=usuario.id_usuario,
        id_reportado=datos.id_reportado,
        id_administrador=None,
    )
    db.add(reporte)
    db.commit()
    db.refresh(reporte)
    return reporte


@admin_router.get(
    "",
    response_model=list[ReporteRespuesta],
    summary="Buscar reportes",
)
def buscar_reportes(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_administrador),
    id_reportante: int | None = Query(default=None, gt=0),
    id_reportado: int | None = Query(default=None, gt=0),
    estado: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    """Permite a administradores buscar por usuario o estado, con paginación."""
    estado_normalizado = _validar_estado(estado)

    consulta = (
        select(Reporte)
        .order_by(Reporte.fecha_creacion.desc(), Reporte.id_reporte.desc())
        .offset(skip)
        .limit(limit)
    )

    if id_reportante is not None:
        consulta = consulta.where(Reporte.id_reportante == id_reportante)
    if id_reportado is not None:
        consulta = consulta.where(Reporte.id_reportado == id_reportado)
    if estado_normalizado is not None:
        consulta = consulta.where(Reporte.estado == estado_normalizado)

    return db.execute(consulta).scalars().all()


@admin_router.get(
    "/{id_reporte}",
    response_model=ReporteRespuesta,
    summary="Consultar reporte por ID",
)
def obtener_reporte(
    id_reporte: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_administrador),
):
    """Devuelve el detalle con reportante, reportado, motivo y fecha."""
    reporte = db.execute(
        select(Reporte).where(Reporte.id_reporte == id_reporte)
    ).scalar_one_or_none()

    if reporte is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reporte no encontrado",
        )

    return reporte


@admin_router.patch(
    "/{id_reporte}",
    response_model=ReporteRespuesta,
    summary="Actualizar estado del reporte",
)
def actualizar_estado_reporte(
    id_reporte: int,
    datos: ReporteEstadoActualizar,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_administrador),
):
    """Cambia entre EN_REVISION y RESUELTO y asocia al administrador que lo gestiona."""
    estado_normalizado = _validar_estado(datos.estado)

    reporte = db.execute(
        select(Reporte).where(Reporte.id_reporte == id_reporte)
    ).scalar_one_or_none()

    if reporte is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reporte no encontrado",
        )

    admin = db.execute(
        select(Administrador).where(
            Administrador.id_usuario == usuario.id_usuario
        )
    ).scalar_one_or_none()

    reporte.estado = estado_normalizado
    reporte.id_administrador = (
        admin.id_administrador if admin is not None else None
    )
    db.add(reporte)
    db.commit()
    db.refresh(reporte)
    return reporte
