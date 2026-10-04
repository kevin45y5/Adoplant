from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.database import get_db
from app.dependencies import obtener_usuario_actual
from app.models import Mensaje, PuntoEncuentro, Usuario
from app.schemas import PuntoEditar, PuntoRespuesta
from app.services.puntos_encuentro import (
    AVISO_RETIRO, adopcion_chat, autorizar_chat, exigir_en_proceso, respuesta_punto,
)

router = APIRouter(tags=["Puntos de encuentro"])


def obtener(db, id_punto, usuario, escritura=False):
    punto = db.get(PuntoEncuentro, id_punto)
    if punto is None:
        raise HTTPException(404, "Punto de encuentro no encontrado")
    chat = autorizar_chat(db, punto.mensaje.id_chat, usuario.id_usuario)
    if escritura:
        if punto.mensaje.id_usuario != usuario.id_usuario:
            raise HTTPException(403, "Solo el remitente puede modificar o retirar el punto")
        exigir_en_proceso(db, chat)
        # Refresca después de esperar el bloqueo: otro dispositivo pudo retirarlo.
        punto = db.scalar(select(PuntoEncuentro).where(PuntoEncuentro.id_punto == id_punto).execution_options(populate_existing=True))
        if punto is None:
            raise HTTPException(404, "Punto de encuentro no encontrado")
    return punto, chat


@router.get("/chats/{id_chat}/puntos", response_model=list[PuntoRespuesta])
def listar_puntos(id_chat: int, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    chat = autorizar_chat(db, id_chat, usuario.id_usuario)
    adopcion = adopcion_chat(db, chat)
    puntos = db.scalars(select(PuntoEncuentro).join(Mensaje).options(selectinload(PuntoEncuentro.mensaje)).where(Mensaje.id_chat == id_chat).order_by(PuntoEncuentro.id_punto)).all()
    return [respuesta_punto(p, usuario.id_usuario, adopcion is not None and adopcion.estado == "EN_PROCESO") for p in puntos]


@router.get("/puntos-encuentro/{id_punto}", response_model=PuntoRespuesta)
def consultar_punto(id_punto: int, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    punto, chat = obtener(db, id_punto, usuario)
    adopcion = adopcion_chat(db, chat)
    return respuesta_punto(punto, usuario.id_usuario, adopcion is not None and adopcion.estado == "EN_PROCESO")


@router.patch("/puntos-encuentro/{id_punto}", response_model=PuntoRespuesta)
def editar_punto(id_punto: int, datos: PuntoEditar, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    punto, _ = obtener(db, id_punto, usuario, escritura=True)
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(punto, campo, valor.strip() if isinstance(valor, str) else valor)
    db.commit()
    db.refresh(punto)
    return respuesta_punto(punto, usuario.id_usuario, True)


@router.delete("/puntos-encuentro/{id_punto}", status_code=204)
def retirar_punto(id_punto: int, db: Session = Depends(get_db), usuario: Usuario = Depends(obtener_usuario_actual)):
    punto, _ = obtener(db, id_punto, usuario, escritura=True)
    mensaje = punto.mensaje
    mensaje.tipo = "TEXTO"
    mensaje.contenido = AVISO_RETIRO
    db.delete(punto)
    db.commit()
    return Response(status_code=204)
