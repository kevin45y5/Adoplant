# Integración del avance grupal — 28-09-2026

Se integró el código recibido sin modificar el esquema ni los datos existentes.
Esto no declara completas las 17 historias ni todos los CRUD individuales.

## Procedencia

| Responsable | Fuente revisada | Integrado |
| --- | --- | --- |
| Krisler | Main, d879b46 | Autenticación, cuenta y administración de usuarios conservadas. |
| Kevin | Main, 6767687 | Solicitudes propias conservadas sin sustituir su implementación. |
| Fabiola | feature/SCRUM-5-publicacion-gestion-plantas-propias, 00a53e8 | Plantas, catálogo y registro de fotografías por URL. La versión más reciente reúne estos módulos. |
| Fabrizio/Edwin | feature/SCRUM-14-Notificaciones, 862a770; esquema válido de d7b274c | Consulta y lectura de notificaciones. |
| Manuel | SCRUM-17-moderacion-publicaciones-manuel, 30c10aa | Chat y moderación; esta rama incluye el trabajo de SCRUM-8. |
| Manuel | feature/SCRUM-19-atencion-reportes, bc7fb60 | Creación y administración de reportes. |

La rama feature/SCRUM-20-categorias-de-gestion (e571998) contiene reportes,
no endpoints de categorías. No se inventó ni se dio por terminado ese módulo.

## Ajustes necesarios para integrar

- Se conservan autenticación, validaciones de usuarios, conexión y router central de Main.
- Se recupera notificaciones sin los restos de conflictos que impedían importar su rama.
- Los modelos y esquemas adicionales comparten una sola Base y los módulos existentes.
- Planta usa la columna existente `estado`; `estado_planta` es un alias del modelo/API.
- Fotografía usa `id_foto` y `fecha_carga`, expuestos como `id_fotografia` y `fecha_subida`.
  No se crean `tipo` ni `es_principal`; el catálogo utiliza la primera foto por ID.
- Moderación registra el ID de la tabla administrador, no el ID del usuario,
  y conserva la restricción que impide marcar como visible una planta eliminada.
- Las nuevas rutas reutilizan los controles actuales de usuario activo y administrador.
- Se ajustaron validaciones básicas de plantas a las restricciones de la base existente.
- No se ejecutan los scripts de migración manual incluidos en la rama de plantas.

## Cobertura y límites del avance

Hay 35 operaciones de negocio y dos de diagnóstico en OpenAPI.

- Categorías no tiene rutas recibidas: publicar plantas requiere una categoría activa existente.
- No se recibió la aceptación de solicitudes (SCRUM-7). El chat exige solicitud aceptada
  y adopción existente; sin esos datos responderá 403. No se elimina esa condición.
- Fotografías registra una URL, no recibe archivos. SCRUM-15 no está completo.
- Moderación conserva el TODO de notificar al donante; no se declara terminado ese criterio.
- No se implementaron recuperación, puntos de encuentro, historial ni confirmaciones
  de entrega/recepción como parte de esta integración.
- La existencia de endpoints no acredita todos los criterios de aceptación.

## Comprobaciones

Pruebas ejecutadas con `SCRUM6_TEST_DB=1`: 142 pruebas y 8 subpruebas aprobadas.
Las pruebas de integración PostgreSQL utilizan transacciones exteriores revertidas;
pueden avanzar secuencias, pero no conservan usuarios, plantas ni otros datos de prueba.
Se verificó que todos los campos ORM existan en el esquema actual. No hay cambios en SQL
ni en migraciones. Los casos positivos de chat usan una adopción preparada únicamente
dentro de la transacción de prueba; no representan un endpoint de aceptación implementado.

## Postman compartido

Importar como colección NUEVA:
`postman/AdopPlant_API_grupal_integrada.postman_collection.json`.

Contiene 38 peticiones: 35 operaciones de negocio, dos diagnósticos y un login adicional
para obtener el token administrativo. No sustituye ni elimina las colecciones originales.

1. Para pruebas locales cambiar `baseUrl` a `http://127.0.0.1:8000`.
2. Para Render conservar `https://adopplant-api.onrender.com`, después de desplegar el commit.
3. Introducir correos, contraseñas e IDs reales como valores locales de la colección.
4. Login de usuario guarda `token_usuario`; Login administrador guarda `token_admin`.
   Los usuarios normales no obtienen permisos administrativos por usar ese login.
5. Registro y creación de recursos guardan sus IDs. Usar cuentas distintas para donante
   y adoptante. No ejecutar toda la colección automáticamente: retirar o moderar una
   planta cambia las condiciones de las peticiones posteriores.
6. Preparar una categoría activa antes de crear plantas; el chat requiere los datos previos
   indicados arriba. Los IDs están vacíos a propósito para evitar modificar recursos ajenos.
7. Los ejemplos conservados de usuarios y solicitudes se identifican como históricos locales.
   Las peticiones de los otros módulos están descritas pero no incluyen respuestas inventadas.
8. Compartir `baseUrl` para publicar documentación; no compartir contraseñas ni tokens.

Las rutas de chat son `/api/chats` y `/api/chats/{id_chat}/mensajes`.
Moderación utiliza `/api/admin/plantas` y `/api/admin/plantas/{id_planta}/moderacion`.
Estas rutas sustituyen las direcciones que no correspondían al código en Parte-Manuel.

## Despliegue

Después del push a Main, usar Render > adopplant-api > Manual Deploy > Deploy latest commit.
La conexión por repositorio público no dispara despliegue automático. No reimportar SQL.
Comprobar Live y las nuevas rutas de `/openapi.json` antes de considerar publicada la integración.
La ejecución local de las pruebas no demuestra por sí sola que Render esté actualizado.
