from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import declarative_base


Base = declarative_base()


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

    # Aquí guardaremos el hash, nunca la contraseña original.
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


class Notificacion(Base):
    __tablename__ = "notificacion"
    __table_args__ = {"schema": "public"}

    id_notificacion = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String(100), nullable=False)
    mensaje = Column(Text, nullable=False)
    fecha_hora = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    leida = Column(Boolean, nullable=False, server_default=text("false"))
    id_usuario = Column(Integer, ForeignKey("public.usuario.id_usuario", ondelete="CASCADE"), nullable=False)
    id_solicitud = Column(Integer, ForeignKey("public.solicitud_adopcion.id_solicitud", ondelete="SET NULL"), nullable=True)
    id_planta = Column(Integer, ForeignKey("public.planta.id_planta", ondelete="SET NULL"), nullable=True)
