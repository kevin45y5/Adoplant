# SCRUM-7 — Gestión de solicitudes recibidas

## Contrato compartido por web y Flutter

- GET `/api/solicitudes?tipo=recibidas`: solicitudes de las plantas del donante
  autenticado; filtros `estado`, `id_planta`, `limite` (1–100), `offset`.
  Incluye `nombre_planta` y `nombre_adoptante`, sin correo ni teléfono.
- GET `/api/solicitudes/{id}`: detalle privado para donante o adoptante.
- PATCH `/api/solicitudes/{id}` con `{"estado":"ACEPTADA"}` o
  `{"estado":"RECHAZADA"}`: decisión exclusiva del donante.
- El PATCH con `{"mensaje":"Texto corregido"}` sigue siendo exclusivo del
  adoptante. No se pueden mezclar mensaje y estado en una petición.

Aceptar una solicitud PENDIENTE de una planta DISPONIBLE, visible y no retirada
confirma en una transacción: elegida ACEPTADA, otras pendientes RECHAZADAS,
planta SOLICITADA, adopción EN_PROCESO y notificación al elegido. Rechazar afecta
solo a la solicitud elegida. Una operación repetida o estado incompatible responde
409; identificador ajeno/inexistente, 404; sesión ausente, 401; cuenta bloqueada, 403.

Se bloquea primero la planta y luego la solicitud, siguiendo el mismo orden de
las operaciones de publicación/retiro. Se conserva el esquema y no hay migración.
El chat móvil continúa pendiente de integración; esta entrega no lo declara terminado.

## Validación

Pruebas con PostgreSQL local: `SCRUM6_TEST_DB=1` y ejecutar pytest. Los casos
transaccionales revierten sus datos. Las carreras crean registros propios locales
y los eliminan al finalizar; jamás se ejecutan contra Render.

Se comprueban aceptación, rechazo individual, permisos, validación, notificación,
fallo antes del commit, dos aceptaciones simultáneas, aceptación contra retiro y
aceptación contra edición. Después de aceptar, editar/retirar la planta se deniega.

Colección compartida: `postman/SCRUM-7.postman_collection.json`. Tokens vacíos;
usar cuentas propias de prueba. No publicar tokens ni códigos de recuperación.

## Prueba móvil pendiente tras desplegar

1. Instalar la APK actualizada. Donante: Mis publicaciones → icono de bandeja
   «Solicitudes recibidas». Debe ver interesado, planta, mensaje, fecha y estado.
2. Para probar rechazo individual, enviar solicitudes desde dos cuentas distintas
   para la misma planta. Rechazar una y comprobar que la otra continúa PENDIENTE.
3. Para probar aceptación y rechazo automático, usar otra planta con dos solicitudes
   PENDIENTES; aceptar una. La otra debe quedar RECHAZADA.
4. En ambas cuentas adoptantes, abrir Mis solicitudes para recargar el resultado.
5. Volver a Mis publicaciones del donante: planta SOLICITADA, sin edición/retiro.
   El catálogo deja de ofrecerla como disponible.

Las pruebas en teléfonos siguen pendientes hasta confirmación del equipo.
