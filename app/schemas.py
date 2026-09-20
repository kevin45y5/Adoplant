from datetime import datetime

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
