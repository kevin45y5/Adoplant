from typing import Optional, List
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class UsuarioRegistro(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    apellido: str = Field(min_length=1, max_length=100)
    correo: EmailStr = Field(max_length=150)
    telefono: str = Field(min_length=1, max_length=20)
    contrasena: str = Field(min_length=8, max_length=128,
                            repr=False, exclude=True)
    confirmar_contrasena: str = Field(
        min_length=8, max_length=128, repr=False, exclude=True)

    @field_validator("nombre", "apellido", "correo", "telefono", mode="before")
    @classmethod
    def quitar_espacios_exteriores(cls, valor):
        return valor.strip() if isinstance(valor, str) else valor

    @field_validator("contrasena")
    @classmethod
    def validar_contrasena(cls, valor: str) -> str:
        if not any(letra.isalpha() for letra in valor) or not any(numero.isdecimal() for numero in valor):
            raise ValueError(
                "La contraseña debe contener al menos una letra y un número")
        return valor

    @model_validator(mode="after")
    def confirmar_coincidencia(self):
        if self.contrasena != self.confirmar_contrasena:
            raise ValueError("Las contraseñas no coinciden")
        return self


class UsuarioRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    nombre: str
    apellido: str
    correo: EmailStr
    telefono: str
    estado: str
    fecha_registro: datetime


class UsuarioLogin(BaseModel):
    identificador: str = Field(min_length=1, max_length=150)
    contrasena: str = Field(
        min_length=1,
        max_length=128,
        repr=False,
        exclude=True,
    )

    @field_validator("identificador", mode="before")
    @classmethod
    def limpiar_identificador(cls, valor):
        return valor.strip() if isinstance(valor, str) else valor


class SolicitudRecuperacion(BaseModel):
    correo: EmailStr = Field(max_length=150)

    @field_validator("correo", mode="before")
    @classmethod
    def limpiar_correo(cls, valor):
        return valor.strip() if isinstance(valor, str) else valor


class VerificacionRecuperacion(SolicitudRecuperacion):
    codigo: str = Field(min_length=8, max_length=8)

    @field_validator("codigo")
    @classmethod
    def validar_codigo(cls, valor: str) -> str:
        if not valor.isascii() or not valor.isdecimal():
            raise ValueError("El código debe contener ocho números")
        return valor

class RestablecimientoContrasena(VerificacionRecuperacion):
    nueva_contrasena: str = Field(min_length=8, max_length=128, repr=False, exclude=True)
    confirmar_contrasena: str = Field(min_length=8, max_length=128, repr=False, exclude=True)

    @field_validator("nueva_contrasena")
    @classmethod
    def validar_nueva_contrasena(cls, valor: str) -> str:
        if not any(letra.isalpha() for letra in valor) or not any(numero.isdecimal() for numero in valor):
            raise ValueError("La contraseña debe contener al menos una letra y un número")
        return valor

    @model_validator(mode="after")
    def comprobar_confirmacion(self):
        if self.nueva_contrasena != self.confirmar_contrasena:
            raise ValueError("Las contraseñas no coinciden")
        return self


class TokenRespuesta(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioEstadoActualizacion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: Literal["ACTIVO", "BLOQUEADO"]


class UsuariosPagina(BaseModel):
    total: int
    pagina: int
    limite: int
    usuarios: list[UsuarioRespuesta]


class SolicitudMensaje(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mensaje: str = Field(min_length=1, max_length=500)

    @field_validator("mensaje")
    @classmethod
    def limpiar_mensaje(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("El mensaje no puede estar vacío")
        return valor


class SolicitudCrear(SolicitudMensaje):
    id_planta: int = Field(strict=True, gt=0, le=2_147_483_647)


class SolicitudDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: Literal["ACEPTADA", "RECHAZADA"]


class SolicitudRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_solicitud: int
    id_planta: int
    id_adoptante: int
    mensaje: str
    estado: str
    fecha_solicitud: datetime
    nombre_planta: str | None = None
    nombre_adoptante: str | None = None


class UsuarioActualizacion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    apellido: str | None = Field(default=None, min_length=1, max_length=100)
    correo: EmailStr | None = Field(default=None, max_length=150)
    telefono: str | None = Field(default=None, min_length=1, max_length=20)

    @field_validator(
        "nombre", "apellido", "correo", "telefono",
        mode="before",
    )
    @classmethod
    def validar_campo_enviado(cls, valor):
        if valor is None:
            raise ValueError("El campo no puede ser null")

        return valor.strip() if isinstance(valor, str) else valor

    @model_validator(mode="after")
    def comprobar_cambios(self):
        if not self.model_fields_set:
            raise ValueError("Debes enviar al menos un campo para actualizar")

        return self


class CategoriaRespuesta(BaseModel):
    id_categoria: int
    nombre: str
    estado: str

    model_config = ConfigDict(from_attributes=True)

class FotografiaRespuesta(BaseModel):
    id_fotografia: int
    url: str
    fecha_subida: datetime

    model_config = ConfigDict(from_attributes=True)

class FotografiaCreate(BaseModel):
    id_planta: int = Field(..., gt=0)
    url: str

    model_config = ConfigDict(extra="forbid")

class PlantaRespuesta(BaseModel):
    id_planta: int
    nombre: str
    tamano: str
    nivel_cuidado: str
    estado_salud: str
    necesidad_luz: str
    necesidad_agua: str
    descripcion: Optional[str]
    ubicacion: str
    estado_planta: str
    fecha_publicacion: datetime
    visible: bool
    eliminada: bool
    motivo_moderacion: Optional[str]
    fecha_moderacion: Optional[datetime]
    id_administrador_moderador: Optional[int]
    id_usuario: int
    id_categoria: int
    fotografia_url: Optional[str] = None
    fotografias: list[str] = Field(default_factory=list)

    @field_validator("fotografias", mode="before")
    @classmethod
    def urls_fotografias(cls, value):
        return [foto if isinstance(foto, str) else foto.url for foto in value]

    puede_solicitar: bool = True
    categoria: Optional[CategoriaRespuesta] = None

    model_config = ConfigDict(from_attributes=True)

class PlantaCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    tamano: str = Field(..., min_length=1, max_length=50)
    nivel_cuidado: str = Field(..., min_length=1, max_length=50)
    estado_salud: str = Field(..., min_length=1, max_length=100)
    necesidad_luz: str = Field(..., min_length=1, max_length=100)
    necesidad_agua: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = None
    ubicacion: str = Field(..., min_length=1, max_length=255)
    id_categoria: int = Field(..., gt=0)

    model_config = ConfigDict(extra="forbid")

    @field_validator("nombre", "tamano", "nivel_cuidado", "estado_salud", "necesidad_luz", "necesidad_agua", "ubicacion", mode="before")
    @classmethod
    def limpiar_textos_planta(cls, valor):
        if valor is None:
            raise ValueError("El campo no puede ser nulo")
        return valor.strip() if isinstance(valor, str) else valor


class PlantaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    tamano: Optional[str] = Field(None, min_length=1, max_length=50)
    nivel_cuidado: Optional[str] = Field(None, min_length=1, max_length=50)
    estado_salud: Optional[str] = Field(None, min_length=1, max_length=100)
    necesidad_luz: Optional[str] = Field(None, min_length=1, max_length=100)
    necesidad_agua: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = None
    ubicacion: Optional[str] = Field(None, min_length=1, max_length=255)
    id_categoria: Optional[int] = Field(None, gt=0)

    model_config = ConfigDict(extra="forbid")

    @field_validator("nombre", "tamano", "nivel_cuidado", "estado_salud", "necesidad_luz", "necesidad_agua", "ubicacion", mode="before")
    @classmethod
    def limpiar_textos_planta(cls, valor):
        if valor is None:
            raise ValueError("El campo no puede ser nulo")
        return valor.strip() if isinstance(valor, str) else valor


class CatalogoResponse(BaseModel):
    total: int
    pagina: int
    limite: int
    plantas: List[PlantaRespuesta]

    model_config = ConfigDict(from_attributes=True)

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

class PlantaModeracion(BaseModel):
    motivo: str = Field(min_length=1, max_length=500)
    visible: bool | None = None
    eliminada: bool | None = None
    fecha_moderacion: datetime | None = None

class ReporteCrear(BaseModel):
    id_reportado: int = Field(gt=0)
    motivo: str = Field(min_length=1)

    @field_validator("motivo", mode="before")
    @classmethod
    def motivo_no_vacio(cls, valor):
        if isinstance(valor, str):
            valor = valor.strip()
        if not valor:
            raise ValueError("El motivo no puede estar vacío")
        return valor

class ReporteEstadoActualizar(BaseModel):
    estado: str = Field(min_length=1, max_length=20)

    @field_validator("estado", mode="before")
    @classmethod
    def normalizar_estado(cls, valor):
        if isinstance(valor, str):
            valor = valor.strip().upper()
        if not valor:
            raise ValueError("El estado no puede estar vacío")
        return valor

class ReporteRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_reporte: int
    motivo: str
    estado: str
    fecha_creacion: datetime
    id_reportante: int
    id_reportado: int
    id_administrador: int | None = None

class ReferenciasNotificacion(BaseModel):
    id_solicitud: int | None
    id_planta: int | None
    solicitud_disponible: bool
    planta_disponible: bool

class NotificacionRespuesta(BaseModel):
    id_notificacion: int
    tipo: str
    mensaje: str
    fecha_hora: datetime
    leida: bool
    referencias: ReferenciasNotificacion
