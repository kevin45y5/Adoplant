from sqlalchemy import func, select
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario
from app.schemas import (
    UsuarioRegistro,
    UsuarioRespuesta,
    UsuarioLogin,
    TokenRespuesta,
)
from app.security import (
    crear_hash,
    verificar_contrasena,
    crear_token_acceso,
)


router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)


@router.post(
    "/registro",
    response_model=UsuarioRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def registrar_usuario(
    datos: UsuarioRegistro,
    db: Session = Depends(get_db),
):
    usuario = Usuario(
        nombre=datos.nombre,
        apellido=datos.apellido,
        correo=str(datos.correo).lower(),
        telefono=datos.telefono,
        contrasena=crear_hash(datos.contrasena),
    )

    try:
        db.add(usuario)
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
                status_code=500,
                detail="No se pudo registrar el usuario",
            ) from None

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=mensaje,
        ) from None

    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=TokenRespuesta)
def iniciar_sesion(
    datos: UsuarioLogin,
    db: Session = Depends(get_db),
):
    identificador = datos.identificador

    if "@" in identificador:
        consulta = select(Usuario).where(
            func.lower(func.btrim(Usuario.correo))
            == identificador.lower()
        )
    else:
        consulta = select(Usuario).where(
            func.btrim(Usuario.telefono) == identificador
        )

    usuario = db.execute(consulta).scalar_one_or_none()

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    if not verificar_contrasena(
        datos.contrasena,
        usuario.contrasena,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    if usuario.estado != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta está bloqueada",
        )

    return TokenRespuesta(
        access_token=crear_token_acceso(usuario.id_usuario)
    )
