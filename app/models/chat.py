from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    text,
)
from sqlalchemy.orm import relationship

from app.models.base import Base


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
