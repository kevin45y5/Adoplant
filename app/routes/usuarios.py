from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import obtener_usuario_actual
from app.models import Usuario
from app.schemas import UsuarioActualizacion, UsuarioRespuesta


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


@router.patch(
    "/me",
    response_model=UsuarioRespuesta,
    summary="Modificar mis datos personales",
)
def actualizar_mi_cuenta(
    datos: UsuarioActualizacion,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    cambios = datos.model_dump(exclude_unset=True)

    if "correo" in cambios:
        cambios["correo"] = str(cambios["correo"]).lower()

    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()

        diagnostico = getattr(error.orig, "diag", None)
        restriccion = getattr(diagnostico, "constraint_name", None)

        if restriccion == "uq_usuario_correo":
            mensaje = "El correo electrónico ya está registrado"
        elif restriccion == "uq_usuario_telefono":
            mensaje = "El número de teléfono ya está registrado"
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo actualizar la cuenta",
            ) from None

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=mensaje,
        ) from None

    db.refresh(usuario)
    return usuario
