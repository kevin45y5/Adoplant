from fastapi import HTTPException
from sqlalchemy import select
from app.models import Adopcion, Chat, ChatParticipante, SolicitudAdopcion
from app.schemas import PuntoRespuesta

AVISO_RETIRO = "Punto de encuentro retirado por el remitente"


def autorizar_chat(db, id_chat, id_usuario):
    chat = db.get(Chat, id_chat)
    if chat is None:
        raise HTTPException(404, "Chat no encontrado")
    if db.get(ChatParticipante, (id_chat, id_usuario)) is None:
        raise HTTPException(403, "No tienes permiso para consultar este chat")
    return chat


def adopcion_chat(db, chat, bloquear=False):
    consulta = select(Adopcion).join(SolicitudAdopcion, Adopcion.id_solicitud == SolicitudAdopcion.id_solicitud).where(
        Adopcion.id_planta == chat.id_planta, SolicitudAdopcion.estado == "ACEPTADA"
    )
    if bloquear:
        # Mismo orden para crear, corregir y retirar: chat y después adopción.
        db.execute(select(Chat.id_chat).where(Chat.id_chat == chat.id_chat).with_for_update())
        consulta = consulta.with_for_update(of=Adopcion)
    return db.scalar(consulta.execution_options(populate_existing=True))


def exigir_en_proceso(db, chat):
    adopcion = adopcion_chat(db, chat, bloquear=True)
    if adopcion is None or adopcion.estado != "EN_PROCESO":
        raise HTTPException(409, "Solo puedes cambiar puntos durante una adopción EN_PROCESO")
    return adopcion


def respuesta_punto(punto, id_usuario, en_proceso):
    return PuntoRespuesta(
        id_punto=punto.id_punto, id_mensaje=punto.id_mensaje,
        latitud=punto.latitud, longitud=punto.longitud, descripcion=punto.descripcion,
        puede_editar=en_proceso and punto.mensaje.id_usuario == id_usuario,
    )
