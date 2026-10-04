# SCRUM-8 — Chat compartido por web y móvil

El chat usa PostgreSQL y las rutas existentes de la API. No se modifica el esquema.
Solo el donante y el adoptante de una solicitud ACEPTADA con adopción asociada
pueden abrirlo. Las cuentas bloqueadas y los tokens vencidos no tienen acceso.

## Endpoints y ejemplos para Postman

Todas las peticiones requieren `Authorization: Bearer {{token_usuario}}`.

- `POST {{baseUrl}}/api/chats`, JSON `{"id_planta": 1}`: 201 al crear; 200 al
  reabrir el mismo chat. Rechaza con 403 si falta aceptación/adopción o es un tercero.
  Bloquea la fila de planta para evitar duplicados al abrir desde ambos teléfonos.
- `GET {{baseUrl}}/api/chats`: lista solo chats propios, con nombre de planta y
  nombre del otro participante; no devuelve correos, teléfonos ni tokens.
- `POST {{baseUrl}}/api/chats/{{id_chat}}/mensajes`, JSON `{"contenido":"Hola"}`:
  201, remitente tomado del token y fecha del servidor. Texto de 1 a 2000 caracteres,
  sin mensajes de espacios. No permite editar/borrar mensajes en general.
- `GET {{baseUrl}}/api/chats/{{id_chat}}/mensajes?pagina=1&tamano_pagina=20`:
  historial cronológico y paginado compatible con los clientes anteriores.
- Para sincronización incremental: agregar `despues_de=0`, guardar el último
  `id_mensaje` recibido y usarlo como `despues_de` en la siguiente lectura.
  Máximo 100 por respuesta; continuar mientras llegue un lote completo.
  `total` cuenta los mensajes que cumplen el filtro. Este modo ordena por ID;
  los envíos del chat se serializan antes de asignarlo. No adelantar el cursor
  de lectura usando la respuesta de un envío propio: podría omitir mensajes ajenos.

## Validación

`SCRUM6_TEST_DB=1 python -m pytest tests/test_chat.py tests/test_chat_integracion.py -q`
usa PostgreSQL local con rollback, sin tocar los datos de Render. Comprueba
aceptación real, reapertura, permisos, espacios, longitud, ambos remitentes,
paginación, lectura incremental, bloqueo y conservación tras completar adopción.

En móvil, el chat consulta cambios cada tres segundos mientras está abierto;
se detiene al salir o poner la aplicación en segundo plano. Los mensajes permanecen
en el servidor al reinstalar la APK. Los fallos de conexión no borran el historial
visible ni el texto que no pudo enviarse. No se reintentan envíos automáticamente.

## Prueba manual pendiente

1. Desplegar este backend y generar la APK actualizada.
2. Dos cuentas: aceptar una solicitud y abrir chat desde ambas bandejas.
3. Enviar en ambas direcciones y comprobar recepción automática sin volver atrás.
4. Cerrar/reabrir la app: el historial debe continuar; Mis conversaciones debe listarlo.
5. Desconectar un teléfono, enviar desde el otro y reconectar: recibir los pendientes.
6. Una solicitud pendiente/rechazada y una tercera cuenta no deben acceder al chat.
7. Revisar por separado el punto de encuentro de SCRUM-9. Esta integración de texto
   no acredita todavía el criterio de compartir ubicación privada.

No marcar SCRUM-8 completo solo por superar las pruebas automatizadas.
