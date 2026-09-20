from sqlalchemy import Column, Integer, ForeignKey

from app.models.base import Base


class administrador(Base):
    __tablename__ = "administrador"
    __table_args__ = {"schema": "public"}

    id_administrador = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("public.usuario.id_usuario"), unique=True, nullable=False)