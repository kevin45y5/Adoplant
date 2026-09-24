"""Envio, consulta autorizada y retiro de solicitudes de adopcion."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import obtener_usuario_actual
from app.models import Usuario
from app.schemas import SolicitudCrear, SolicitudRespuesta
from app.services.notificaciones import registrar_notificacion

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes"])


@router.post("", response_model=SolicitudRespuesta, status_code=status.HTTP_201_CREATED)
def enviar_solicitud(
    datos: SolicitudCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    planta = db.execute(
        text("""
            SELECT id_planta, id_usuario, nombre, estado::text AS estado,
                   visible, eliminada
            FROM public.planta
            WHERE id_planta = :id_planta
            FOR UPDATE
        """),
        {"id_planta": datos.id_planta},
    ).mappings().one_or_none()
    if planta is None:
        raise HTTPException(status_code=404, detail="Planta no encontrada")
    if (planta["estado"] != "DISPONIBLE" or not planta["visible"]
            or planta["eliminada"]):
        raise HTTPException(status_code=409, detail="La planta no esta disponible")
    if planta["id_usuario"] == usuario.id_usuario:
        raise HTTPException(status_code=409, detail="No puedes solicitar tu propia planta")

    try:
        fila = db.execute(
            text("""
                INSERT INTO public.solicitud_adopcion
                    (mensaje, estado, id_planta, id_adoptante)
                VALUES (:mensaje, 'PENDIENTE', :id_planta, :id_adoptante)
                RETURNING id_solicitud, mensaje, estado::text AS estado,
                          fecha_solicitud, id_planta, id_adoptante
            """),
            {
                "mensaje": datos.mensaje,
                "id_planta": datos.id_planta,
                "id_adoptante": usuario.id_usuario,
            },
        ).mappings().one()
        registrar_notificacion(
            db,
            id_usuario=planta["id_usuario"],
            tipo="NUEVA_SOLICITUD",
            mensaje=f"Recibiste una solicitud para tu planta {planta['nombre']}",
            id_planta=datos.id_planta,
            id_solicitud=fila["id_solicitud"],
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una solicitud activa para esta planta",
        ) from None

    return SolicitudRespuesta(**dict(fila))


@router.get("/{id_solicitud}", response_model=SolicitudRespuesta)
def consultar_solicitud(
    id_solicitud: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    fila = db.execute(
        text("""
            SELECT s.id_solicitud, s.mensaje, s.estado::text AS estado,
                   s.fecha_solicitud, s.id_planta, s.id_adoptante
            FROM public.solicitud_adopcion AS s
            JOIN public.planta AS p ON p.id_planta = s.id_planta
            WHERE s.id_solicitud = :id_solicitud
              AND (s.id_adoptante = :id_usuario OR p.id_usuario = :id_usuario)
        """),
        {"id_solicitud": id_solicitud, "id_usuario": usuario.id_usuario},
    ).mappings().one_or_none()
    if fila is None:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return SolicitudRespuesta(**dict(fila))


@router.delete("/{id_solicitud}", status_code=status.HTTP_204_NO_CONTENT)
def retirar_solicitud(
    id_solicitud: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    fila = db.execute(
        text("""
            SELECT s.id_solicitud, s.id_planta, s.id_adoptante, s.estado::text AS estado, p.nombre
            FROM public.solicitud_adopcion AS s
            JOIN public.planta AS p ON p.id_planta = s.id_planta
            WHERE s.id_solicitud = :id_solicitud
            FOR UPDATE OF s
        """),
        {"id_solicitud": id_solicitud},
    ).mappings().one_or_none()
    if fila is None or fila["id_adoptante"] != usuario.id_usuario:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if fila["estado"] != "PENDIENTE":
        raise HTTPException(status_code=409, detail="Solo se pueden retirar solicitudes pendientes")

    tiene_adopcion = db.execute(
        text("SELECT 1 FROM public.adopcion WHERE id_solicitud = :id_solicitud"),
        {"id_solicitud": id_solicitud},
    ).scalar_one_or_none()
    if tiene_adopcion is not None:
        raise HTTPException(status_code=409, detail="La solicitud ya tiene una adopcion asociada")

    try:
        db.execute(
            text("""
                UPDATE public.notificacion
                SET id_solicitud = NULL,
                    mensaje = :mensaje
                WHERE id_solicitud = :id_solicitud
            """),
            {
                "id_solicitud": id_solicitud,
                "mensaje": f"La solicitud para la planta {fila['nombre']} fue retirada por quien la envio.",
            },
        )
        db.execute(
            text("DELETE FROM public.solicitud_adopcion WHERE id_solicitud = :id_solicitud"),
            {"id_solicitud": id_solicitud},
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo retirar la solicitud porque tiene una adopcion asociada",
        ) from None
