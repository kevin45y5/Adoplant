from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import obtener_administrador_actual
from app.models import Usuario
from app.schemas import UsuarioEstadoActualizacion, UsuarioRespuesta, UsuariosPagina


router = APIRouter(
    prefix="/admin/usuarios", tags=["Administración de usuarios"],
    dependencies=[Depends(obtener_administrador_actual)],
)


@router.get("", response_model=UsuariosPagina, summary="Buscar usuarios")
def buscar_usuarios(
    buscar: str | None = Query(default=None, max_length=150),
    pagina: int = Query(default=1, ge=1, le=1_000_000),
    limite: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    condiciones = []
    termino = buscar.strip() if buscar else ""
    if termino:
        texto = termino.lower()
        coincidencias = [
            func.lower(Usuario.nombre).contains(texto, autoescape=True),
            func.lower(Usuario.apellido).contains(texto, autoescape=True),
            func.lower(Usuario.correo).contains(texto, autoescape=True),
        ]
        if termino.isascii() and termino.isdecimal() and len(termino) <= 10:
            identificador = int(termino)
            if 1 <= identificador <= 2_147_483_647:
                coincidencias.append(Usuario.id_usuario == identificador)
        condiciones.append(or_(*coincidencias))
    total = db.scalar(select(func.count()).select_from(Usuario).where(*condiciones))
    usuarios = db.scalars(
        select(Usuario).where(*condiciones).order_by(Usuario.id_usuario)
        .offset((pagina - 1) * limite).limit(limite)
    ).all()
    return UsuariosPagina(total=total, pagina=pagina, limite=limite, usuarios=usuarios)


@router.get("/{id_usuario}", response_model=UsuarioRespuesta,
            summary="Consultar usuario por ID")
def consultar_usuario(
    id_usuario: int = Path(ge=1, le=2_147_483_647),
    db: Session = Depends(get_db),
):
    usuario = db.get(Usuario, id_usuario)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.patch("/{id_usuario}/estado", response_model=UsuarioRespuesta,
              summary="Bloquear o reactivar usuario")
def cambiar_estado_usuario(
    datos: UsuarioEstadoActualizacion,
    id_usuario: int = Path(ge=1, le=2_147_483_647),
    db: Session = Depends(get_db),
):
    usuario = consultar_usuario(id_usuario, db)
    usuario.estado = datos.estado
    db.commit()
    db.refresh(usuario)
    return usuario
