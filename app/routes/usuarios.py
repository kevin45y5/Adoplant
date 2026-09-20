from fastapi import APIRouter, Depends

from app.dependencies import obtener_usuario_actual
from app.models import Usuario
from app.schemas import UsuarioRespuesta


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
)


@router.get(
    "/me",
    response_model=UsuarioRespuesta,
    summary="Consultar mi cuenta",
)
def consultar_mi_cuenta(
    usuario: Usuario = Depends(obtener_usuario_actual),
):
    return usuario
