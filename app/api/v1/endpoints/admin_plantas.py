from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario, Planta
from app.schemas.planta import PlantaRespuesta, PlantaModeracion
from app.api.deps import obtener_usuario_actual, es_administrador

router = APIRouter(tags=["Administración"])


@router.get(
    "",
    response_model=list[PlantaRespuesta],
    summary="Listar todas las publicaciones administrativas",
)
def listar_plantas_admin(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_administrador),
    q: str | None = Query(default=None, description="Buscar por nombre de planta"),
    skip: int = Query(default=0, ge=0, description="Registro inicial para paginación"),
    limit: int = Query(default=100, ge=1, le=500, description="Máximo de registros a devolver"),
):
    """Listar todas las publicaciones, incluidas ocultas o eliminadas lógicamente.
    Requiere rol de administrador. No expone chats ni puntos de encuentro."""
    consulta = select(Planta).offset(skip).limit(limit)

    if q:
        consulta = consulta.where(Planta.nombre.ilike(f"%{q}%"))

    plantas = db.execute(consulta).scalars().all()
    return plantas


@router.get(
    "/{id_planta}",
    response_model=PlantaRespuesta,
    summary="Consultar planta por ID (administrador)",
)
def obtener_planta_admin(
    id_planta: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_administrador),
):
    """Consultar una publicación por ID, incluyendo las ocultas o eliminadas.
    Requiere rol de administrador. No expone chats ni puntos de encuentro."""
    planta = db.execute(
        select(Planta).where(Planta.id_planta == id_planta)
    ).scalar_one_or_none()

    if planta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planta no encontrada",
        )

    return planta


@router.patch(
    "/{id_planta}/moderacion",
    response_model=PlantaRespuesta,
    summary="Moderar publicación",
)
def moderar_planta(
    id_planta: int,
    datos: PlantaModeracion,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(es_administrador),
):
    """Aplicar borrado u ocultamiento lógico a una publicación.
    Requiere motivo no vacío y rol de administrador.
    Usa los campos visible=False y/o eliminada=True.
    Registra la fecha, ID del administrador y el motivo.
    Conserva fotos, solicitudes y historial de adopciones.
    Dispara notificación al donante explicando el motivo."""
    planta = db.execute(
        select(Planta).where(Planta.id_planta == id_planta)
    ).scalar_one_or_none()

    if planta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planta no encontrada",
        )

    # Aplicar moderación
    motivo = datos.motivo.strip() if datos.motivo else None

    if not motivo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El motivo de moderación es obligatorio",
        )

    planta.visible = datos.visible if datos.visible is not None else False
    planta.eliminada = datos.eliminada if datos.eliminada is not None else True
    planta.motivo_moderacion = motivo
    planta.fecha_moderacion = datos.fecha_moderacion or datetime.now(timezone.utc)
    planta.id_administrador_moderador = usuario.id_usuario

    db.add(planta)
    db.commit()
    db.refresh(planta)

    # TODO: Disparar notificación al donante usando el servicio de notificaciones
    # from app.services.notificaciones import crear_notificacion
    # crear_notificacion(
    #     id_usuario=planta.id_usuario,
    #     tipo="moderacion",
    #     mensaje=f"Tu publicación '{planta.nombre}' ha sido {'ocultada' if not planta.eliminada else 'retirada'} por el motivo: {motivo}",
    #     id_planta=planta.id_planta,
    # )

    return planta