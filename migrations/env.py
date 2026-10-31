"""Migraciones con la misma conexión privada que utiliza la API."""
import os

from alembic import context
from sqlalchemy import create_engine

from app.database import database_url, engine, normalizar_url

# Neon: las migraciones van por la conexión directa (sin el sufijo -pooler).
_cadena_directa = os.environ.get("DATABASE_URL", "").strip()
if _cadena_directa:
    engine_migraciones = create_engine(
        normalizar_url(_cadena_directa), connect_args={"connect_timeout": 10}
    )
else:
    engine_migraciones = engine

# Aún no existen modelos para las 14 tablas. Se escriben revisiones explícitas:
# autogenerate podría interpretar las tablas sin modelo como tablas a eliminar.
if context.is_offline_mode():
    context.configure(url=database_url, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    with engine_migraciones.connect() as connection:
        context.configure(connection=connection, target_metadata=None)
        with context.begin_transaction():
            context.run_migrations()
