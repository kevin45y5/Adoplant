#!/usr/bin/env bash
# Entrada del contenedor de la API AdopPlant.
set -euo pipefail

# Las migraciones se aplican solo cuando se piden de forma explicita.
# La base es compartida con AdopPlant.Analytics y el equipo ejecuta
# Alembic a mano al preparar cada revision.
if [ "${APLICAR_MIGRACIONES:-0}" = "1" ]; then
  echo "Aplicando migraciones Alembic (upgrade head)..."
  python -m alembic upgrade head
fi

exec "$@"
