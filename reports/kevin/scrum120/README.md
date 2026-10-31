# SCRUM-120 — Seguridad de la API Python

Responsable de la entrega: Kevin Meza. Fecha: 30 de octubre de 2026.

## Alcance autorizado

Solo FastAPI/Python, por instrucción del usuario. No se probó C# Analytics, ni `/api/metricas`. El caso C-SEC-04 original de Jira apunta a C# y aquí se presenta una **adaptación Python**, identificada expresamente. No debe marcarse el alcance original completo como PASS basándose solo en este reporte.

Herramientas ejecutadas: pytest, FastAPI/Starlette TestClient, PyJWT, SQLAlchemy y PostgreSQL local `adopplant_test`. TestClient envía peticiones ASGI en proceso a las rutas reales de `app.main:app`; no usa un servidor HTTP por TCP ni Render. La base sí es PostgreSQL real. Se crean cuentas ficticias por caso dentro de una transacción externa que se revierte al finalizar. Solo se simula la entrega de correo para evitar envíos externos. Las claves JWT de prueba son ficticias.

## Resultados

**7 escenarios PASS, 0 fallos**. Evidencias:

- [Ejecución HTML](ejecucion.html).
- [Salida completa de consola](../scrum120_ejecucion.txt).
- [JUnit XML](resultados.xml).
- [Código de las pruebas](../../../tests/test_seguridad_api_postgres.py).
- [Colección Postman preparada](../../../postman/SCRUM-120_python.postman_collection.json).

| Caso | Comprobación efectiva | Resultado | Log |
|---|---|---|---|
| C-SEC-01 | Perfil, administración y notificaciones sin token: 401 y WWW-Authenticate: Bearer | PASS | [Peticiones](peticiones/test_csec_01_sin_token.json) |
| C-SEC-02 | Firma incorrecta y payload de usuario alterado a administrador: 401 | PASS | [Peticiones](peticiones/test_csec_02_firma_invalida_y_payload_modificado.json) |
| C-SEC-03 | Token expirado: 401 y desafío Bearer | PASS | [Peticiones](peticiones/test_csec_03_token_expirado.json) |
| C-SEC-04, adaptación Python | Administración de usuarios: usuario normal 403, administrador 200; sin contraseñas en respuesta | PASS Python | [Peticiones](peticiones/test_csec_04_roles_administracion_python.json) |
| C-SEC-05 | Diez intentos inválidos entre cuenta existente/desconocida: respuesta genérica uniforme; acceso válido posterior | PASS para consistencia | [Peticiones](peticiones/test_csec_05_intentos_repetidos_sin_filtracion.json) |
| C-SEC-06 | Tres entradas SQLi en login y búsqueda administrativa: no permiten acceso ni cambian el total de usuarios; el login usa parámetros SQL separados | PASS | [Peticiones](peticiones/test_csec_06_inyeccion_sql_parametrizada.json) |
| C-SEC-07 | Login y recuperación uniformes para correo conocido/desconocido; notificación ajena e inexistente producen mismo 404; propietario obtiene 200 | PASS en rutas evaluadas | [Peticiones](peticiones/test_csec_07_enumeracion_login_recuperacion_y_recursos.json) |

Los logs guardan método, ruta, estado, desafío de autenticación y cuerpo de respuesta. No guardan contraseñas, claves ni cabeceras Authorization; los access_token se sustituyen por `[OMITIDO]`.

## Límites que deben acompañar la entrega

- No se ejecutó OWASP ZAP. No existe un reporte ZAP ni se presenta este trabajo como un escaneo OWASP completo.
- La colección Postman está preparada y validada como JSON; no se ha ejecutado con Postman/Newman. Los resultados acreditados provienen de pytest.
- C-SEC-05 verifica respuestas genéricas con un número acotado de intentos; **no demuestra bloqueo, limitación de tasa ni resistencia a fuerza bruta sostenida**. El login revisado no incorpora rate limiting.
- C-SEC-07 compara contenido y estado, no tiempos de respuesta. No cubre todas las rutas. El registro sigue informando conflictos de correo/teléfono duplicado; no se acredita ausencia global de enumeración.
- No se probaron TLS, proxy, configuración de despliegue, correo real ni infraestructura de producción. Tampoco se ha demostrado ausencia de todas las vulnerabilidades críticas.
- Para la entrega formal siguen pendientes las capturas y la vinculación de código y evidencias en Jira. Jira no fue modificado.

## Reproducir

Desde `Adoplant`, con `.env` local configurado y esquema importado en `adopplant_test`:

```powershell
$env:DB_NAME='adopplant_test'
$env:SCRUM120_TEST_DB='1'
$env:SCRUM120_LOG_DIR='reports/kevin/scrum120/peticiones'
.\.venv\Scripts\python.exe -m pytest tests/test_seguridad_api_postgres.py -v --html=reports/kevin/scrum120/ejecucion.html --self-contained-html --junitxml=reports/kevin/scrum120/resultados.xml
Remove-Item Env:DB_NAME, Env:SCRUM120_TEST_DB, Env:SCRUM120_LOG_DIR
```

La suite rechaza servidores distintos de localhost/127.0.0.1/::1 y nombres de base distintos de `adopplant_test`. Para Postman, importar la colección y configurar cuentas ficticias, tokens de administrador/usuario, token expirado e ID de una notificación ajena. El prerrequisito impide dirigir esa colección fuera de HTTP localhost/127.0.0.1. No usar cuentas ni tokens de producción.
