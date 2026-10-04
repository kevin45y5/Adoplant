# SCRUM-9 — Puntos de encuentro privados

Implementación sobre la tabla existente `public.punto_encuentro`, relacionada
con `mensaje`. No requiere migración ni cambios en el diagrama.

## Contrato para web, móvil y Postman

Todas las peticiones requieren un token de usuario activo. Solo los participantes
del chat pueden consultar. Para crear/corregir/retirar debe existir una adopción
EN_PROCESO; corregir y retirar son exclusivos del autor del punto.

1. `POST /api/chats/{id_chat}/mensajes` crea mensaje y punto en una transacción:

   ```json
   {"tipo":"UBICACION","latitud":13.7167,"longitud":-89.7167,"descripcion":"Entrada del parque"}
   ```

   Responde 201 con el mensaje habitual más `punto`: `id_punto`, `id_mensaje`,
   `latitud`, `longitud`, `descripcion` y `puede_editar`. El contenido textual
   del mensaje es «Punto de encuentro»; las coordenadas solo están en el punto.
   Mensajes antiguos `{"contenido":"Hola"}` siguen siendo válidos como TEXTO.

2. `GET /api/chats/{id_chat}/puntos`: 200, lista completa de puntos vigentes del chat.
3. `GET /api/puntos-encuentro/{id_punto}`: 200, punto vigente privado por ID.
4. `PATCH /api/puntos-encuentro/{id_punto}`: 200; admite uno o varios campos:

   ```json
   {"latitud":13.717,"longitud":-89.716,"descripcion":"Entrada norte"}
   ```

   Conserva ID, remitente y fecha del mensaje. No permite coordenadas nulas.
   `descripcion: null` borra la descripción opcional.
5. `DELETE /api/puntos-encuentro/{id_punto}`: 204 sin cuerpo. Elimina el punto y
   convierte su mensaje a TEXTO: «Punto de encuentro retirado por el remitente».
   Consultar el punto retirado responde 404. No elimina el mensaje ni el chat.

Errores: 401 sin sesión válida; 403 cuenta bloqueada/tercero/no autor; 404 inexistente;
409 adopción completada o inexistente para escritura; 422 coordenadas fuera de
rangos (-90..90, -180..180), valores no finitos, campos inválidos o descripción >255.

## Sincronización y privacidad

GET de mensajes incluye el punto vigente. Como las correcciones no crean otro
mensaje, el cliente también consulta la lista de puntos para actualizar los que ya
mostró. Si un punto desaparece de esa lista autorizada, sustituye sus coordenadas
por el aviso de retiro. Un error de conexión no equivale a una lista vacía.

La app selecciona un marcador estático con OpenStreetMap; no solicita GPS ni envía
ubicación en tiempo real. «Cómo llegar» consulta el punto vigente por ID y abre
un mapa externo con ese destino. La app de mapas externa administra su propia ruta.

Las escrituras bloquean chat y adopción, en ese orden, y se confirman juntas.
SCRUM-16 debe conservar el control transaccional al completar la adopción.
Después de completarla se pueden consultar puntos conservados, pero no cambiarlos.

## Verificación

Pruebas automáticas locales con rollback:
`SCRUM6_TEST_DB=1 python -m pytest tests/test_chat.py tests/test_chat_integracion.py tests/test_puntos_encuentro.py -q`.

Prueba manual pendiente en dos teléfonos: crear punto, verlo en ambos, abrir
«Cómo llegar», corregirlo desde el autor, comprobar que cambia en el receptor,
retirarlo y comprobar el aviso en ambos. El receptor no debe tener botones de
corregir/retirar puntos ajenos. Cerrar y reabrir debe conservar el resultado.

Primero desplegar Main de la API; después instalar la APK nueva. No dar por cerrada
la prueba de mapa externo hasta realizarla en el teléfono.
