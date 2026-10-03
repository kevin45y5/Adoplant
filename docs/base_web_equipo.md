# Base web compartida

La interfaz se sirve desde el mismo servicio de Render que la API:

- Entrada: https://adopplant-api.onrender.com/views/index.html
- Registro: https://adopplant-api.onrender.com/views/register.html
- Recuperación: https://adopplant-api.onrender.com/views/recuperar.html
- Inicio protegido: https://adopplant-api.onrender.com/views/inicio.html

Estas rutas requieren desplegar en Render el commit que contiene `views`.
La raíz `/` sigue mostrando la salud de la API y `/docs` conserva Swagger.
`views/config.js` fija la API en `https://adopplant-api.onrender.com/api` para
registro, login, recuperación e inicio, incluso al trabajar en la computadora.
La API permite CORS desde HTTP localhost y 127.0.0.1 con puerto; conserva JWT.
Este cambio de CORS también debe desplegarse en Render antes de probar la web local.

Para desarrollar pueden mantener `http://127.0.0.1:8000/views/index.html` o servir
la carpeta raíz del repositorio con Live Server (no solamente `views`). Las rutas
de recursos y páginas empiezan por `/views/`. No abrir con `file://`.
Los registros, cambios de contraseña y demás operaciones afectan a los datos reales
de Render. No se necesitan claves de Mailjet ni una base de datos local para servir
los archivos estáticos. Los nuevos módulos deben reutilizar `window.ADOPPLANT_API_URL`.

## Comportamiento

El registro reutiliza la API existente. El login permite correo o teléfono completo
tal como se registró y abre Inicio. Inicio consulta `/api/usuarios/me`; una sesión
vencida o bloqueada vuelve al login. Cerrar sesión elimina el token del navegador.
El token se conserva en `sessionStorage`, por pestaña, sin almacenar contraseñas.
La portada es una base para continuar; no incluye todavía catálogo ni otras funciones.

La recuperación usa exactamente las dos rutas ya utilizadas por Flutter: solicita
un código y luego envía código y nueva contraseña juntos. No hay un endpoint
separado para verificar códigos. Mailjet y sus claves permanecen en el backend.
Los compañeros no necesitan configurar claves de correo en sus computadoras.

## Traer la base y continuar

Guardar el trabajo pendiente en la rama propia antes de cambiar de rama.
No descartar archivos ni usar `reset --hard` para actualizar.

```powershell
git fetch origin
git switch Develop
git pull --ff-only origin Develop
git switch -c SCRUM-XX-descripcion
```

Si ya existe una rama de trabajo con cambios, integrar `origin/Develop` en ella y
resolver cualquier conflicto conservando tanto sus cambios como la integración
con `/api`. Revisar especialmente `views/main.js` y `app/main.py`.
No reemplazar el backend por una copia antigua de la rama `feature/bienvenida`.
El diseño inicial de login y registro proviene de esa rama (Fabiola, 6010267).

Publicar cambios revisados en Main y desplegar el último commit de Main en Render.
Los cambios locales no aparecen en la web publicada hasta ese despliegue.

## Comprobación manual después del despliegue

1. Registrar una cuenta de prueba con correo accesible; repetir correo y comprobar el error.
2. Iniciar sesión y verificar que Inicio muestra los datos de esa cuenta.
3. Cerrar sesión; entrar directamente a Inicio debe devolver al login.
4. Recuperar contraseña con el correo registrado. Probar primero un código incorrecto,
   después el recibido con una contraseña nueva. La anterior debe fallar y la nueva funcionar.
5. Probar login con el teléfono completo registrado.

Pruebas automatizadas: `node --test tests/recuperacion_web.test.cjs tests/sesion_web.test.cjs`
y `python -m pytest -q tests/test_web_recuperacion.py tests/test_autenticacion.py tests/test_registro_validacion.py tests/test_rutas.py`.
