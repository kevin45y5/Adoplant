"""Dependencias de autenticacion compartidas por los endpoints."""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

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

    try:
        contenido = jwt.decode(
            credenciales.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
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
        )
    return usuario
