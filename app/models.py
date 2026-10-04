from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, SmallInteger, String, Text, text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import declarative_base, relationship, synonym


Base = declarative_base()


class Administrador(Base):
    __tablename__ = "administrador"
    __table_args__ = {"schema": "public"}

    id_administrador = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("public.usuario.id_usuario"),
                        nullable=False, unique=True)


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
    estado = Column(
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

    estado_planta = synonym("estado")

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


class RecuperacionContrasena(Base):
    __tablename__ = "recuperacion_contrasena"
    __table_args__ = {"schema": "public"}

    id_recuperacion = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("public.usuario.id_usuario"), nullable=False)
    codigo_hash = Column(String(255), nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    fecha_expiracion = Column(DateTime(timezone=True), nullable=False)
    utilizado = Column(Boolean, nullable=False, server_default=text("false"))
    intentos = Column(SmallInteger, nullable=False, server_default=text("0"))


class Fotografia(Base):
    __tablename__ = "fotografia"
    __table_args__ = {"schema": "public"}

    id_fotografia = Column("id_foto", Integer, primary_key=True, autoincrement=True)
    id_planta = Column(Integer, ForeignKey("public.planta.id_planta"),
                        nullable=False)
    url = Column(String(500), nullable=False)
    fecha_subida = Column("fecha_carga", DateTime(timezone=True), nullable=False,
                           server_default=text("CURRENT_TIMESTAMP"))

    planta = relationship("Planta", foreign_keys=[id_planta],
                          back_populates="fotografias")

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

class Chat(Base):
    __tablename__ = "chat"
    __table_args__ = {"schema": "public"}

    id_chat = Column(Integer, primary_key=True, autoincrement=True)
    fecha_creacion = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    id_planta = Column(
        Integer,
        ForeignKey("public.planta.id_planta"),
        nullable=False,
    )

    participantes = relationship(
        "ChatParticipante",
        back_populates="chat",
        cascade="all, delete-orphan",
    )
    mensajes = relationship(
        "Mensaje",
        back_populates="chat",
        order_by="Mensaje.fecha_hora",
    )

class ChatParticipante(Base):
    __tablename__ = "chat_participante"
    __table_args__ = {"schema": "public"}

    id_chat = Column(
        Integer,
        ForeignKey("public.chat.id_chat", ondelete="CASCADE"),
        primary_key=True,
    )
    id_usuario = Column(
        Integer,
        ForeignKey("public.usuario.id_usuario"),
        primary_key=True,
    )
    posicion = Column(SmallInteger, nullable=False)

    chat = relationship("Chat", back_populates="participantes")
    usuario = relationship("Usuario")

class Mensaje(Base):
    __tablename__ = "mensaje"
    __table_args__ = {"schema": "public"}

    id_mensaje = Column(Integer, primary_key=True, autoincrement=True)
    contenido = Column(Text)
    fecha_hora = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    tipo = Column(
        String(20),
        nullable=False,
        server_default=text("'TEXTO'::character varying"),
    )
    id_chat = Column(
        Integer,
        ForeignKey("public.chat.id_chat"),
        nullable=False,
    )
    id_usuario = Column(
        Integer,
        ForeignKey("public.usuario.id_usuario"),
        nullable=False,
    )

    chat = relationship("Chat", back_populates="mensajes")
    usuario = relationship("Usuario")
    punto = relationship("PuntoEncuentro", uselist=False, back_populates="mensaje", cascade="all, delete-orphan")


class PuntoEncuentro(Base):
    __tablename__ = "punto_encuentro"
    __table_args__ = {"schema": "public"}

    id_punto = Column(Integer, primary_key=True, autoincrement=True)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    descripcion = Column(String(255))
    id_mensaje = Column(Integer, ForeignKey("public.mensaje.id_mensaje", ondelete="CASCADE"), nullable=False)
    mensaje = relationship("Mensaje", back_populates="punto")

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

class Reporte(Base):
    __tablename__ = "reporte"
    __table_args__ = {"schema": "public"}

    id_reporte = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    motivo = Column(Text, nullable=False)
    estado = Column(
        ENUM(
            "EN_REVISION",
            "RESUELTO",
            name="estado_reporte",
            schema="public",
            create_type=False,
        ),
        nullable=False,
        server_default=text("'EN_REVISION'::public.estado_reporte"),
    )
    fecha_creacion = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    id_reportante = Column(
        Integer,
        ForeignKey("public.usuario.id_usuario"),
        nullable=False,
    )
    id_reportado = Column(
        Integer,
        ForeignKey("public.usuario.id_usuario"),
        nullable=False,
    )
    id_administrador = Column(
        Integer,
        ForeignKey("public.administrador.id_administrador"),
        nullable=True,
    )
