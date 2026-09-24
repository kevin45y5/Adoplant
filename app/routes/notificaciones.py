"""Consulta de notificaciones propias."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import obtener_usuario_actual
from app.models import Usuario
from app.schemas import NotificacionRespuesta

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])

_CONSULTA_NOTIFICACIONES = text("""
    SELECT n.id_notificacion, n.tipo, n.mensaje, n.fecha_hora, n.leida,
           CASE
               WHEN s.id_solicitud IS NOT NULL
                AND (s.id_adoptante = :id_usuario OR planta_solicitud.id_usuario = :id_usuario)
               THEN s.id_solicitud
               ELSE NULL
           END AS id_solicitud_autorizada,
           CASE
               WHEN planta.id_planta IS NOT NULL
                AND ((planta.visible = TRUE AND planta.eliminada = FALSE)
                     OR planta.id_usuario = :id_usuario)
               THEN planta.id_planta
               ELSE NULL
           END AS id_planta_autorizada,
           CASE
               WHEN planta.id_planta IS NOT NULL
                AND ((planta.visible = TRUE AND planta.eliminada = FALSE)
                     OR planta.id_usuario = :id_usuario)
               THEN TRUE
               ELSE FALSE
           END AS planta_disponible
    FROM public.notificacion AS n
    LEFT JOIN public.solicitud_adopcion AS s
           ON s.id_solicitud = n.id_solicitud
    LEFT JOIN public.planta AS planta_solicitud
           ON planta_solicitud.id_planta = s.id_planta
    LEFT JOIN public.planta AS planta
           ON planta.id_planta = COALESCE(n.id_planta, s.id_planta)
    WHERE n.id_usuario = :id_usuario
""")


def _respuesta(row) -> NotificacionRespuesta:
    return NotificacionRespuesta(
        id_notificacion=row["id_notificacion"],
        tipo=row["tipo"],
        mensaje=row["mensaje"],
        fecha_hora=row["fecha_hora"],
        leida=row["leida"],
        referencias={
            "id_solicitud": row["id_solicitud_autorizada"],
            "id_planta": row["id_planta_autorizada"],
            "solicitud_disponible": row["id_solicitud_autorizada"] is not None,
            "planta_disponible": row["planta_disponible"],
        },
    )


@router.get("", response_model=list[NotificacionRespuesta])
def listar_notificaciones(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    filas = db.execute(
        text(str(_CONSULTA_NOTIFICACIONES) + " ORDER BY n.fecha_hora DESC, n.id_notificacion DESC"),
        {"id_usuario": usuario.id_usuario},
    ).mappings().all()
    return [_respuesta(fila) for fila in filas]


@router.get("/{id_notificacion}", response_model=NotificacionRespuesta)
def consultar_notificacion(
    id_notificacion: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    consulta = text(str(_CONSULTA_NOTIFICACIONES) + " AND n.id_notificacion = :id_notificacion")
    fila = db.execute(
        consulta,
        {"id_usuario": usuario.id_usuario, "id_notificacion": id_notificacion},
    ).mappings().one_or_none()
    if fila is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificacion no encontrada",
        )
    return _respuesta(fila)


@router.patch("/{id_notificacion}", response_model=NotificacionRespuesta)
def marcar_notificacion_leida(
    id_notificacion: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    actualizada = db.execute(
        text("""
            UPDATE public.notificacion
            SET leida = TRUE
            WHERE id_notificacion = :id_notificacion
              AND id_usuario = :id_usuario
            RETURNING id_notificacion
        """),
        {"id_notificacion": id_notificacion, "id_usuario": usuario.id_usuario},
    ).scalar_one_or_none()
    if actualizada is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificacion no encontrada",
        )
    db.commit()
    consulta = text(str(_CONSULTA_NOTIFICACIONES) + " AND n.id_notificacion = :id_notificacion")
    fila = db.execute(
        consulta,
        {"id_usuario": usuario.id_usuario, "id_notificacion": id_notificacion},
    ).mappings().one()
    return _respuesta(fila)