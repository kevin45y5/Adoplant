# AdopPlant API (FastAPI) - README

API REST monolítica compartida por la web y la aplicación Flutter. Proyecto Python 3.14 + FastAPI + PostgreSQL.

## Requisitos

- [Python 3.14](https://www.python.org/) o
- [Docker](https://www.docker.com/) para ejecutar sin instalar Python localmente

## Ejecutar tests (SIN necesidad de levantar otros servicios)

Los tests unitarios **no requieren base de datos**. Se pueden ejecutar directamente desde esta carpeta.

### Opción 1: Con entorno local (venv)

`ash
# Desde la carpeta Adoplant/
python -m venv .venv
# Activar venv
# Linux/macOS/Codespaces:
source .venv/bin/activate
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Windows (CMD):
.\.venv\Scripts\activate.bat

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar tests
python -m pytest -q
`

### Opción 2: Con Docker (100% portable - Windows/Linux/macOS/GitHub Codespaces)

Desde **esta misma carpeta** (Adoplant/):

#### Linux/macOS/Codespaces (bash/zsh)

`ash
docker run --rm \
  -v "C:\Users\sault\Documents\para mientras":/app \
  -w /app \
  python:3.14-slim \
  sh -c "pip install --no-cache-dir -r requirements.txt && python -m pytest -q"
`

#### Windows (PowerShell)

`powershell
docker run --rm -v "C:\Users\sault\Documents\para mientras:/app" -w /app python:3.14-slim sh -c "pip install --no-cache-dir -r requirements.txt && python -m pytest -q"
`

#### Windows (CMD)

`cmd
docker run --rm -v "%CD%:/app" -w /app python:3.14-slim sh -c "pip install --no-cache-dir -r requirements.txt && python -m pytest -q"
`

**Nota:** Si abres esta carpeta como proyecto raíz en GitHub Codespaces (sin la carpeta para mientras), todos los comandos funcionan con rutas relativas. No hay referencias a rutas absolutas del equipo.

## Ejecutar la API localmente (opcional)

`ash
# Con venv activado
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
`

Documentación en http://127.0.0.1:8000/docs. Para el stack completo con Analytics ver ../INICIAR_PROYECTOS.md o usar docker compose desde la raíz del workspace.

## DevContainer

Existe ./.devcontainer/ con Python 3.14, Node 22 y PostgreSQL 18 propio. Abre **esta carpeta** directamente en VS Code Dev Containers o en GitHub Codespaces.
