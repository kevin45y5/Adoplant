from sqlalchemy import Column, DateTime, Integer, String, text
from sqlalchemy.dialects.postgresql import ENUM

from app.models.base import Base


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = {"schema": "public"}

    id_usuario = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    correo = Column(String(150), nullable=False)
    telefono = Column(String(20), nullable=False)

    contrasena = Column(String(255), nullable=False)

    estado = Column(
        ENUM(
            "ACTIVO",
            "BLOQUEADO",
            name="estado_usuario",
            schema="public",
            create_type=False,
        ),
        nullable=False,
        server_default=text("'ACTIVO'::public.estado_usuario"),
    )

    fecha_registro = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
