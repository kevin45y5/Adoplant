"""Adopta la base existente, incluido el teléfono obligatorio y único.

En una base nueva, importar sql/base_inicial.sql antes de ejecutar upgrade head.
No recrea ni elimina tablas del negocio.
"""
from alembic import op
from sqlalchemy import inspect, text

revision = "0001_base_existente"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    inspector = inspect(connection)
    expected = {
        "usuario", "administrador", "categoria", "planta", "fotografia",
        "solicitud_adopcion", "adopcion", "chat", "chat_participante",
        "mensaje", "punto_encuentro", "notificacion", "reporte",
        "recuperacion_contrasena",
    }
    if not expected.issubset(inspector.get_table_names(schema="public")):
        raise RuntimeError("Falta la base inicial: importar sql/base_inicial.sql en una base vacía")
    phone = next(c for c in inspector.get_columns("usuario", schema="public") if c["name"] == "telefono")
    unique_phone = connection.execute(text("""
        SELECT i.indisunique AND i.indisvalid
        FROM pg_index i JOIN pg_class idx ON idx.oid = i.indexrelid
        JOIN pg_namespace n ON n.oid = idx.relnamespace
        WHERE n.nspname = 'public' AND idx.relname = 'uq_usuario_telefono'
    """)).scalar()
    if phone["nullable"] or not unique_phone:
        raise RuntimeError("La base no incluye el ajuste de teléfono obligatorio y único")


def downgrade():
    raise RuntimeError("La base inicial se conserva; no se permite eliminar sus tablas mediante downgrade")
