# SCRUM-6 — Solicitudes de adopción

Implementación local en `feature/SCRUM-6-envio-solicitudes`, basada en `origin/Develop`.
No se crearon tablas ni estados nuevos. No se ha publicado la rama ni modificado Jira.

## Organización del trabajo

| Subtarea | Implementación |
|---|---|
| Modelo y esquemas (SCRUM-44) | SolicitudAdopcion, SolicitudCrear, SolicitudMensaje y SolicitudRespuesta |
| Envío (SCRUM-45) | POST /api/solicitudes y notificación interna al donante |
| Consultas | GET /api/solicitudes y GET /api/solicitudes/{id} |
| Corrección | PATCH /api/solicitudes/{id} |
| Retiro | DELETE /api/solicitudes/{id} |
| Pruebas y documentación | Pruebas automáticas y colección de Postman organizada por función |

Las notificaciones se guardan en PostgreSQL; no se envía correo ni push. Se reutiliza
la autenticación de SCRUM-1. El modelo parcial Planta solo se utiliza para consultar
y bloquear la tabla existente: no utilizar create_all ni insertar plantas mediante él.
Coordinar el modelo completo con SCRUM-5 y el servicio de notificaciones con SCRUM-14.

## Contrato de los endpoints

Todas las rutas requieren Authorization: Bearer con un token de un usuario activo.
Sin token válido devuelven 401; una cuenta bloqueada recibe 403.

### POST /api/solicitudes

Body de ejemplo (sustituir el ID por una planta real):

```json
{"id_planta": 123, "mensaje": "Tengo espacio y tiempo para cuidarla."}
```

Devuelve 201 con id_solicitud, id_planta, id_adoptante, mensaje, estado y fecha_solicitud.
La solicitud queda PENDIENTE y la planta permanece DISPONIBLE. Requiere planta ajena,
visible y no eliminada. Guarda notificación y solicitud juntas. Rechaza duplicados
PENDIENTES o ACEPTADOS (409), planta propia (403), no disponible (409), inexistente,
oculta o eliminada (404), mensaje vacío o mayor de 500 caracteres (422).

### GET /api/solicitudes

Devuelve 200 con una lista JSON (vacía si no hay coincidencias).

- tipo=enviadas (predeterminado): solo solicitudes del usuario.
- tipo=recibidas: solo solicitudes para plantas cuyo dueño es el usuario.
- estado=PENDIENTE, ACEPTADA o RECHAZADA (opcional).
- id_planta: filtro opcional por planta.
- limite: 1–100, predeterminado 20.
- offset: desde 0, predeterminado 0.

Ejemplo: `/api/solicitudes?tipo=recibidas&estado=PENDIENTE&limite=20&offset=0`.
Orden: fecha descendente y, en empates, ID descendente. No se admiten filtros para
suplantar otro usuario. No se exponen correos, contraseñas ni perfiles privados.

### GET /api/solicitudes/{id}

Devuelve 200 con los mismos campos de la creación. Solo pueden consultar el
adoptante o el dueño de la planta. Una solicitud inexistente o ajena devuelve 404.

### PATCH /api/solicitudes/{id}

```json
{"mensaje": "Ahora tengo más espacio para cuidarla."}
```

Devuelve 200 con la solicitud actualizada. Solo el adoptante puede corregir una
solicitud PENDIENTE cuya planta siga DISPONIBLE y sin adopción asociada. Conserva
planta, autor, fecha y estado. Rechaza campos adicionales, mensaje vacío o superior
a 500 caracteres (422), solicitud ajena/inexistente (404) y estados incompatibles (409).

### DELETE /api/solicitudes/{id}

Sin Body. Devuelve 204 sin contenido. Solo el adoptante puede retirar su solicitud
PENDIENTE y sin adopción asociada. Elimina únicamente esa solicitud; conserva sus
notificaciones, deja id_solicitud en null y actualiza el mensaje para indicar el
retiro. No crea un estado CANCELADA. No cambia la planta ni elimina una adopción.
Una solicitud ACEPTADA/RECHAZADA devuelve 409; ajena o inexistente, 404. Repetir
el retiro devuelve 404. Una solicitud pendiente puede retirarse aunque la planta
haya dejado de estar disponible.

## Transacciones y concurrencia

Crear, corregir y retirar bloquean primero la planta. Edición y retiro bloquean
después la solicitud y releen su estado. Los cambios se confirman juntos; ante un
fallo se revierten. Errores de persistencia en esas operaciones devuelven 503.
Las futuras rutas de aceptación y moderación deben usar el mismo orden de bloqueo
(planta, solicitud) para coordinarse y evitar interbloqueos. La aceptación del donante
pertenece a otra historia. Las pruebas actuales no simulan dos conexiones concurrentes.

## Postman: importar y ejecutar

1. Mantener la API ejecutándose en http://127.0.0.1:8000.
2. Importar `postman/SCRUM-6.postman_collection.json`. Su nombre nuevo es
   **SCRUM-6 - Gestión de solicitudes**. Usar esta colección en lugar de la versión anterior.
3. Reutilizar el entorno **AdopPlant SCRUM-6 local** que ya se importó. Si falta,
   importar `postman/SCRUM-6.local.postman_environment.json`.
4. La carpeta **01 Enviar solicitud y validaciones** conserva las 16 pruebas previas.
5. Ejecutar la carpeta **02 Consultar, corregir y retirar** en orden, una iteración.
   Tiene 21 peticiones: login, preparar/reutilizar solicitud, consultas, edición,
   permisos del donante/terceros y retiro. Los logins guardan el token automáticamente.
   La consulta inicial guarda solicitud_id sin copiarlo a mano.
6. Revisar Test Results. Los casos 401/403/404/409/422 son éxitos cuando ese es el
   código esperado. El DELETE correcto devuelve 204 con Body vacío.

La carpeta 02 utiliza solo las cuentas y la planta disponible del entorno de
pruebas. Crea una solicitud o reutiliza la pendiente del adoptante y la retira al
final. Se puede repetir mientras la planta siga disponible. No ejecutar esa carpeta
con credenciales o IDs reales ajenos a las pruebas. Las notificaciones se conservan.
En la carpeta 01, repetir creaciones sin retiro previo devuelve 409; es correcto.

Si aún no existen datos de ejemplo:

```powershell
.\.venv\Scripts\python.exe -m scripts.preparar_postman
```

El script crea cuatro usuarios, una categoría y cinco plantas de prueba. Si el
entorno local ya existe, se detiene sin insertar datos. El archivo local contiene
credenciales de prueba y está excluido de Git. No compartirlo públicamente.

## Pruebas automáticas

```powershell
.\.venv\Scripts\python.exe -m pytest -q
$env:SCRUM6_TEST_DB = '1'
.\.venv\Scripts\python.exe -m pytest -q
Remove-Item Env:SCRUM6_TEST_DB
```

La integración usa PostgreSQL y revierte los datos insertados en cada prueba.
Las secuencias pueden avanzar. Comprueba privacidad, filtros, paginación, campos
protegidos, conservación de fecha/autor, estados decididos, adopción asociada,
retiro, notificaciones conservadas y reversión ante fallos.

Resultado: 120 pruebas y 6 subpruebas correctas con integración habilitada.
La ejecución en la aplicación Postman y las capturas para la entrega se realizan
por separado; no se consideran completadas por las pruebas automáticas.
