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

## Tests de aceptación y E2E (Jira SCRUM-89, 90 y 94)

Estos tests validan flujos de extremo a extremo y aceptación de la aplicación web. Requieren la API levantada y, en algunos casos, PostgreSQL con datos de seed.

| Ticket | Tipo | Archivos de test | Qué valida |
|--------|------|------------------|------------|
| **SCRUM-89** | Test E2E | `tests/test_web_recuperacion.py`, `tests/recuperacion_web.test.cjs`, `tests/sesion_web.test.cjs` | Flujo E2E de recuperación y sesión en la app web de plantas |
| **SCRUM-90** | Test E2E | `tests/perfil_web.test.cjs`, `tests/recuperacion_web.test.cjs`, `tests/sesion_web.test.cjs` | Pruebas web E2E/frontend (perfil, recuperación, sesión) |
| **SCRUM-94** | Test Aceptación | (archivos de aceptación admin) | Prueba funcional de aceptación del panel de administración |

> **SCRUM-91 no pertenece a este proyecto.** Según `TEST_CASES_JIRA_COMPLETO.md`, SCRUM-91 es la **UAT del módulo de Analytics** y se ejecuta en `../AdopPlant.Analytics/tests/uat/` (ver el README de ese proyecto).

### Ejecutar tests web (Python)

```powershell
# Desde la carpeta Adoplant/
# Asegúrate de que la API esté corriendo en http://127.0.0.1:8000
# y PostgreSQL en localhost:5432 con datos de seed

$env:DB_HOST="localhost"; $env:DB_PORT="5432"; $env:DB_USER="postgres"; $env:DB_PASSWORD="javarberl"; $env:DB_NAME="plant"

python -m pytest tests/test_web_recuperacion.py -v          # SCRUM-89
python -m pytest tests/test_admin_panel.py -v               # SCRUM-94 (administración)
```

### Ejecutar tests web frontend (JavaScript/Node)

Estos archivos `.cjs` se ejecutan con Node y requieren un navegador (Playwright/Puppeteer según configuración):

```powershell
# Desde la carpeta Adoplant/
node tests/perfil_web.test.cjs                              # SCRUM-90
node tests/recuperacion_web.test.cjs                        # SCRUM-89, SCRUM-90
node tests/sesion_web.test.cjs                              # SCRUM-89, SCRUM-90
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

## Pruebas de rendimiento y carga con k6 (SCRUM-92 y SCRUM-95)

Los scripts viven en `tests/perf/` y dejan la evidencia en `tests/perf/reports/`.

| Ticket | Script | Escenarios | Endpoints | Criterio de salida |
|---|---|---|---|---|
| **SCRUM-92** | `k6-api-baseline.js` | 1 VU / 1 min y 5 VU / 2 min | `GET /` y `GET /api/plantas` | HTTP 200, 0 % de errores y p95 ≤ 2 s |
| **SCRUM-95** | `k6-api-load.js` | 5 VU / 1 min y 10 VU / 5 min | `GET /api/plantas` y `GET /api/plantas/{id}` | 0 errores 500, p95 < 3 s y errores ≤ 1 % |

### Preparar el entorno

1. PostgreSQL con la base `plant` y los datos de prueba (idempotente):

   ```powershell
   cd "C:\Users\sault\Documents\Adoplant"
   .\.venv\Scripts\python.exe -m scripts.seed_pruebas
   ```

   Crea `admin.panel@adopplant.com` / `Admin2026panel` (lo usa SCRUM-92) y
   `donante.pruebas@adopplant.com` / `Donante2026!` (lo usa SCRUM-95). Los dos
   scripts inician sesión en su `setup`, así que sin estas cuentas la prueba falla.

2. API en `http://127.0.0.1:8000`:

   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

3. k6 instalado y en el PATH (`k6 version`).

### Ejecutar

```powershell
cd "C:\Users\sault\Documents\Adoplant"

k6 run -e BASE_URL=http://127.0.0.1:8000 tests/perf/k6-api-baseline.js   # SCRUM-92 (~3 min)
k6 run -e BASE_URL=http://127.0.0.1:8000 tests/perf/k6-api-load.js       # SCRUM-95 (~6 min)
```

- `BASE_URL` por defecto es `http://api:8000` (pensado para Docker); en local se pasa siempre.
- Credenciales: `-e ADMIN_USER=... -e ADMIN_PASSWORD=...` para SCRUM-92 y
  `-e DONOR_USER=... -e DONOR_PASSWORD=...` para SCRUM-95.
- Si un *threshold* incumple (p95 o tasa de errores), k6 termina con código distinto
  de cero: la ejecución **no** se aprueba.

### Ver los reportes

Cada ejecución escribe dos archivos en `tests/perf/reports/`:

| Archivo | Contenido |
|---|---|
| `scrum-92-baseline-reporte.html` | tabla legible: promedio, mediana, p95, máximo, tasa y muestras por métrica |
| `scrum-92-baseline-resumen.json` | volcado completo de k6 (evidencia cruda para Jira) |
| `scrum-95-load-reporte.html` / `scrum-95-load-resumen.json` | ídem para SCRUM-95 |

```powershell
Start-Process tests/perf/reports/scrum-92-baseline-reporte.html
Start-Process tests/perf/reports/scrum-95-load-reporte.html
```

El resumen corto (promedio, p95, tasa de error y checks) también se imprime en la
consola al terminar. `-e REPORTES_DIR=otra/carpeta` cambia el destino; la carpeta
debe existir.

## Ejecutar la API localmente (opcional)

```bash
# Con venv activado
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Documentación en http://127.0.0.1:8000/docs. Para el stack completo con Analytics ver ../INICIAR_PROYECTOS.md.
