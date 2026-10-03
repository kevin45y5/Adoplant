from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Categoria
from app.schemas import CategoriaRespuesta

router = APIRouter(prefix="/categorias", tags=["Categorías"])


@router.get("", response_model=list[CategoriaRespuesta])
def listar_categorias(db: Session = Depends(get_db)):
    return db.scalars(select(Categoria).where(Categoria.estado == "ACTIVA").order_by(Categoria.nombre, Categoria.id_categoria)).all()
