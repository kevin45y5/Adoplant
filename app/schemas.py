from datetime import datetime
from typing import List, Optional
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


class CategoriaCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)


class CategoriaRespuesta(BaseModel):
    id_categoria: int
    nombre: str
    estado: str
    model_config = ConfigDict(from_attributes=True)


class PlantaCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    tamano: str = Field(min_length=1, max_length=50)
    nivel_cuidado: str = Field(min_length=1, max_length=50)
    estado_salud: str = Field(min_length=1, max_length=100)
    necesidad_luz: str = Field(min_length=1, max_length=100)
    necesidad_agua: str = Field(min_length=1, max_length=100)
    descripcion: Optional[str] = Field(default="", max_length=500)
    ubicacion: str = Field(min_length=1, max_length=255)
    id_categoria: int


class PlantaUpdate(BaseModel):
    nombre: Optional[str] = Field(default="", max_length=100)
    tamano: Optional[str] = Field(default="", max_length=50)
    nivel_cuidado: Optional[str] = Field(default="", max_length=50)
    estado_salud: Optional[str] = Field(default="", max_length=100)
    necesidad_luz: Optional[str] = Field(default="", max_length=100)
    necesidad_agua: Optional[str] = Field(default="", max_length=100)
    descripcion: Optional[str] = Field(default="", max_length=500)
    ubicacion: Optional[str] = Field(default="", max_length=255)
    id_categoria: Optional[int] = None
    visible: bool = Field(default=True)


class PlantaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    categoria: Optional[CategoriaRespuesta] = None
    fotografia_url: Optional[str] = None
    puede_solicitar: bool = False


class FotografiaRespuesta(BaseModel):
    id_foto: int
    url: str
    fecha_carga: datetime
    id_planta: int
    model_config = ConfigDict(from_attributes=True)


class FotografiaCreate(BaseModel):
    id_planta: int
    model_config = ConfigDict(from_attributes=True)


class CatalogoResponse(BaseModel):
    items: List[PlantaRespuesta]
    total: int
    pagina: int
    limite: int
    total_paginas: int
    tiene_mas: bool
