from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import obtener_usuario_actual
from app.database import get_db
from app.models import (
    Adopcion,
    Chat,
    ChatParticipante,
    Mensaje,
    SolicitudAdopcion,
    Usuario,
)
from app.schemas.chat import (
    ChatCrear,
    ChatRespuesta,
    ChatResumen,
    MensajeCrear,
    MensajeRespuesta,
    MensajesPaginados,
    ParticipanteChatRespuesta,
)

router = APIRouter()


def _serializar_chat(chat: Chat) -> ChatRespuesta:
    return ChatRespuesta(
        id_chat=chat.id_chat,
        id_planta=chat.id_planta,
        fecha_creacion=chat.fecha_creacion,
        participantes=[
            ParticipanteChatRespuesta.model_validate(participante)
            for participante in chat.participantes
        ],
    )


def _obtener_adopcion_autorizada(
    db: Session,
    id_planta: int,
) -> Adopcion | None:
    return db.execute(
        select(Adopcion)
        .join(
            SolicitudAdopcion,
            Adopcion.id_solicitud == SolicitudAdopcion.id_solicitud,
        )
        .where(
            Adopcion.id_planta == id_planta,
            SolicitudAdopcion.estado == "ACEPTADA",
        )
    ).scalar_one_or_none()


def _usuario_participa_en_chat(
    db: Session,
    id_chat: int,
    id_usuario: int,
) -> bool:
    participante = db.execute(
        select(ChatParticipante.id_usuario).where(
            ChatParticipante.id_chat == id_chat,
            ChatParticipante.id_usuario == id_usuario,
        )
    ).scalar_one_or_none()
    return participante is not None


def _obtener_chat_con_participantes(
    db: Session,
    id_chat: int,
) -> Chat | None:
    return db.execute(
        select(Chat)
        .options(selectinload(Chat.participantes))
        .where(Chat.id_chat == id_chat)
    ).scalar_one_or_none()


@router.post(
    "",
    response_model=ChatRespuesta,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_200_OK: {"model": ChatRespuesta}},
)
def crear_u_obtener_chat(
    datos: ChatCrear,
    respuesta: Response,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    adopcion = _obtener_adopcion_autorizada(db, datos.id_planta)

    if adopcion is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "El chat no está disponible sin una solicitud aceptada "
                "y una adopción asociada"
            ),
        )

    if usuario.id_usuario not in (
        adopcion.id_donante,
        adopcion.id_adoptante,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a este chat",
        )

    chat_existente = db.execute(
        select(Chat)
        .options(selectinload(Chat.participantes))
        .where(Chat.id_planta == datos.id_planta)
    ).scalar_one_or_none()

    if chat_existente is not None:
        if not _usuario_participa_en_chat(
            db,
            chat_existente.id_chat,
            usuario.id_usuario,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para acceder a este chat",
            )
        respuesta.status_code = status.HTTP_200_OK
        return _serializar_chat(chat_existente)

    chat = Chat(id_planta=datos.id_planta)
    db.add(chat)
    db.flush()

    db.add_all(
        [
            ChatParticipante(
                id_chat=chat.id_chat,
                id_usuario=adopcion.id_donante,
                posicion=1,
            ),
            ChatParticipante(
                id_chat=chat.id_chat,
                id_usuario=adopcion.id_adoptante,
                posicion=2,
            ),
        ]
    )

    try:
        db.commit()
    except Exception:
        db.rollback()
        chat_recuperado = db.execute(
            select(Chat)
            .options(selectinload(Chat.participantes))
            .where(Chat.id_planta == datos.id_planta)
        ).scalar_one_or_none()
        if chat_recuperado is None:
            raise
        respuesta.status_code = status.HTTP_200_OK
        return _serializar_chat(chat_recuperado)

    db.refresh(chat)
    chat = _obtener_chat_con_participantes(db, chat.id_chat)
    return _serializar_chat(chat)


@router.get("", response_model=list[ChatResumen])
def listar_chats_propios(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    chats = db.execute(
        select(Chat)
        .join(
            ChatParticipante,
            Chat.id_chat == ChatParticipante.id_chat,
        )
        .where(ChatParticipante.id_usuario == usuario.id_usuario)
        .order_by(Chat.fecha_creacion.desc())
        .distinct()
    ).scalars().all()

    resumen: list[ChatResumen] = []

    for chat in chats:
        otro_participante = db.execute(
            select(ChatParticipante.id_usuario).where(
                ChatParticipante.id_chat == chat.id_chat,
                ChatParticipante.id_usuario != usuario.id_usuario,
            )
        ).scalar_one()

        resumen.append(
            ChatResumen(
                id_chat=chat.id_chat,
                id_planta=chat.id_planta,
                fecha_creacion=chat.fecha_creacion,
                id_otro_participante=otro_participante,
            )
        )

    return resumen


@router.post(
    "/{id_chat}/mensajes",
    response_model=MensajeRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def enviar_mensaje(
    id_chat: int,
    datos: MensajeCrear,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    chat = _obtener_chat_con_participantes(db, id_chat)

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat no encontrado",
        )

    if not _usuario_participa_en_chat(db, id_chat, usuario.id_usuario):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para enviar mensajes en este chat",
        )

    mensaje = Mensaje(
        contenido=datos.contenido,
        tipo="TEXTO",
        id_chat=id_chat,
        id_usuario=usuario.id_usuario,
    )
    db.add(mensaje)
    db.commit()
    db.refresh(mensaje)

    return mensaje


@router.get("/{id_chat}/mensajes", response_model=MensajesPaginados)
def listar_mensajes(
    id_chat: int,
    pagina: int = Query(1, ge=1),
    tamano_pagina: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    chat = db.execute(
        select(Chat.id_chat).where(Chat.id_chat == id_chat)
    ).scalar_one_or_none()

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat no encontrado",
        )

    if not _usuario_participa_en_chat(db, id_chat, usuario.id_usuario):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para consultar este chat",
        )

    total = db.execute(
        select(func.count())
        .select_from(Mensaje)
        .where(Mensaje.id_chat == id_chat)
    ).scalar_one()

    desplazamiento = (pagina - 1) * tamano_pagina
    mensajes = db.execute(
        select(Mensaje)
        .where(Mensaje.id_chat == id_chat)
        .order_by(Mensaje.fecha_hora.asc(), Mensaje.id_mensaje.asc())
        .offset(desplazamiento)
        .limit(tamano_pagina)
    ).scalars().all()

    return MensajesPaginados(
        total=total,
        pagina=pagina,
        tamano_pagina=tamano_pagina,
        mensajes=[MensajeRespuesta.model_validate(m) for m in mensajes],
    )
