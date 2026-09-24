 feature/SCRUM-14-Notificaciones
"""Envio, consulta autorizada y retiro de solicitudes de adopcion."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from sqlalchemy import select, text, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
 Main
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import obtener_usuario_actual
 feature/SCRUM-14-Notificaciones
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

from app.models import Notificacion, Planta, SolicitudAdopcion, Usuario
from app.schemas import SolicitudCrear, SolicitudMensaje, SolicitudRespuesta
from app.services.notificaciones import notificar_solicitud

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/solicitudes", tags=["Solicitudes"])
IdSolicitud = Annotated[int, Path(gt=0, le=2_147_483_647)]


@router.get("", response_model=list[SolicitudRespuesta])
def listar_solicitudes(
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
    tipo: Literal["enviadas", "recibidas"] = "enviadas",
    estado: Literal["PENDIENTE", "ACEPTADA", "RECHAZADA"] | None = None,
    id_planta: Annotated[int | None, Query(gt=0, le=2_147_483_647)] = None,
    limite: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """Lista privada, ordenada de más reciente a más antigua, con filtros y paginación."""
    consulta = select(SolicitudAdopcion).join(
        Planta, Planta.id_planta == SolicitudAdopcion.id_planta)
    condicion = (SolicitudAdopcion.id_adoptante == usuario.id_usuario
                 if tipo == "enviadas" else Planta.id_usuario == usuario.id_usuario)
    consulta = consulta.where(condicion)
    if estado is not None:
        consulta = consulta.where(SolicitudAdopcion.estado == estado)
    if id_planta is not None:
        consulta = consulta.where(SolicitudAdopcion.id_planta == id_planta)
    return db.scalars(consulta.order_by(
        SolicitudAdopcion.fecha_solicitud.desc(), SolicitudAdopcion.id_solicitud.desc()
    ).limit(limite).offset(offset)).all()


@router.get("/{id_solicitud}", response_model=SolicitudRespuesta,
            responses={404: {"description": "Solicitud inexistente o ajena"}})
def consultar_solicitud(id_solicitud: IdSolicitud,
                       usuario: Usuario = Depends(obtener_usuario_actual),
                       db: Session = Depends(get_db)):
    fila = db.execute(select(SolicitudAdopcion, Planta.id_usuario).join(
        Planta, Planta.id_planta == SolicitudAdopcion.id_planta).where(
        SolicitudAdopcion.id_solicitud == id_solicitud)).first()
    if fila is None or usuario.id_usuario not in (fila[0].id_adoptante, fila[1]):
        raise HTTPException(404, "Solicitud no encontrada")
    return fila[0]


def bloquear_solicitud_propia(db: Session, id_solicitud: int, id_usuario: int):
    # Leer solo el ID de planta; después bloquear planta y solicitud, en ese orden.
    # Releer tras el bloqueo evita actuar sobre un estado anterior a una aceptación.
    id_planta = db.scalar(select(SolicitudAdopcion.id_planta).where(
        SolicitudAdopcion.id_solicitud == id_solicitud,
        SolicitudAdopcion.id_adoptante == id_usuario))
    if id_planta is None:
        raise HTTPException(404, "Solicitud no encontrada")
    planta = db.scalar(select(Planta).where(Planta.id_planta == id_planta)
                      .with_for_update().execution_options(populate_existing=True))
    solicitud = db.scalar(select(SolicitudAdopcion).where(
        SolicitudAdopcion.id_solicitud == id_solicitud,
        SolicitudAdopcion.id_adoptante == id_usuario,
    ).with_for_update().execution_options(populate_existing=True))
    if solicitud is None or planta is None:
        raise HTTPException(404, "Solicitud no encontrada")
    if solicitud.estado != "PENDIENTE":
        raise HTTPException(409, "Solo puedes modificar o retirar solicitudes pendientes")
    asociada = db.scalar(text(
        "SELECT id_adopcion FROM public.adopcion WHERE id_solicitud = :id"
    ), {"id": id_solicitud})
    if asociada is not None:
        raise HTTPException(409, "La solicitud tiene una adopción asociada")
    return solicitud, planta


@router.patch("/{id_solicitud}", response_model=SolicitudRespuesta,
              responses={404: {"description": "Solicitud inexistente o ajena"},
                         409: {"description": "Solicitud o planta no permite edición"},
                         503: {"description": "No se pudo guardar el cambio"}})
def corregir_solicitud(id_solicitud: IdSolicitud, datos: SolicitudMensaje,
                      usuario: Usuario = Depends(obtener_usuario_actual),
                      db: Session = Depends(get_db)):
    """Modifica únicamente el mensaje; conserva autor, planta, fecha y estado."""
    try:
        solicitud, planta = bloquear_solicitud_propia(db, id_solicitud, usuario.id_usuario)
        if planta.estado != "DISPONIBLE":
            raise HTTPException(409, "La planta no está disponible")
        solicitud.mensaje = datos.mensaje
        respuesta = SolicitudRespuesta.model_validate(solicitud)
        db.commit()
        return respuesta
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        logger.exception("No se pudo corregir la solicitud")
        raise HTTPException(503, "No se pudo guardar el cambio") from None


@router.delete("/{id_solicitud}", status_code=204, response_class=Response,
               responses={404: {"description": "Solicitud inexistente o ajena"},
                          409: {"description": "Solicitud no permite retiro"},
                          503: {"description": "No se pudo retirar la solicitud"}})
def retirar_solicitud(id_solicitud: IdSolicitud,
                     usuario: Usuario = Depends(obtener_usuario_actual),
                     db: Session = Depends(get_db)):
    """Retira una solicitud pendiente y conserva sus avisos sin enlace a ella."""
    try:
        solicitud, _ = bloquear_solicitud_propia(db, id_solicitud, usuario.id_usuario)
        db.execute(update(Notificacion).where(
            Notificacion.id_solicitud == id_solicitud).values(
            id_solicitud=None, mensaje="Solicitud de adopción retirada por el adoptante."))
        db.delete(solicitud)
        db.commit()
        return Response(status_code=204)
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        logger.exception("No se pudo retirar la solicitud")
        raise HTTPException(503, "No se pudo retirar la solicitud") from None


@router.post("", response_model=SolicitudRespuesta, status_code=201,
             responses={401: {"description": "Token ausente, inválido o vencido"},
                        403: {"description": "Cuenta bloqueada o planta propia"},
                        404: {"description": "Planta inexistente o no visible"},
                        409: {"description": "Planta no disponible o solicitud duplicada"},
                        503: {"description": "No se pudo guardar la solicitud"}})
def crear_solicitud(datos: SolicitudCrear,
                    usuario: Usuario = Depends(obtener_usuario_actual),
                    db: Session = Depends(get_db)):
    try:
        # Serializa envíos para la misma planta. Las futuras operaciones de
        # aceptación/retiro deben bloquear también esta fila antes de decidir.
        planta = db.execute(select(Planta).where(
            Planta.id_planta == datos.id_planta).with_for_update()).scalar_one_or_none()
        if planta is None or not planta.visible or planta.eliminada:
            raise HTTPException(404, "Planta no encontrada")
        if planta.id_usuario == usuario.id_usuario:
            raise HTTPException(403, "No puedes solicitar tu propia planta")
        if planta.estado != "DISPONIBLE":
            raise HTTPException(409, "La planta no está disponible")

        existente = db.execute(select(SolicitudAdopcion.id_solicitud).where(
            SolicitudAdopcion.id_planta == planta.id_planta,
            SolicitudAdopcion.id_adoptante == usuario.id_usuario,
            SolicitudAdopcion.estado.in_(["PENDIENTE", "ACEPTADA"]),
        )).scalar_one_or_none()
        if existente is not None:
            raise HTTPException(409, "Ya tienes una solicitud activa para esta planta")

        solicitud = SolicitudAdopcion(id_planta=planta.id_planta,
                                     id_adoptante=usuario.id_usuario,
                                     mensaje=datos.mensaje, estado="PENDIENTE")
        db.add(solicitud)
        db.flush()
        notificar_solicitud(db, id_usuario=planta.id_usuario,
                           id_planta=planta.id_planta,
                           id_solicitud=solicitud.id_solicitud,
                           nombre_planta=planta.nombre)
        respuesta = SolicitudRespuesta.model_validate(solicitud)
        db.commit()
        return respuesta
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as error:
        db.rollback()
        restriccion = getattr(getattr(error.orig, "diag", None), "constraint_name", None)
        if restriccion == "uq_solicitud_activa_por_usuario":
            raise HTTPException(409, "Ya tienes una solicitud activa para esta planta") from None
        logger.exception("No se pudo guardar la solicitud y su notificación")
        raise HTTPException(503, "No se pudo guardar la solicitud") from None
    except SQLAlchemyError:
        db.rollback()
        logger.exception("No se pudo guardar la solicitud y su notificación")
        raise HTTPException(503, "No se pudo guardar la solicitud") from None
 Main
