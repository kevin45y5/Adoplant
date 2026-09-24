 feature/SCRUM-14-Notificaciones
"""Dependencias de autenticacion compartidas por los endpoints."""

import re
 Main

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
 feature/SCRUM-14-Notificaciones

from app.database import get_db
from app.models import Usuario
from app.security import JWT_ALGORITHM, JWT_SECRET_KEY

_bearer = HTTPBearer(auto_error=False)


def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    """Valida el bearer token y devuelve la cuenta activa que lo emitio."""
    no_autorizado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Autenticacion requerida",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credenciales is None:
        raise no_autorizado

from sqlalchemy import select

from app.database import get_db
from app.models import Administrador, Usuario
from app.security import JWT_ALGORITHM, JWT_SECRET_KEY


bearer = HTTPBearer(auto_error=False)


def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    error_autenticacion = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token ausente, inválido o vencido",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credenciales is None:
        raise error_autenticacion
 Main

    try:
        contenido = jwt.decode(
            credenciales.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
 feature/SCRUM-14-Notificaciones
        )
        id_usuario = int(contenido["sub"])
        if id_usuario <= 0:
            raise ValueError("subject invalido")
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise no_autorizado from None

    usuario = db.get(Usuario, id_usuario)
    if usuario is None:
        raise no_autorizado
    if usuario.estado != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta esta bloqueada",
   
       options={"require": ["sub", "exp", "iat"]},
        )

        identificador = contenido["sub"]

        if not isinstance(identificador, str):
            raise error_autenticacion

        if re.fullmatch(r"[1-9][0-9]{0,9}", identificador) is None:
            raise error_autenticacion

        id_usuario = int(identificador)

        if id_usuario > 2_147_483_647:
            raise error_autenticacion

    except jwt.InvalidTokenError:
        raise error_autenticacion from None

    usuario = db.get(Usuario, id_usuario)

    if usuario is None:
        raise error_autenticacion

    if usuario.estado != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta está bloqueada",
        )

    return usuario


def obtener_administrador_actual(
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
) -> Usuario:
    consulta = select(Administrador.id_administrador).where(
        Administrador.id_usuario == usuario.id_usuario
    )
    if db.execute(consulta).scalar_one_or_none() is None:
        raise HTTPException(
            status_code=403, detail="Se requieren permisos de administrador"
 Main
        )
    return usuario
