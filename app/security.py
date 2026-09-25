import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", interpolate=False)

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_MINUTES = int(
    os.environ["JWT_ACCESS_TOKEN_MINUTES"]
)

if len(JWT_SECRET_KEY) < 64:
    raise ValueError("La clave JWT debe tener al menos 64 caracteres")

if JWT_ACCESS_TOKEN_MINUTES <= 0:
    raise ValueError("La duración del token debe ser mayor que cero")


password_hash = PasswordHash.recommended()


def crear_hash(contrasena: str) -> str:
    return password_hash.hash(contrasena)


def verificar_contrasena(contrasena: str, hash_guardado: str) -> bool:
    return password_hash.verify(contrasena, hash_guardado)


def crear_token_acceso(id_usuario: int) -> str:
    ahora = datetime.now(timezone.utc)
    vencimiento = ahora + timedelta(
        minutes=JWT_ACCESS_TOKEN_MINUTES
    )

    contenido = {
        "sub": str(id_usuario),
        "iat": ahora,
        "exp": vencimiento,
    }

    return jwt.encode(
        contenido,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )



