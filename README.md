# AdopPlant API

Proyecto académico: API REST monolítica compartida por la futura web y aplicación Flutter.

Documentación vigente:

- `docs/entrega_classroom.md`: requisitos de entrega grupal e individual y guía de Postman.
- `docs/despliegue_render.md`: configuración y actualización del servicio público.
- `docs/historias_de_usuario_revisadas.md`: las 17 historias y criterios actuales.
- `docs/subtareas_backend_jira.md`: desglose del trabajo entre los cinco integrantes.
- `docs/revision_historias_backend.md`: decisiones tomadas para conservar el diagrama y la base.
- `docs/guia_tecnica.md`: arquitectura y tecnologías acordadas.

Avance implementado: registro e inicio de sesión por correo o teléfono con hash
Argon2 y JWT, consulta y edición de cuenta propia, administración de usuarios y envío de solicitudes de
adopción con notificación interna al donante. SCRUM-6 incluye consultas privadas,
corrección del mensaje y retiro de solicitudes pendientes.

## Instalación en Windows

Desde esta carpeta, con Python 3.14 (versión usada en desarrollo):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Editar `.env` con la conexión local y generar una clave JWT aleatoria de al menos
64 caracteres. No sobrescribir el `.env` existente ni subirlo a Git.

Para generar una clave sin mostrarla ni copiarla manualmente, ejecutar después de
crear `.env`:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; from dotenv import set_key; set_key('.env', 'JWT_SECRET_KEY', secrets.token_hex(32)); print('Clave JWT configurada')"
```

## Base de datos

La base actual ya está preparada. No importar scripts sobre ella.
Para una instalación nueva, crear una base PostgreSQL 18 vacía e importar
sql/base_inicial.sql con psql (incluye comandos propios de psql):

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -h localhost -U postgres -d adopplant -v ON_ERROR_STOP=1 -f sql/base_inicial.sql
.\.venv\Scripts\python.exe -m alembic upgrade head
```

El archivo no incluye usuarios ni contraseñas ni datos de ejemplo. La revisión inicial
verifica que existan las tablas y el ajuste de teléfono, y registra la versión.
Alembic añade su propia tabla alembic_version: son 14 tablas del negocio más esta
tabla técnica. La primera revisión no elimina tablas al intentar revertirla.

Futuros cambios: crear una revisión con `alembic revision -m "descripcion"`, escribir
y revisar upgrade/downgrade, luego aplicar `alembic upgrade head`. Usar el Python
del entorno como en los comandos anteriores. No usar --autogenerate por ahora:
no todas las tablas tienen modelo; las demás tablas también deben conservarse.

## Ejecutar y comprobar

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Swagger: http://127.0.0.1:8000/docs
Bienvenida: GET http://127.0.0.1:8000/
Conexión: GET http://127.0.0.1:8000/api/prueba-db
El alias /prueba-db se conserva por compatibilidad.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m alembic current
```

Las pruebas predeterminadas no requieren PostgreSQL. Las pruebas de integración
de SCRUM-6 se habilitan con `SCRUM6_TEST_DB=1` y revierten sus datos al finalizar.
La comprobación manual /api/prueba-db sí requiere la conexión configurada.
Endpoints funcionales actuales:

- `POST /api/auth/registro`
- `POST /api/auth/login`
- `GET /api/usuarios/me`
- `PATCH /api/usuarios/me`
- `GET /api/admin/usuarios`
- `GET /api/admin/usuarios/{id_usuario}`
- `PATCH /api/admin/usuarios/{id_usuario}/estado`
- `POST /api/solicitudes` (SCRUM-6: envío autenticado y notificación interna).
- `GET /api/solicitudes` (enviadas/recibidas, filtros y paginación).
- `GET /api/solicitudes/{id}` (detalle privado para adoptante y donante).
- `PATCH /api/solicitudes/{id}` (corregir mensaje pendiente).
- `DELETE /api/solicitudes/{id}` (retirar solicitud pendiente).

Importar la colección `postman/SCRUM-6.postman_collection.json`; generar el entorno
local con `python -m scripts.preparar_postman` usando el Python de `.venv`.

Los endpoints de diagnóstico no cuentan como funciones del negocio. Las operaciones
pendientes se encuentran en las historias y subtareas vigentes.

## Enlaces del avance publicado

- API: https://adopplant-api.onrender.com
- Swagger: https://adopplant-api.onrender.com/docs
- Postman (SCRUM-1 y SCRUM-18): https://documenter.getpostman.com/view/58260475/2sBYB4LSGg

El enlace de Postman indicado no cubre todavía todos los módulos del equipo.

## Integración del equipo (28-09-2026)

Ver `docs/integracion_grupal.md` para procedencia, pruebas, límites y despliegue.
Se integran plantas, fotografías por URL, notificaciones, chat, moderación y reportes,
además de usuarios y solicitudes. OpenAPI reúne 35 operaciones de negocio.
Importar `postman/AdopPlant_API_grupal_integrada.postman_collection.json` como colección nueva.
Categorías y aceptación de solicitudes aún no tienen endpoints recibidos.

## Cuentas y datos de prueba

`scripts/seed_pruebas.py` crea (de forma **idempotente**) las cuentas y los datos
que usan las suites automatizadas:

| Rol | Usuario | Contraseña |
|---|---|---|
| Administrador | `admin.panel@adopplant.com` | `Admin2026panel` |
| Donante | `donante.pruebas@adopplant.com` | `Donante2026!` |
| Adoptante | `adoptante.pruebas@adopplant.com` | `Adoptante2026!` |

Además inserta 4 categorías y 3 plantas de ejemplo. Se puede ejecutar las veces
que haga falta sin duplicar registros.

```powershell
# Base local (Windows): usa el .env del repositorio
.\.venv\Scripts\python.exe -m scripts.seed_pruebas

# Con la pila de contenedores
docker compose run --rm seed
```

> Son cuentas **solo para desarrollo y QA**. No existen en staging/producción.

## Contenedores y devcontainer

La API se puede ejecutar en Docker sin cambiar el flujo de trabajo en Windows.
No hace falta ninguna imagen base propia: la oficial `python:3.14-slim-bookworm`
basta (todas las dependencias de `requirements.txt` traen ruedas `cp314`).

```powershell
# Pila completa del proyecto (base + API Python + API .NET de Analytics)
cd "C:\Users\sault\Documents\para mientras"
docker compose up -d --build
docker compose run --rm seed        # cuentas y plantas de prueba

# Desde esta carpeta (el compose.yaml incluye el de la raíz)
cd "C:\Users\sault\Documents\para mientras\Adoplant"
docker compose up -d --build

# Solo esta API
docker build -t adopplant-api:local .
docker run --rm -p 8000:8000 --env-file .env adopplant-api

# Pruebas unitarias en contenedor (no requieren base de datos)
docker run --rm --env-file .env adopplant-api python -m pytest -q
```

| Recurso | URL |
|---|---|
| API + web de plantas | <http://localhost:8000> |
| Web de plantas | <http://localhost:8000/views/index.html> |
| Swagger | <http://localhost:8000/docs> |
| OpenAPI | <http://localhost:8000/openapi.json> |
| PostgreSQL del compose | `localhost:55432` (`postgres` / la clave del `.env`) |

- `Dockerfile`: imagen de ejecución sobre `python:3.14-slim-bookworm`, usuario
  sin privilegios y `HEALTHCHECK`.
- `docker/entrypoint.sh`: aplica `alembic upgrade head` solo si se pide con
  `APLICAR_MIGRACIONES=1` (en staging y producción se ejecuta a mano).
- `compose.yaml`: atajo que **incluye** el compose de la raíz del workspace, de
  modo que esta API y la de Analytics nunca se desincronicen.
- `.devcontainer/`: entorno de desarrollo en VS Code con Python 3.14, Node 22,
  cliente `psql` 18 y su propia PostgreSQL 18. Opcional: el flujo habitual
  (Windows + `.venv`) sigue igual. No toca el `.venv` de Windows (usa
  `/home/vscode/venv`) y su base es limpia y desechable.
- Detalle completo de la pila en `../CONTENEDORES.md`.

## Pruebas automatizadas

| Suite | Herramienta | Ticket |
|---|---|---|
| Carga básica (`GET /`, `GET /api/plantas`) | k6 | **SCRUM-92** |
| Carga sostenida (catálogo + detalle) | k6 | **SCRUM-95** |
| Estrés (rampa 0 → 200 VU, pico, recuperación) | k6 | **SCRUM-121** |
| Contrato OpenAPI + casos C-SEC-01…07 | Newman | **SCRUM-86**, **SCRUM-120** |
| Seguridad de la API | OWASP ZAP | **SCRUM-120** |

```powershell
# Desde la raíz del workspace
docker compose -f docker-compose.yml -f compose.k6-api.yaml      run --rm k6-api
docker compose -f docker-compose.yml -f compose.k6-api-load.yaml run --rm k6-api-load
docker compose -f docker-compose.yml -f compose.k6-stress.yaml   run --rm k6-stress
docker compose -f docker-compose.yml -f compose.newman.yaml      run --rm newman
docker compose -f docker-compose.yml -f compose.zap.yaml         run --rm zap-api
```

- Guiones: `tests/perf/` (k6) y `postman/` (Newman).
- Reportes: `../tests/reports/{k6,newman,zap}`.
- Comandos, criterios y solución de problemas: **`../tests/README.md`**.
- La web también tiene pruebas con Node 22: `node --test tests/*.cjs`.
