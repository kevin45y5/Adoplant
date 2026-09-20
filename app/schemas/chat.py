from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatCrear(BaseModel):
    id_planta: int = Field(gt=0)


class ParticipanteChatRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    posicion: int


class ChatRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_chat: int
    id_planta: int
    fecha_creacion: datetime
    participantes: list[ParticipanteChatRespuesta]


class ChatResumen(BaseModel):
    id_chat: int
    id_planta: int
    fecha_creacion: datetime
    id_otro_participante: int


class MensajeCrear(BaseModel):
    contenido: str = Field(min_length=1)

    @field_validator("contenido", mode="before")
    @classmethod
    def contenido_no_vacio(cls, valor):
        if isinstance(valor, str):
            valor = valor.strip()
        if not valor:
            raise ValueError("El mensaje no puede estar vacío")
        return valor


class MensajeRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_mensaje: int
    contenido: str | None
    fecha_hora: datetime
    tipo: str
    id_chat: int
    id_usuario: int


class MensajesPaginados(BaseModel):
    total: int
    pagina: int
    tamano_pagina: int
    mensajes: list[MensajeRespuesta]
