# Reporte de ejecución — Kevin Meza

Fecha: 30 de octubre de 2026 (America/El_Salvador).

## Alcance y resultado

| Jira | Resultado local | Cobertura del módulo | Herramienta |
|---|---|---|---|
| [SCRUM-111](https://jdavidg555-1788882610120.atlassian.net/browse/SCRUM-111) | 10 casos PASS | `app/security.py`: 100 % | pytest, pytest-cov, PyJWT, pwdlib |
| [SCRUM-112](https://jdavidg555-1788882610120.atlassian.net/browse/SCRUM-112) | 8 casos PASS | `app/services/notificaciones.py`: 100 % | pytest, unittest.mock; SQLite en memoria para C-112-07 |
| [SCRUM-120](https://jdavidg555-1788882610120.atlassian.net/browse/SCRUM-120) | 7 escenarios Python PASS | No aplica | pytest, FastAPI TestClient, PostgreSQL local |

Ejecución dirigida SCRUM-111/112: **18 pruebas PASS, 5 subcasos PASS**. SCRUM-120 Python: **7 escenarios PASS**. La última regresión está en `regresion.txt` y `regresion.xml`.

Los resultados son locales. No se han modificado estados, comentarios ni adjuntos en Jira. El usuario limitó el alcance a SCRUM-111, SCRUM-112 y la parte Python de SCRUM-120. SCRUM-119 queda fuera. C-SEC-04 se adaptó a `/api/admin/usuarios`; no acredita `/api/metricas` de C#. Este documento no acredita la entrega completa del equipo ni el alcance original de ambas APIs de SCRUM-120.

## Evidencias

- [Reporte HTML de ejecución](ejecucion.html).
- [Salida de consola](ejecucion.txt).
- [JUnit XML con nombres y resultados](resultados.xml).
- [Reporte HTML de cobertura](cobertura/index.html) y [datos JSON](cobertura.json).
- [Regresión completa](regresion.txt) y [JUnit de regresión](regresion.xml).
- [Fallo inicial reproducido](defecto_hash_antes.txt) y [JUnit del fallo](defecto_hash_antes.xml).
- [Reporte de seguridad SCRUM-120 Python](scrum120/README.md), con resultados, peticiones y límites.
- [Colección Postman SCRUM-120 Python](../../postman/SCRUM-120_python.postman_collection.json), preparada para reproducción manual; no ejecutada con Postman.

Pendiente para la entrega: capturas de los reportes, vinculación de evidencias/ejecuciones en Jira.

## Trazabilidad de casos

Cada función de prueba comienza con el identificador Jira normalizado, por ejemplo `test_c111_01_...` corresponde a C-111-01. Los nombres completos aparecen en el XML y el HTML.

| Caso | Comprobación | Resultado |
|---|---|---|
| C-111-01 | Hash con sal aleatoria y sin contraseña en claro | PASS |
| C-111-02 | Contraseña correcta | PASS |
| C-111-03 | Contraseña incorrecta | PASS |
| C-111-04 | Hash vacío y corrupto rechazados sin excepción | PASS tras corrección |
| C-111-05 | Claims, algoritmo y duración del JWT | PASS |
| C-111-06 | Tokens consecutivos y usuarios distintos | PASS |
| C-111-07 | Firma correcta y clave incorrecta | PASS |
| C-111-08 | Decodificación en un proceso Python independiente | PASS |
| C-111-09 | Rechazo de clave JWT corta | PASS |
| C-111-10 | Rechazo de duración cero o negativa | PASS |
| C-112-01 | Tipo, texto e identificadores de solicitud | PASS |
| C-112-02 | Servicio sin commit ni rollback | PASS |
| C-112-03 | Decisión aceptada | PASS |
| C-112-04 | Decisión rechazada | PASS |
| C-112-05 | Otro estado tratado como rechazo | PASS |
| C-112-06 | Destinatario adoptante | PASS |
| C-112-07 | Flush, consulta y rollback en SQLite efímera | PASS |
| C-112-08 | Dos notificaciones independientes | PASS |

## Defecto corregido

C-111-04 falló inicialmente: `pwdlib` lanzaba `UnknownHashError` ante un hash vacío o desconocido. `verificar_contrasena` captura ahora esa excepción específica y devuelve `False`. Se conservan las comprobaciones de contraseña válida e inválida. No se ocultan otras excepciones inesperadas.

## Límites e interpretación

- C-111-08 valida otro proceso Python con una clave ficticia común; no demuestra interoperabilidad con C# ni utiliza el secreto real de la aplicación.
- Los tiempos JWT son segundos: la diferencia `exp - iat` debe ser los minutos configurados multiplicados por 60.
- C-112-07 es una comprobación de componente complementaria usando SQLite en memoria, para demostrar un flush real. Los otros siete casos usan sesión simulada. No se conecta a PostgreSQL en esta suite dirigida. SQLite no acredita restricciones específicas de PostgreSQL.
- Un 100 % de cobertura en estos dos archivos no implica cobertura total del sistema ni ausencia de vulnerabilidades.

## Código y reproducción

Repositorio configurado: [kevin45y5/Adoplant](https://github.com/kevin45y5/Adoplant).
Commit base: `8297a2ce3c05f1d865171369efa6befebf43f87f`.
El código y las evidencias se incluyen en el mismo commit que este reporte. Consultar el historial de este archivo en GitHub para identificar la revisión publicada.

- [Pruebas de seguridad](../../tests/test_security.py).
- [Pruebas de notificaciones](../../tests/test_notificaciones.py).
- [Módulo corregido](../../app/security.py).

Desde la carpeta `Adoplant`, sin los indicadores de integración activados:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_security.py tests/test_notificaciones.py -v --cov=app.security --cov=app.services.notificaciones --cov-branch --cov-fail-under=90 --cov-report=term-missing --cov-report=html:reports/kevin/cobertura --cov-report=json:reports/kevin/cobertura.json --html=reports/kevin/ejecucion.html --self-contained-html --junitxml=reports/kevin/resultados.xml
```

Las pruebas dirigidas utilizan contraseñas y claves ficticias. La comprobación del mínimo de cobertura aplica al total; el reporte también confirma 100 % en cada archivo individual.
