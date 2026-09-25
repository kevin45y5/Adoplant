from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Administrador(Base):
    __tablename__ = "administrador"
    __table_args__ = {"schema": "public"}

    id_administrador = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("public.usuario.id_usuario"),
                        nullable=False, unique=True)


class Fotografia(Base):
    __tablename__ = "fotografia"
    __table_args__ = {"schema": "public"}

    id_fotografia = Column(Integer, primary_key=True, autoincrement=True)
    id_planta = Column(Integer, ForeignKey("public.planta.id_planta"),
                        nullable=False)
    url = Column(String(500), nullable=False)
    tipo = Column(String(50), nullable=True)
    fecha_subida = Column(DateTime(timezone=True), nullable=False,
                           server_default=text("CURRENT_TIMESTAMP"))
    es_principal = Column(Boolean, nullable=False, server_default=text("false"))

    planta = relationship("Planta", foreign_keys=[id_planta],
                          back_populates="fotografias")


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
    descripcion = Column(Text, nullable=True)
    ubicacion = Column(String(255), nullable=False)
    estado_planta = Column(
        ENUM("DISPONIBLE", "SOLICITADA", "ADOPTADA", name="estado_planta", schema="public", create_type=False),
        nullable=False,
        server_default=text("'DISPONIBLE'::public.estado_planta"),
    )
    fecha_publicacion = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    visible = Column(Boolean, nullable=False, server_default=text("true"))
    eliminada = Column(Boolean, nullable=False, server_default=text("false"))
    motivo_moderacion = Column(Text, nullable=True)
    fecha_moderacion = Column(DateTime(timezone=True), nullable=True)
    id_administrador_moderador = Column(Integer, nullable=True)
    id_usuario = Column(Integer, nullable=False)
    id_categoria = Column(Integer, nullable=False)

    fotografias = relationship("Fotografia", back_populates="planta")


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


class Categoria(Base):
    __tablename__ = "categoria"
    __table_args__ = {"schema": "public"}

    id_categoria = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    estado = Column(
        ENUM("ACTIVA", "INACTIVA", name="estado_categoria", schema="public", create_type=False),
        nullable=False,
        server_default=text("'ACTIVA'::public.estado_categoria"),
    )
