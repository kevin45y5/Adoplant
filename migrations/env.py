"""Migraciones con la misma conexión privada que utiliza la API."""
from alembic import context

from app.database import database_url, engine

# Aún no existen modelos para las 14 tablas. Se escriben revisiones explícitas:
# autogenerate podría interpretar las tablas sin modelo como tablas a eliminar.
if context.is_offline_mode():
    context.configure(url=database_url, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=None)
        with context.begin_transaction():
            context.run_migrations()
