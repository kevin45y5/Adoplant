from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Administrador(Base):
    __tablename__ = "administrador"
    __table_args__ = {"schema": "public"}

    id_administrador = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("public.usuario.id_usuario"),
                        nullable=False, unique=True)


class Planta(Base):
    """Campos de la tabla existente necesarios para consultar y bloquear la planta.

    SCRUM-6 no crea ni modifica plantas mediante este modelo.
    """

    __tablename__ = "planta"
    __table_args__ = {"schema": "public"}

    id_planta = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    id_usuario = Column(Integer, nullable=False)
    estado = Column(ENUM("DISPONIBLE", "SOLICITADA", "ADOPTADA",
                         name="estado_planta", schema="public", create_type=False))
    visible = Column(Boolean, nullable=False)
    eliminada = Column(Boolean, nullable=False)


class SolicitudAdopcion(Base):
    __tablename__ = "solicitud_adopcion"
    __table_args__ = {"schema": "public"}

    id_solicitud = Column(Integer, primary_key=True, autoincrement=True)
    mensaje = Column(String(500), nullable=False)
    estado = Column(ENUM("PENDIENTE", "ACEPTADA", "RECHAZADA",
                         name="estado_solicitud", schema="public", create_type=False),
                    nullable=False, server_default=text("'PENDIENTE'::public.estado_solicitud"))
    fecha_solicitud = Column(DateTime(timezone=True), nullable=False,
                             server_default=text("CURRENT_TIMESTAMP"))
    id_planta = Column(Integer, nullable=False)
    id_adoptante = Column(Integer, nullable=False)


class Notificacion(Base):
    __tablename__ = "notificacion"
    __table_args__ = {"schema": "public"}

    id_notificacion = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String(100), nullable=False)
    mensaje = Column(Text, nullable=False)
    fecha_hora = Column(DateTime(timezone=True), nullable=False,
                        server_default=text("CURRENT_TIMESTAMP"))
    leida = Column(Boolean, nullable=False, server_default=text("false"))
    id_usuario = Column(Integer, nullable=False)
    id_solicitud = Column(Integer)
    id_planta = Column(Integer)


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
