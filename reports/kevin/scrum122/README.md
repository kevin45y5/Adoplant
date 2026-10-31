# SCRUM-122 — Reporte de ejecución y resultados

> **Alcance Jira corregido:** SCRUM-122 es el E2E completo de la app móvil PlantHaven (Flutter). Este checkout solo contiene Adoplant API/web; las pruebas Python, web, carga y seguridad resumidas abajo no validan los escenarios móviles. La ejecución específica quedó en **BLOCKED / NOT EXECUTED (0/10)** y se registró en el [comentario de SCRUM-122](https://jdavidg555-1788882610120.atlassian.net/browse/SCRUM-122). Consulta [el reporte específico de móvil](ejecucion_mobile.md). El caso no se marcó Pass/Done.

**Proyecto:** AdopPlant API (Python/FastAPI y web)

**Fecha de ejecución local:** 30 de octubre de 2026

**Repositorio:** [kevin45y5/Adoplant](https://github.com/kevin45y5/Adoplant)

**Colecciones:** [SCRUM-120 Python](../../../postman/SCRUM-120_python.postman_collection.json), [API revisada](../../../postman/AdopPlant_API_revisada.postman_collection.json), [API de pruebas](../../../postman/AdopPlant_API_pruebas.postman_collection.json)

## Resultado de esta ejecución

| Estrategia | Herramienta/evidencia | Resultado | Alcance y límite |
|---|---|---|---|
| Unitarias | pytest 9.1.1 | **PASS — 124 pruebas, 13 subtests** | Suite Python ejecutada el 30/10/2026. Incluye un aviso de deprecación de Starlette/httpx. |
| Componentes | Node.js 24 `node --test` | **PASS — 45/45** | Componentes/flujo web con simulaciones DOM y API. Este checkout no contiene la app React Native/Flutter ni pruebas móviles. |
| API | pytest, FastAPI TestClient, SQLAlchemy/SQLite o dobles | **PASS dentro de las 124** | Solicitudes ASGI en proceso; no equivale a ejecución desde Postman ni prueba de red externa. Integración PostgreSQL opcional fue omitida. |
| Extremo a extremo | Node.js 24 `node --test` y pruebas web Python | **PASS dentro de las suites anteriores** | E2E lógico de interfaz/API simulada documentado en el README del proyecto; sin navegador real/Playwright. |
| Carga | k6; reportes preexistentes SCRUM-92 y SCRUM-95 | **PASS histórico; no repetido en esta ejecución** | SCRUM-92: 1/5 VU, 1.861 solicitudes, 3.102 checks, 0 fallos HTTP, p95 agregado 72,36 ms. SCRUM-95: 5/10 VU, 11.086 checks, 0 fallos HTTP, p95 agregado 128,89 ms. Los umbrales registrados pasaron. Ver reportes y fecha original en los archivos fuente. |
| Estrés | k6 `tests/perf/k6-api-stress.js` | **NO EJECUTADO en esta sesión** | `k6` no está instalado/disponible en PATH. El script de estrés apunta también a Analytics .NET, fuera de este checkout. |
| Seguridad | pytest + TestClient + PostgreSQL local, SCRUM-120 | **PASS histórico — 7/7** | Evidencia ejecutada el 30/10/2026; no forma parte de la ejecución Python actual. La adaptación C-SEC-04 cubre Python, no Analytics .NET. No es escaneo ZAP ni certificación integral. |
| UAT | Revisión humana con usuarios/criterios Jira | **PENDIENTE** | No se obtuvo aceptación de usuarios ni el inventario de casos de Jira; no se puede afirmar cobertura UAT del 30–40% ni marcar casos como ejecutados sin esa evidencia. Se adjunta propuesta de muestra. |

**Suite Python completa:** 124 passed, 101 skipped, 13 subtests passed, 1 warning (7,60 s). Los omitidos son principalmente integraciones PostgreSQL que requieren activación explícita. No se habilitaron para no apuntar por accidente a la base local de desarrollo.

**Suite web JavaScript:** 45 passed, 0 failed, 0 skipped (1,16 s).

**API local previamente iniciada:** `GET /` y `/docs` respondieron 200; `/prueba-db` verificó conexión con la base `adopplant` (0 usuarios en ese momento). Esta comprobación de disponibilidad no reemplaza pruebas de aceptación.

## Evidencia

- [Reporte HTML de la suite Python](unitarias_api_e2e.html)
- [Resultados JUnit XML de Python](resultados-python.xml)
- [Salida de pruebas web Node](node-web.txt)
- [Reporte histórico de carga SCRUM-92](../../../tests/perf/reports/scrum-92-baseline-reporte.html) y [resumen JSON](../../../tests/perf/reports/scrum-92-baseline-resumen.json)
- [Reporte histórico de carga SCRUM-95](../../../tests/perf/reports/scrum-95-load-reporte.html) y [resumen JSON](../../../tests/perf/reports/scrum-95-load-resumen.json)
- [Reporte de seguridad SCRUM-120](../scrum120/README.md), [JUnit](../scrum120/resultados.xml), [salida de consola](../scrum120_ejecucion.txt), [código de casos](../../../tests/test_seguridad_api_postgres.py)
- [Pruebas Python](../../../tests) y [pruebas web JS](../../../tests)

Los resúmenes JSON SCRUM-92 y SCRUM-95 fueron saneados: el campo de token de acceso que había quedado en `setup_data` ahora está redactado. Se mantienen las métricas originales.

## Muestra UAT propuesta para Jira

Al no disponer del total de casos de Jira, la proporción se calcula al consultar el inventario. La regla será seleccionar entre `ceil(0,30 × total)` y `floor(0,40 × total)` casos UAT, verificando que el intervalo admita un entero. Como muestra concreta, si existen 15 casos UAT, ejecutar 5 (33,3%). Los casos propuestos son borradores y no están ejecutados ni aceptados:

| ID propuesto | Escenario de aceptación | Resultado esperado | Estado |
|---|---|---|---|
| UAT-01 | Registrar usuario con datos válidos e iniciar sesión | Cuenta creada; acceso con sus credenciales | Not Executed |
| UAT-02 | Publicar planta con datos y fotografía válidos | Publicación aparece en el catálogo | Not Executed |
| UAT-03 | Buscar y filtrar plantas en el catálogo | Resultados respetan los filtros elegidos | Not Executed |
| UAT-04 | Enviar una solicitud de adopción y consultarla | El solicitante ve confirmación y el donante la solicitud | Not Executed |
| UAT-05 | Donante acepta una solicitud pendiente | Estado se actualiza y las partes ven la decisión | Not Executed |

Al consultar el total real de Jira se debe elegir una muestra dentro del rango, registrar quién valida cada escenario y adjuntar evidencia de aceptación. Un PASS automatizado no es aceptación UAT.

## Casos por estrategia para vincular en Jira

Son referencias de trazabilidad propuestas; requieren vinculación con los casos Jira existentes o creación por el responsable del proyecto. No se actualizaron incidencias Jira en esta ejecución.

| Estrategia | Casos sugeridos | Evidencia asociada |
|---|---|---|
| Unitarias | C-UNIT-01 validación/autenticación; C-UNIT-02 reglas de solicitudes | `tests/test_security.py`, `tests/test_solicitudes.py` |
| Componentes web | C-COMP-01 filtros del catálogo; C-COMP-02 formulario/foto de publicación | `tests/catalogo_web.test.cjs`, `tests/publicar_web.test.cjs` |
| API | C-API-01 rutas de perfil; C-API-02 catálogo y filtros | `tests/test_perfil.py`, `tests/test_catalogo_postgres.py` (integración PostgreSQL omitida en la corrida actual) |
| E2E | C-E2E-01 sesión; C-E2E-02 solicitud y decisión | `tests/sesion_web.test.cjs`, `tests/solicitudes_web.test.cjs` |
| Carga | C-LOAD-01 1/5 VU; C-LOAD-02 5/10 VU | Evidencia histórica SCRUM-92/SCRUM-95 enlazada arriba |
| Estrés | C-STR-01 rampa/pico; C-STR-02 recuperación | `tests/perf/k6-api-stress.js`; sin resultado actual |
| Seguridad | C-SEC-01 autorización; C-SEC-06 inyección SQL | SCRUM-120, resultados y peticiones individuales enlazados arriba |
| UAT | UAT-01…UAT-05 o la muestra del 30–40% calculada desde Jira | Requiere participantes y aceptación humana |

## Registro Jira y pendientes de entrega

No hubo conexión Atlassian/Jira disponible durante esta sesión, por tanto no se pudieron leer SCRUM-122 ni los casos asociados, actualizar estados o adjuntar los archivos. Los enlaces de repositorio y colecciones arriba son rastreables, pero la vinculación y los estados de Jira siguen pendientes. La distribución total de casos, la proporción UAT y los estados Jira no se pueden afirmar sin consultar Jira.

Para cerrar SCRUM-122 en Jira: vincular el repositorio y las colecciones, adjuntar estos informes y resultados, asociar los casos de cada estrategia, actualizar los casos automatizados con el resultado real (Pass/Fail/Executed), adjuntar evidencia por caso, ejecutar y obtener firma UAT, calcular la muestra sobre el inventario completo y repetir carga/estrés con `k6` disponible y el entorno objetivo aprobado.

## Reproducción local

Desde `Adoplant/`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --html=reports/kevin/scrum122/unitarias_api_e2e.html --self-contained-html --junitxml=reports/kevin/scrum122/resultados-python.xml
node --test tests/*.test.cjs
k6 run -e BASE_URL=http://127.0.0.1:8000 tests/perf/k6-api-baseline.js
k6 run -e BASE_URL=http://127.0.0.1:8000 tests/perf/k6-api-load.js
k6 run -e BASE_URL=http://127.0.0.1:8000 tests/perf/k6-api-stress.js
```
