from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean, text, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import declarative_base, relationship

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

    usuario = relationship("Usuario", foreign_keys=[id_usuario])
    categoria = relationship("Categoria", foreign_keys=[id_categoria])


class Fotografia(Base):
    __tablename__ = "fotografia"
    __table_args__ = {"schema": "public"}

    id_foto = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(500), nullable=False)
    fecha_carga = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    id_planta = Column(Integer, nullable=False)

    planta = relationship("Planta", foreign_keys=[id_planta])
