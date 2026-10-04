# Mensajes y ubicación de entrega

La web abre `/views/mensajes.html`. Desde una solicitud aceptada, el botón de coordinar entrega abre `?planta=ID` y crea o recupera el chat usando `POST /api/chats`. El servidor exige una adopción asociada y permite únicamente al donante y al adoptante acceder a los mensajes.

La web envía puntos y actualizaciones como mensajes nativos `UBICACION`, con `latitud`, `longitud` y `descripcion`, compatibles con la tarjeta de ubicación de la app móvil. La sesión de seguimiento se conserva en el contenido con el prefijo `[PlantHaven:ubicacion:1]`. La API valida esos datos, devuelve `ubicacion` para el seguimiento web y `punto` para la app móvil, y presenta un texto legible en lugar del JSON interno. Los mensajes antiguos se muestran como puntos de solo lectura. Al corregir un punto desde la app móvil, la web usa las coordenadas corregidas. No requiere tablas nuevas.

Hay que desplegar tanto API como web y recargar el chat en ambas cuentas. Los scripts tienen versiones para renovar la caché. La app móvil necesita su propia implementación para mover un marcador en vivo; este proyecto contiene la API y la web, no el código móvil.

Compartir requiere permiso de geolocalización, HTTPS (o localhost), obtener una vista previa y confirmar el envío. Un punto fijo no inicia seguimiento. La opción en vivo dura 15 minutos, envía aproximadamente cada 15 segundos y consulta mensajes cada 5 segundos sin reconstruir el chat ni recargar mapas cuya posición no cambió. El botón de detener cancela el GPS y envía un aviso. Al cerrar o abandonar la página se cancela el GPS; si no llega el aviso, el receptor indica que el último punto está desactualizado tras 45 segundos sin una nueva lectura. No se garantiza seguimiento con la pestaña suspendida o el teléfono bloqueado.

Los puntos enviados permanecen en el historial privado del chat; detener no borra el historial. El mapa se carga mediante OpenStreetMap y el enlace de indicaciones abre Google Maps. No hay claves de mapas en el código.

Validación: `node --test tests/chat_location_web.test.cjs tests/solicitudes_web.test.cjs` y `python -m pytest tests/test_chat.py -q`. Para comprobar dos dispositivos, aceptar una solicitud, abrir el chat en las cuentas de donante y adoptante, enviar texto y un punto, activar seguimiento y detenerlo. La entrega GPS entre dispositivos reales requiere esta verificación manual sobre el sitio desplegado.
