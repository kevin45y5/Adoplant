# Publicación de AdopPlant en Render

Estado del 28-09-2026: API publicada en https://adopplant-api.onrender.com.
Swagger disponible en /docs. Conexión PostgreSQL verificada.

## Primer paso: cuenta

Crear una cuenta en https://dashboard.render.com/register usando GitHub o correo.
No contratar un plan ni crear recursos de pago como parte de este primer paso.
El repositorio pertenece a `kevin45y5`; al vincularlo se debe comprobar que la cuenta
usada tenga permiso suficiente. Si no aparece, coordinar el acceso con su propietario.

## Configuración del servicio

| Campo | Valor |
| --- | --- |
| Tipo | Web Service |
| Repositorio | kevin45y5/Adoplant |
| Rama | Main |
| Runtime | Python 3 |
| Root Directory | Vacío: app y requirements.txt están en la raíz de la repo |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/` |

El archivo `.python-version` selecciona Python 3.14, la misma serie utilizada localmente.
En Render se configuró PYTHON_VERSION=3.14.2, que tiene precedencia sobre el archivo.
No usar --reload en el servidor.

## Procedimiento para una instalación nueva

- Seleccionar PostgreSQL remoto y revisar su versión antes de importar el esquema.
  El script inicial procede de PostgreSQL 18 y contiene comandos propios de psql.
- Importar `sql/base_inicial.sql` solo en una base NUEVA vacía, nunca sobre la local
  existente ni automáticamente en cada arranque.
- Ejecutar la revisión inicial de Alembic contra la base remota ya preparada.
- Configurar DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, JWT_SECRET_KEY y
  JWT_ACCESS_TOKEN_MINUTES en el servicio. Usar una clave JWT nueva para ese entorno.
- Configurar PGSSLMODE=require para exigir TLS.
- Preparar cuentas de prueba y un administrador mediante un procedimiento controlado;
  importar solo estructura no copia a Ana ni le asigna permisos automáticamente.
- Probar /docs, conexión, registro, login, perfil y administración en la URL pública.
- Actualizar baseUrl en Postman y publicar su documentación.

## Limitaciones relevantes antes de elegir recursos

- La base PostgreSQL gratuita de Render caduca a los 30 días. Debe seguir accesible
  durante la evaluación; confirmar la fecha o elegir otra alternativa antes de crearla.
- El servicio web gratuito duerme tras 15 minutos sin tráfico; el primer acceso
  posterior puede tardar aproximadamente un minuto.
- Las fotografías en el disco local del servicio no son persistentes. Al integrar
  el módulo de fotografías se debe usar almacenamiento duradero compatible.
- El servicio gratuito bloquea los puertos SMTP 25, 465 y 587. Considerarlo al
  implementar SCRUM-2; un proveedor de correo con API HTTPS puede ser necesario.

Fuentes oficiales consultadas:

- https://render.com/docs/deploy-fastapi
- https://render.com/docs/python-version
- https://render.com/docs/free

## Actualización del despliegue existente

El servicio se conectó mediante la URL pública del repositorio, sin integración de GitHub.
Después de subir y verificar Main, usar Manual Deploy > Deploy latest commit en Render.
No reimportar el esquema inicial: la base ya tiene las 14 tablas de negocio y se ejecutó
la revisión Alembic 0001_base_existente. Utilizar Alembic para futuras migraciones.
Los secretos se configuran exclusivamente en Render; no se incluyen en este documento.

## Verificación del código antes de cambiar la contraseña

La web de recuperación requiere `POST /api/auth/verificar-codigo`, con `correo`
y `codigo` (ocho dígitos). Solo una respuesta exitosa permite mostrar el formulario
de nueva contraseña. El backend comprueba el correo, el código más reciente,
su vencimiento, su uso y el límite compartido de cinco intentos. Al guardar la
contraseña, `/api/auth/restablecer-contrasena` vuelve a comprobar el código.

Después de actualizar Main, desplegar el último commit en Render y comprobar que
`/docs` incluye `/api/auth/verificar-codigo`. No se necesita una migración de base
de datos ni cambiar variables de entorno. Recargar la web local después del
despliegue: ya utiliza la API de Render. Hasta desplegar el backend nuevo, la
verificación queda bloqueada; no existe una alternativa que acepte cualquier código.

Validación local: `node --test tests/*.cjs` y las pruebas pytest. Para incluir las
pruebas PostgreSQL, establecer `SCRUM2_TEST_DB=1` y `SCRUM6_TEST_DB=1`; los datos de
prueba se revierten y el envío de correo de recuperación se simula.
