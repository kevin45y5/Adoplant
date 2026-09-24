# AdopPlant API

Proyecto académico: API REST monolítica compartida por la futura web y aplicación Flutter.

Documentación vigente:

- `docs/historias_de_usuario_revisadas.md`: las 17 historias y criterios actuales.
- `docs/subtareas_backend_jira.md`: desglose del trabajo entre los cinco integrantes.
- `docs/revision_historias_backend.md`: decisiones tomadas para conservar el diagrama y la base.
- `docs/guia_tecnica.md`: arquitectura y tecnologías acordadas.

Avance implementado: registro e inicio de sesión por correo o teléfono con hash
Argon2 y JWT, consulta y edición de cuenta propia, y envío de solicitudes de
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
solo usuario tiene modelo; las demás tablas también deben conservarse.

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
- `POST /api/solicitudes` (SCRUM-6: envío autenticado y notificación interna).
- `GET /api/solicitudes` (enviadas/recibidas, filtros y paginación).
- `GET /api/solicitudes/{id}` (detalle privado para adoptante y donante).
- `PATCH /api/solicitudes/{id}` (corregir mensaje pendiente).
- `DELETE /api/solicitudes/{id}` (retirar solicitud pendiente).

Subtareas de solicitudes y guía para Postman: `docs/SCRUM-6-postman.md`.
Importar la colección `postman/SCRUM-6.postman_collection.json`; generar el entorno
local con `python -m scripts.preparar_postman` usando el Python de `.venv`.

Los endpoints de diagnóstico no cuentan como funciones del negocio. Las operaciones
pendientes se encuentran en las historias y subtareas vigentes.
