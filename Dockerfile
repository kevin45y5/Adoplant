# Imagen de la API AdopPlant.
#
# La imagen oficial de Python es suficiente como base: todas las dependencias
# fijadas en requirements.txt publican ruedas (wheels) para CPython 3.14 en
# Linux, por lo que no hace falta compilar nada ni instalar librerías del
# sistema (psycopg[binary] incluye libpq y Pillow incluye sus decodificadores).
# No hay una imagen base propia que mantener.
FROM python:3.14-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /srv/app

# Usuario sin privilegios para ejecutar la API.
RUN groupadd --system adopplant \
 && useradd --system --gid adopplant --create-home --home-dir /home/adopplant adopplant

# Primero las dependencias: esta capa se reutiliza cuando solo cambia el código.
COPY requirements.txt ./
RUN pip install --no-cache-dir --requirement requirements.txt

COPY --chown=adopplant:adopplant app ./app
COPY --chown=adopplant:adopplant views ./views
COPY --chown=adopplant:adopplant migrations ./migrations
COPY --chown=adopplant:adopplant scripts ./scripts
COPY --chown=adopplant:adopplant sql ./sql
COPY --chown=adopplant:adopplant tests ./tests
COPY --chown=adopplant:adopplant alembic.ini pytest.ini ./
COPY --chmod=0755 docker/entrypoint.sh /usr/local/bin/entrypoint.sh

USER adopplant

EXPOSE 8000

# Comprobación sin herramientas externas: el propio Python consulta la API.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD ["python", "-c", "import urllib.request as u; u.urlopen('http://127.0.0.1:8000/', timeout=4)"]

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
