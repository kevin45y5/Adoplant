import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

# Busca .env en la carpeta principal del proyecto.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", interpolate=False)


def normalizar_url(cadena: str) -> str:
    """Adapta una URL de Neon/Render al driver psycopg 3 de SQLAlchemy.

    Acepta `postgres://` y `postgresql://`; SQLAlchemy necesita el prefijo
    `postgresql+psycopg://` porque psycopg2 no está instalado.
    """
    cadena = cadena.strip().strip('"').strip("'")
    if cadena.startswith("postgres://"):
        cadena = "postgresql://" + cadena[len("postgres://"):]
    if cadena.startswith("postgresql://"):
        cadena = "postgresql+psycopg://" + cadena[len("postgresql://"):]
    return cadena


# Neon (y Render) entregan DATABASE_URL. Para la API se prefiere la conexión
# con pooler (-pooler); las migraciones usan la directa (ver migrations/env.py).
_cadena_pooled = os.environ.get("DATABASE_URL_POOLED", "")
_cadena_directa = os.environ.get("DATABASE_URL", "")

if _cadena_pooled or _cadena_directa:
    database_url: URL | str = normalizar_url(_cadena_pooled or _cadena_directa)
else:
    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
        query={"sslmode": os.environ["DB_SSLMODE"]} if os.environ.get("DB_SSLMODE") else {},
    )

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_recycle=300,  # Neon cierra conexiones inactivas
    connect_args={"connect_timeout": 10},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
)


def get_db():
    with SessionLocal() as db:
        yield db
