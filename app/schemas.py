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


class SolicitudRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_solicitud: int
    id_planta: int
    id_adoptante: int
    mensaje: str
    estado: str
    fecha_solicitud: datetime


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
