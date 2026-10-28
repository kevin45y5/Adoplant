# AdopPlant API (FastAPI) - README

API REST monolítica compartida por la web y la aplicación Flutter. Proyecto Python 3.14 + FastAPI + PostgreSQL.

## Requisitos

- [Python 3.14](https://www.python.org/)

## Ejecutar tests

Los tests unitarios **no requieren base de datos**. Se pueden ejecutar directamente desde esta carpeta.

```bash
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

**Nota:** Si el comando `python -m pytest --cov=app --cov-report=html` te devuelve
`error: unrecognized arguments: --cov=app --cov-report=html`, significa que
`pytest-cov` no está instalado. Instálalo manualmente:

```bash
pip install pytest-cov pytest-html
```

Luego vuelve a ejecutar el comando de cobertura.

# Ejecutar todos los tests
python -m pytest -q

# Ejecutar con más detalle
python -m pytest -v

# Ejecutar un archivo de tests específico
python -m pytest tests/test_autenticacion.py -v
```

## Tests de aceptación y E2E (Jira SCRUM-89, 90, 91, 94)

Estos tests validan flujos de extremo a extremo y aceptación de la aplicación web. Requieren la API levantada y, en algunos casos, PostgreSQL con datos de seed.

| Ticket | Tipo | Archivos de test | Qué valida |
|--------|------|------------------|------------|
| **SCRUM-89** | Test E2E | `tests/test_web_recuperacion.py`, `tests/recuperacion_web.test.cjs`, `tests/sesion_web.test.cjs` | Flujo E2E de recuperación y sesión en la app web de plantas |
| **SCRUM-90** | Test E2E | `tests/perfil_web.test.cjs`, `tests/recuperacion_web.test.cjs`, `tests/sesion_web.test.cjs` | Pruebas web E2E/frontend (perfil, recuperación, sesión) |
| **SCRUM-91** | Test Aceptación | `tests/test_web_recuperacion.py`, `tests/recuperacion_web.test.cjs`, `tests/sesion_web.test.cjs` | Pruebas web de aceptación de recuperación y sesión |
| **SCRUM-94** | Test Aceptación | (archivos de aceptación admin) | Prueba funcional de aceptación del panel de administración |

### Ejecutar tests web (Python)

```powershell
# Desde la carpeta Adoplant/
# Asegúrate de que la API esté corriendo en http://127.0.0.1:8000
# y PostgreSQL en localhost:5432 con datos de seed

$env:DB_HOST="localhost"; $env:DB_PORT="5432"; $env:DB_USER="postgres"; $env:DB_PASSWORD="javarberl"; $env:DB_NAME="plant"

python -m pytest tests/test_web_recuperacion.py -v          # SCRUM-89, SCRUM-91
python -m pytest tests/test_admin_panel.py -v               # SCRUM-94 (administración)
```

### Ejecutar tests web frontend (JavaScript/Node)

Estos archivos `.cjs` se ejecutan con Node y requieren un navegador (Playwright/Puppeteer según configuración):

```powershell
# Desde la carpeta Adoplant/
node tests/perfil_web.test.cjs                              # SCRUM-90
node tests/recuperacion_web.test.cjs                        # SCRUM-89, SCRUM-90, SCRUM-91
node tests/sesion_web.test.cjs                              # SCRUM-89, SCRUM-90, SCRUM-91
```

**Total de tests:** 200 tests (según `pytest --collect-only`).

## Ver reportes

pytest muestra el resumen en consola. Para reportes detallados:

```bash
# Reporte HTML (requiere pytest-html)
pip install pytest-html
python -m pytest --html=report.html --self-contained-html

# Cobertura de código (requiere pytest-cov)
pip install pytest-cov
python -m pytest --cov=app --cov-report=html
```

El reporte HTML de cobertura se genera en `htmlcov/` y el reporte de ejecución en `report.html`.

## Ejecutar la API localmente (opcional)

```bash
# Con venv activado
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Documentación en http://127.0.0.1:8000/docs. Para el stack completo con Analytics ver ../INICIAR_PROYECTOS.md.
