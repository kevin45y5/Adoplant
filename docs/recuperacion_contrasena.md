# SCRUM-2 — Recuperación de contraseña

La API usa la tabla existente `recuperacion_contrasena`; este cambio no requiere migración. Las dos rutas se comparten entre la aplicación móvil y el portal web.

## Configurar el envío por Mailjet

1. Crear una cuenta gratuita en Mailjet y validar un correo remitente en **Account Settings → Senders & Domains**. La dirección usada para registrarse suele quedar validada automáticamente.
2. En **Account Settings → API Keys**, consultar la clave pública y generar/guardar la clave secreta. No compartirlas por chat ni guardarlas en Git.
3. En el servicio web de Render, abrir **Environment** y agregar `MAILJET_API_KEY`, `MAILJET_SECRET_KEY` y `MAILJET_SENDER_EMAIL` (el correo verificado). Guardar y esperar el nuevo despliegue.
4. Para probar localmente, agregar las mismas variables al `.env` personal. No subir ese archivo.

El servicio de Render Free no permite SMTP tradicional; se usa la API HTTPS de Mailjet. Brevo permanece como alternativa con `BREVO_API_KEY` y `BREVO_SENDER_EMAIL`. Si ambos están configurados, Mailjet tiene prioridad. Si falta la configuración, la solicitud devuelve `503`. Si el proveedor falla, la API no guarda un código utilizable y registra el error del lado del servidor.

## Flujo en Postman

1. `POST {{baseUrl}}/api/auth/recuperacion` con `{"correo":"correo-registrado@example.com"}`. Respuesta `202` genérica; un correo desconocido también recibe `202`.
2. Leer el código de ocho dígitos recibido en el correo de prueba. No guardarlo como ejemplo público de Postman.
3. `POST {{baseUrl}}/api/auth/restablecer-contrasena` con `{"correo":"correo-registrado@example.com","codigo":"CODIGO_RECIBIDO","nueva_contrasena":"NuevaClave123","confirmar_contrasena":"NuevaClave123"}`. Respuesta `200`.
4. Comprobar que el código no puede reutilizarse (`400`), la contraseña anterior ya no inicia sesión (`401`) y la nueva sí (`200`). Un código vencido o cinco intentos fallidos también dan `400`.

El código caduca en 15 minutos; un nuevo pedido se limita a uno por minuto por cuenta. Solo se almacena el hash del código. Las contraseñas se validan con la misma política del registro y nunca se devuelven en las respuestas.

## Interfaz web de SCRUM-2

La rama `scrum-2-recuperacion-web` incorpora los archivos `views` de
`feature/bienvenida` (6010267, trabajo de Fabiola), conservando el backend actual.
No integra los cambios antiguos de `app/main.py` de esa rama.

Abrir `/views/index.html` para login o `/views/recuperar.html` directamente.
FastAPI sirve las páginas y `/api` en el mismo origen, tanto localmente como
en Render: no abrir los HTML con `file://` ni con Live Server en otro puerto.
El inicio `/` conserva la respuesta JSON de salud de la API.

La recuperación solicita el correo, luego el código y ambas contraseñas en un
formulario. La validación del código ocurre al guardar. No existe una llamada
intermedia a un endpoint de verificación. No se guardan códigos o contraseñas
en el navegador. Se puede reenviar el código tras un minuto o cambiar de correo.

Pruebas de interfaz lógica: `node --test tests/recuperacion_web.test.cjs`.
Prueba de rutas estáticas: `python -m pytest tests/test_web_recuperacion.py`.
Pendiente la prueba manual con correo real tras integrar y desplegar esta rama.

## Pruebas del backend

En una base PostgreSQL **local** con el esquema ya instalado, ejecutar `SCRUM2_TEST_DB=1` y `pytest -q tests/test_recuperacion_postgres.py`. Las pruebas interceptan el envío de correo y revierten sus datos de prueba; no usan Mailjet ni la base de Render.
