from datetime import datetime
from typing import Optional, List, Annotated, Any

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator, BeforeValidator


def strip_str(v: Any) -> Any:
    if isinstance(v, str):
        return v.strip()
    return v

def reject_bool(v: Any) -> Any:
    if isinstance(v, bool):
        raise ValueError("Must be an integer, not boolean")
    return v


class UsuarioRegistro(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    apellido: str = Field(..., min_length=1, max_length=100)
    correo: str = Field(..., max_length=150)
    telefono: str = Field(..., min_length=1, max_length=20)
    contrasena: str = Field(..., min_length=8)
    confirmar_contrasena: str

    model_config = ConfigDict(extra="forbid")

    @field_validator("nombre", "apellido", mode="before")
    @classmethod
    def limpiar_cadenas(cls, v: str) -> str:
        return v.strip()

    @field_validator("correo", mode="before")
    @classmethod
    def validar_correo(cls, v: str) -> str:
        v = v.strip()
        if "@" not in v:
            raise ValueError("Correo inválido")
        return v

    @field_validator("telefono", mode="before")
    @classmethod
    def validar_telefono(cls, v: str) -> str:
        if v is None:
            raise ValueError("El teléfono es obligatorio")
        v = v.strip()
        if len(v) > 20:
            raise ValueError("Teléfono demasiado largo")
        return v

    @field_validator("contrasena")
    @classmethod
    def validar_contrasena(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Debe tener al menos una mayúscula")
        if not any(c.islower() for c in v):
            raise ValueError("Debe tener al menos una minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("Debe tener al menos un dígito")
        return v

    @model_validator(mode="after")
    def validar_confirmacion(self) -> "UsuarioRegistro":
        if self.contrasena != self.confirmar_contrasena:
            raise ValueError("Las contraseñas no coinciden")
        return self

    def model_dump(self, **kwargs):
        result = super().model_dump(**kwargs)
        result.pop("contrasena", None)
        result.pop("confirmar_contrasena", None)
        return result


class UsuarioLogin(BaseModel):
    identificador: str
    contrasena: str

    model_config = ConfigDict(extra="forbid")


class TokenRespuesta(BaseModel):
    access_token: str


class UsuarioRespuesta(BaseModel):
    id_usuario: int
    nombre: str
    apellido: str
    correo: str
    telefono: str
    estado: str
    fecha_registro: datetime

    model_config = ConfigDict(from_attributes=True)


class UsuarioActualizacion(BaseModel):
    nombre: Annotated[Optional[str], BeforeValidator(strip_str)] = Field(None, min_length=1, max_length=100)
    apellido: Annotated[Optional[str], BeforeValidator(strip_str)] = Field(None, min_length=1, max_length=100)
    correo: Annotated[Optional[str], BeforeValidator(strip_str)] = Field(None, max_length=150)
    telefono: Annotated[Optional[str], BeforeValidator(strip_str)] = Field(None, min_length=1, max_length=20)

    model_config = ConfigDict(extra="forbid")

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if "@" not in v:
            raise ValueError("Correo inválido")
        return v

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v) > 20:
            raise ValueError("Teléfono demasiado largo")
        return v

    @model_validator(mode="after")
    def al_menos_un_campo(self) -> "UsuarioActualizacion":
        if all(v is None for v in [self.nombre, self.apellido, self.correo, self.telefono]):
            raise ValueError("Al menos un campo es necesario")
        return self

    @model_validator(mode="after")
    def validar_campos_no_vacios(self) -> "UsuarioActualizacion":
        for campo in ["nombre", "apellido", "correo", "telefono"]:
            val = getattr(self, campo)
            if val is not None and val == "":
                raise ValueError(f"{campo} no puede estar vacío")
        return self


class UsuarioEstadoActualizacion(BaseModel):
    estado: str = Field(..., pattern="^(ACTIVO|BLOQUEADO)$")

    model_config = ConfigDict(extra="forbid")


class UsuariosPagina(BaseModel):
    total: int
    pagina: int
    limite: int
    usuarios: List[UsuarioRespuesta]

    model_config = ConfigDict(from_attributes=True)


class SolicitudCrear(BaseModel):
    id_planta: Annotated[int, BeforeValidator(reject_bool)] = Field(..., gt=0, le=2_147_483_647)
    mensaje: Annotated[str, BeforeValidator(strip_str)] = Field(..., min_length=1, max_length=500)

    model_config = ConfigDict(extra="forbid")


class SolicitudMensaje(BaseModel):
    mensaje: Annotated[str, BeforeValidator(strip_str)] = Field(..., min_length=1, max_length=500)

    model_config = ConfigDict(extra="forbid")


class SolicitudRespuesta(BaseModel):
    id_solicitud: int
    mensaje: str
    estado: str
    fecha_solicitud: datetime
    id_planta: int
    id_adoptante: int

    model_config = ConfigDict(from_attributes=True)


class CategoriaRespuesta(BaseModel):
    id_categoria: int
    nombre: str
    estado: str

    model_config = ConfigDict(from_attributes=True)


class FotografiaRespuesta(BaseModel):
    id_fotografia: int
    url: str
    tipo: Optional[str]
    fecha_subida: datetime
    es_principal: bool

    model_config = ConfigDict(from_attributes=True)


class FotografiaCreate(BaseModel):
    id_planta: int = Field(..., gt=0)
    url: str
    tipo: Optional[str] = None
    es_principal: bool = False

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
    puede_solicitar: bool = True
    categoria: Optional[CategoriaRespuesta] = None

    model_config = ConfigDict(from_attributes=True)


class PlantaCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    tamano: str = Field(..., max_length=50)
    nivel_cuidado: str = Field(..., max_length=50)
    estado_salud: str = Field(..., max_length=100)
    necesidad_luz: str = Field(..., max_length=100)
    necesidad_agua: str = Field(..., max_length=100)
    descripcion: Optional[str] = None
    ubicacion: str = Field(..., max_length=255)
    id_categoria: int = Field(..., gt=0)

    model_config = ConfigDict(extra="forbid")


class PlantaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    tamano: Optional[str] = Field(None, max_length=50)
    nivel_cuidado: Optional[str] = Field(None, max_length=50)
    estado_salud: Optional[str] = Field(None, max_length=100)
    necesidad_luz: Optional[str] = Field(None, max_length=100)
    necesidad_agua: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    ubicacion: Optional[str] = Field(None, max_length=255)
    id_categoria: Optional[int] = None

    model_config = ConfigDict(extra="forbid")


class CatalogoResponse(BaseModel):
    total: int
    pagina: int
    limite: int
    plantas: List[PlantaRespuesta]

    model_config = ConfigDict(from_attributes=True)
