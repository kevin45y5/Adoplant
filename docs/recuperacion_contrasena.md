# SCRUM-2 — Recuperación de contraseña

La API usa la tabla existente `recuperacion_contrasena`; este cambio no requiere migración. Las dos rutas se comparten entre la aplicación móvil y el portal web.

## Configurar el envío por Brevo

1. Crear una cuenta en Brevo y verificar un correo remitente en **Senders & IPs**.
2. Generar una clave **API v3** en Brevo. No compartirla por chat ni guardarla en Git.
3. En el servicio web de Render, abrir **Environment** y agregar `BREVO_API_KEY` y `BREVO_SENDER_EMAIL` (el correo verificado). Guardar y esperar el nuevo despliegue.
4. Para probar localmente, agregar las mismas variables al `.env` personal. No subir ese archivo.

El servicio de Render Free no permite SMTP tradicional; se usa la API HTTPS de Brevo. Si falta la configuración, la solicitud devuelve `503`. Si Brevo falla, la API no guarda un código utilizable y registra el error del lado del servidor.

## Flujo en Postman

1. `POST {{baseUrl}}/api/auth/recuperacion` con `{"correo":"correo-registrado@example.com"}`. Respuesta `202` genérica; un correo desconocido también recibe `202`.
2. Leer el código de ocho dígitos recibido en el correo de prueba. No guardarlo como ejemplo público de Postman.
3. `POST {{baseUrl}}/api/auth/restablecer-contrasena` con `{"correo":"correo-registrado@example.com","codigo":"CODIGO_RECIBIDO","nueva_contrasena":"NuevaClave123","confirmar_contrasena":"NuevaClave123"}`. Respuesta `200`.
4. Comprobar que el código no puede reutilizarse (`400`), la contraseña anterior ya no inicia sesión (`401`) y la nueva sí (`200`). Un código vencido o cinco intentos fallidos también dan `400`.

El código caduca en 15 minutos; un nuevo pedido se limita a uno por minuto por cuenta. Solo se almacena el hash del código. Las contraseñas se validan con la misma política del registro y nunca se devuelven en las respuestas.

## Prueba automática

En una base PostgreSQL **local** con el esquema ya instalado, ejecutar `SCRUM2_TEST_DB=1` y `pytest -q tests/test_recuperacion_postgres.py`. Las pruebas interceptan el envío de correo y revierten sus datos de prueba; no usan Brevo ni la base de Render.
