from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM

from app.models.base import Base


class Planta(Base):
    __tablename__ = "planta"
    __table_args__ = {"schema": "public"}

    id_planta = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    tamano = Column(String(50), nullable=False)
    nivel_cuidado = Column(String(50), nullable=False)
    estado_salud = Column(String(100), nullable=False)
    necesidad_luz = Column(String(100), nullable=False)
    necesidad_agua = Column(String(100), nullable=False)
    descripcion = Column(Text)
    ubicacion = Column(String(255), nullable=False)
    estado = Column(
        ENUM(
            "DISPONIBLE",
            "SOLICITADA",
            "ADOPTADA",
            name="estado_planta",
            schema="public",
            create_type=False,
        ),
        nullable=False,
        default="DISPONIBLE",
    )
    fecha_publicacion = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default="CURRENT_TIMESTAMP",
    )
    visible = Column(Boolean, nullable=False, default=True)
    eliminada = Column(Boolean, nullable=False, default=False)
    motivo_moderacion = Column(Text)
    fecha_moderacion = Column(DateTime(timezone=True))
    id_administrador_moderador = Column(Integer, ForeignKey("public.administrador.id_administrador"))
    id_usuario = Column(Integer, ForeignKey("public.usuario.id_usuario"), nullable=False)
    id_categoria = Column(Integer, ForeignKey("public.categoria.id_categoria"), nullable=False)