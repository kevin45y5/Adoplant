"""Entrega y recepción privadas, confirmadas independientemente por cada participante."""
from datetime import datetime, timezone
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import obtener_usuario_actual
from app.models import Adopcion, Fotografia, Notificacion, Planta, Usuario

router = APIRouter(prefix="/adopciones", tags=["Adopciones"])
logger = logging.getLogger(__name__)


def participantes(usuario):
    return or_(Adopcion.id_donante == usuario.id_usuario,
               Adopcion.id_adoptante == usuario.id_usuario)


def respuesta(db, adopcion, usuario):
    planta = db.get(Planta, adopcion.id_planta)
    donante = db.get(Usuario, adopcion.id_donante)
    adoptante = db.get(Usuario, adopcion.id_adoptante)
    foto = db.scalar(select(Fotografia.url).where(
        Fotografia.id_planta == adopcion.id_planta).order_by(Fotografia.id_fotografia).limit(1))
    def nombre(persona):
        return f"{persona.nombre} {persona.apellido}".strip() if persona else "Participante"
    return {
        "id_adopcion": adopcion.id_adopcion, "id_planta": adopcion.id_planta,
        "id_solicitud": adopcion.id_solicitud, "estado": adopcion.estado,
        "rol": "donante" if usuario.id_usuario == adopcion.id_donante else "adoptante",
        "fecha_entrega": adopcion.fecha_entrega.astimezone(timezone.utc) if adopcion.fecha_entrega else None,
        "fecha_recepcion": adopcion.fecha_recepcion.astimezone(timezone.utc) if adopcion.fecha_recepcion else None,
        "donante": nombre(donante), "adoptante": nombre(adoptante),
        "planta": {"nombre": planta.nombre if planta else "Planta",
                   "fotografia_url": foto, "descripcion": planta.descripcion if planta else None,
                   "ubicacion": planta.ubicacion if planta else None,
                   "tamano": planta.tamano if planta else None,
                   "luz": planta.necesidad_luz if planta else None,
                   "riego": planta.necesidad_agua if planta else None},
    }


@router.get("")
def listar(db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    rows = db.scalars(select(Adopcion).where(participantes(usuario)).order_by(Adopcion.id_adopcion.desc())).all()
    return [respuesta(db, row, usuario) for row in rows]


@router.get("/{id_adopcion}")
def detalle(id_adopcion: int, db: Session = Depends(get_db),
            usuario: Usuario = Depends(obtener_usuario_actual)):
    row = db.scalar(select(Adopcion).where(Adopcion.id_adopcion == id_adopcion, participantes(usuario)))
    if row is None:
        raise HTTPException(404, "Adopción no encontrada")
    return respuesta(db, row, usuario)


def aplicar_confirmacion(adopcion, planta, usuario_id, ahora):
    """La identidad autenticada elige el campo; un reintento no modifica su fecha."""
    if usuario_id not in (adopcion.id_donante, adopcion.id_adoptante):
        raise HTTPException(404, "Adopción no encontrada")
    campo = "fecha_entrega" if usuario_id == adopcion.id_donante else "fecha_recepcion"
    if getattr(adopcion, campo) is not None or adopcion.estado == "COMPLETADA":
        return False
    setattr(adopcion, campo, ahora)
    if adopcion.fecha_entrega is not None and adopcion.fecha_recepcion is not None:
        adopcion.estado = "COMPLETADA"
        planta.estado = "ADOPTADA"
    return True


@router.post("/{id_adopcion}/confirmar")
def confirmar(id_adopcion: int, db: Session = Depends(get_db),
              usuario: Usuario = Depends(obtener_usuario_actual)):
    return _confirmar(id_adopcion, db, usuario)


@router.post("/{id_adopcion}/entrega")
def confirmar_entrega(id_adopcion: int, db: Session = Depends(get_db),
                     usuario: Usuario = Depends(obtener_usuario_actual)):
    return _confirmar(id_adopcion, db, usuario, "donante")


@router.post("/{id_adopcion}/recepcion")
def confirmar_recepcion(id_adopcion: int, db: Session = Depends(get_db),
                       usuario: Usuario = Depends(obtener_usuario_actual)):
    return _confirmar(id_adopcion, db, usuario, "adoptante")


def _confirmar(id_adopcion, db, usuario, rol_requerido=None):
    try:
        planta_id = db.scalar(select(Adopcion.id_planta).where(
            Adopcion.id_adopcion == id_adopcion, participantes(usuario)))
        if planta_id is None:
            raise HTTPException(404, "Adopción no encontrada")
        # Igual orden de bloqueo que las operaciones de publicación: planta, adopción.
        planta = db.scalar(select(Planta).where(Planta.id_planta == planta_id)
                           .with_for_update().execution_options(populate_existing=True))
        row = db.scalar(select(Adopcion).where(Adopcion.id_adopcion == id_adopcion, participantes(usuario))
                        .with_for_update().execution_options(populate_existing=True))
        if row is None or planta is None:
            raise HTTPException(404, "Adopción no encontrada")
        rol = "donante" if usuario.id_usuario == row.id_donante else "adoptante"
        if rol_requerido is not None and rol != rol_requerido:
            raise HTTPException(403, "Esta confirmación corresponde al otro participante")
        if aplicar_confirmacion(row, planta, usuario.id_usuario, datetime.now(timezone.utc)):
            entregada = usuario.id_usuario == row.id_donante
            destinatarios = [row.id_donante, row.id_adoptante] if row.estado == "COMPLETADA" else [row.id_adoptante if entregada else row.id_donante]
            mensaje = (f"Ambas personas confirmaron la entrega de {planta.nombre}. Adopción completada."
                       if row.estado == "COMPLETADA" else
                       f"{'El donante confirmó la entrega' if entregada else 'El adoptante confirmó la recepción'} de {planta.nombre}. Falta tu confirmación en Mis adopciones.")
            for destinatario in destinatarios:
                db.add(Notificacion(tipo="ADOPCION_COMPLETADA" if row.estado == "COMPLETADA" else "CONFIRMACION_ENTREGA",
                                    mensaje=mensaje, id_usuario=destinatario,
                                    id_planta=row.id_planta, id_solicitud=row.id_solicitud))
        resultado = respuesta(db, row, usuario)
        db.commit()
        return resultado
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        logger.exception("No se pudo confirmar la entrega")
        raise HTTPException(503, "No se pudo guardar la confirmación. Consulta el estado antes de reintentar.") from None
