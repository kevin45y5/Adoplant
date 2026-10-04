import hashlib
import hmac
import logging
import secrets
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import func, select, update
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.correo import correo_configurado, enviar_codigo_recuperacion
from app.models import RecuperacionContrasena, Usuario
from app.schemas import (
    RestablecimientoContrasena,
    VerificacionRecuperacion,
    SolicitudRecuperacion,
    UsuarioRegistro,
    UsuarioRespuesta,
    UsuarioLogin,
    TokenRespuesta,
)
from app.security import (
    crear_hash,
    verificar_contrasena,
    crear_token_acceso,
    JWT_SECRET_KEY,
)


router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)

logger = logging.getLogger(__name__)
MENSAJE_RECUPERACION = "Si el correo está registrado, recibirás un código de recuperación"
ERROR_CODIGO = "Código inválido, vencido o utilizado"
MAX_INTENTOS = 5


def _hash_codigo(id_usuario: int, codigo: str) -> str:
    mensaje = f"{id_usuario}:{codigo}".encode()
    return hmac.new(JWT_SECRET_KEY.encode(), mensaje, hashlib.sha256).hexdigest()


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


@router.post("/recuperacion", status_code=status.HTTP_202_ACCEPTED)
def solicitar_recuperacion(datos: SolicitudRecuperacion, db: Session = Depends(get_db)):
    # Comprobar la configuración antes de buscar al usuario mantiene la misma
    # respuesta para correos registrados y desconocidos cuando falta el servicio.
    if not correo_configurado():
        raise HTTPException(status_code=503, detail="Correo temporalmente no disponible")

    correo = str(datos.correo).lower()
    usuario = db.execute(
        select(Usuario).where(func.lower(func.btrim(Usuario.correo)) == correo)
    ).scalar_one_or_none()
    if usuario is None or usuario.estado != "ACTIVO":
        return {"mensaje": MENSAJE_RECUPERACION}

    ahora = datetime.now(timezone.utc)
    ultima = db.execute(
        select(RecuperacionContrasena)
        .where(RecuperacionContrasena.id_usuario == usuario.id_usuario)
        .order_by(RecuperacionContrasena.fecha_creacion.desc(), RecuperacionContrasena.id_recuperacion.desc())
        .limit(1)
    ).scalar_one_or_none()
    if ultima is not None and ultima.fecha_creacion > ahora - timedelta(minutes=1):
        return {"mensaje": MENSAJE_RECUPERACION}

    codigo = f"{secrets.randbelow(100_000_000):08d}"
    db.execute(
        update(RecuperacionContrasena)
        .where(RecuperacionContrasena.id_usuario == usuario.id_usuario,
               RecuperacionContrasena.utilizado.is_(False))
        .values(utilizado=True)
    )
    db.add(RecuperacionContrasena(
        id_usuario=usuario.id_usuario,
        codigo_hash=_hash_codigo(usuario.id_usuario, codigo),
        fecha_expiracion=ahora + timedelta(minutes=15),
        utilizado=False,
        intentos=0,
    ))

    try:
        db.flush()
        enviar_codigo_recuperacion(usuario.correo, codigo)
        db.commit()
    except (httpx.HTTPError, OSError):
        db.rollback()
        logger.exception("No se pudo entregar un correo de recuperación")
    return {"mensaje": MENSAJE_RECUPERACION}


def _validar_recuperacion(datos: VerificacionRecuperacion, db: Session):
    correo = str(datos.correo).lower()
    usuario = db.execute(
        select(Usuario).where(func.lower(func.btrim(Usuario.correo)) == correo)
    ).scalar_one_or_none()
    if usuario is None or usuario.estado != "ACTIVO":
        raise HTTPException(status_code=400, detail=ERROR_CODIGO)

    recuperacion = db.execute(
        select(RecuperacionContrasena)
        .where(RecuperacionContrasena.id_usuario == usuario.id_usuario)
        .order_by(RecuperacionContrasena.fecha_creacion.desc(), RecuperacionContrasena.id_recuperacion.desc())
        .limit(1)
        .with_for_update()
    ).scalar_one_or_none()
    if recuperacion is None or recuperacion.utilizado or recuperacion.intentos >= MAX_INTENTOS:
        raise HTTPException(status_code=400, detail=ERROR_CODIGO)

    if recuperacion.fecha_expiracion <= datetime.now(timezone.utc):
        recuperacion.utilizado = True
        db.commit()
        raise HTTPException(status_code=400, detail=ERROR_CODIGO)

    hash_recibido = _hash_codigo(usuario.id_usuario, datos.codigo)
    if not hmac.compare_digest(hash_recibido, recuperacion.codigo_hash):
        recuperacion.intentos += 1
        if recuperacion.intentos >= MAX_INTENTOS:
            recuperacion.utilizado = True
        db.commit()
        raise HTTPException(status_code=400, detail=ERROR_CODIGO)

    return usuario, recuperacion


@router.post("/verificar-codigo")
def verificar_codigo(datos: VerificacionRecuperacion, db: Session = Depends(get_db)):
    _validar_recuperacion(datos, db)
    db.commit()
    return {"mensaje": "Código verificado"}


@router.post("/restablecer-contrasena")
def restablecer_contrasena(datos: RestablecimientoContrasena, db: Session = Depends(get_db)):
    # Se valida nuevamente para impedir usar códigos vencidos, sustituidos o usados.
    usuario, recuperacion = _validar_recuperacion(datos, db)
    usuario.contrasena = crear_hash(datos.nueva_contrasena)
    recuperacion.utilizado = True
    db.execute(
        update(RecuperacionContrasena)
        .where(RecuperacionContrasena.id_usuario == usuario.id_usuario,
               RecuperacionContrasena.id_recuperacion != recuperacion.id_recuperacion,
               RecuperacionContrasena.utilizado.is_(False))
        .values(utilizado=True)
    )
    db.commit()
    return {"mensaje": "Contraseña actualizada. Ya puedes iniciar sesión"}
