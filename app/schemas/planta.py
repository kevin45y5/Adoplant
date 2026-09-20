from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PlantaCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    tamano: str = Field(min_length=1, max_length=50)
    nivel_cuidado: str = Field(min_length=1, max_length=50)
    estado_salud: str = Field(min_length=1, max_length=100)
    necesidad_luz: str = Field(min_length=1, max_length=100)
    necesidad_agua: str = Field(min_length=1, max_length=100)
    descripcion: str = Field(max_length=500, default="")
    ubicacion: str = Field(min_length=1, max_length=255)
    estado: str = Field(default="DISPONIBLE", max_length=20)
    categoria_id: int = Field(gt=0)


class PlantaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_planta: int
    nombre: str
    tamano: str
    nivel_cuidado: str
    estado_salud: str
    necesidad_luz: str
    necesidad_agua: str
    descripcion: str | None
    ubicacion: str
    estado: str
    fecha_publicacion: datetime
    visible: bool
    eliminada: bool
    motivo_moderacion: str | None
    fecha_moderacion: datetime | None
    id_administrador_moderador: int | None
    id_usuario: int
    id_categoria: int


class PlantaModeracion(BaseModel):
    motivo: str = Field(min_length=1, max_length=500)
    visible: bool | None = None
    eliminada: bool | None = None
    fecha_moderacion: datetime | None = None