from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import ENUM

from app.models.base import Base


class SolicitudAdopcion(Base):
    __tablename__ = "solicitud_adopcion"
    __table_args__ = {"schema": "public"}

    id_solicitud = Column(Integer, primary_key=True, autoincrement=True)
    mensaje = Column(String(500), nullable=False)
    estado = Column(
        ENUM(
            "PENDIENTE",
            "ACEPTADA",
            "RECHAZADA",
            name="estado_solicitud",
            schema="public",
            create_type=False,
        ),
        nullable=False,
        server_default=text("'PENDIENTE'::public.estado_solicitud"),
    )
    fecha_solicitud = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    id_planta = Column(
        Integer,
        ForeignKey("public.planta.id_planta"),
        nullable=False,
    )
    id_adoptante = Column(
        Integer,
        ForeignKey("public.usuario.id_usuario"),
        nullable=False,
    )


class Adopcion(Base):
    __tablename__ = "adopcion"
    __table_args__ = {"schema": "public"}

    id_adopcion = Column(Integer, primary_key=True, autoincrement=True)
    estado = Column(
        ENUM(
            "EN_PROCESO",
            "COMPLETADA",
            name="estado_adopcion",
            schema="public",
            create_type=False,
        ),
        nullable=False,
        server_default=text("'EN_PROCESO'::public.estado_adopcion"),
    )
    fecha_entrega = Column(DateTime(timezone=True))
    fecha_recepcion = Column(DateTime(timezone=True))
    id_solicitud = Column(
        Integer,
        ForeignKey("public.solicitud_adopcion.id_solicitud"),
        nullable=False,
        unique=True,
    )
    id_planta = Column(
        Integer,
        ForeignKey("public.planta.id_planta"),
        nullable=False,
        unique=True,
    )
    id_donante = Column(
        Integer,
        ForeignKey("public.usuario.id_usuario"),
        nullable=False,
    )
    id_adoptante = Column(
        Integer,
        ForeignKey("public.usuario.id_usuario"),
        nullable=False,
    )
