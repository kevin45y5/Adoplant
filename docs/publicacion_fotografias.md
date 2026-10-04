# SCRUM-5: publicación con fotografías

## Configuración del servidor

Render necesita `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY` y
`CLOUDINARY_API_SECRET`. No colocar estos valores en Flutter ni en Git.
Las fotos se guardan en Cloudinary y su enlace HTTPS en la tabla existente
`fotografia`. No hay migración ni cambios del esquema.

## Contrato para móvil y web

- `GET /api/categorias`: devuelve categorías activas con sus IDs reales.
- `POST /api/plantas`: enviar `multipart/form-data` con los campos de
  `PlantaCreate` y un archivo llamado `fotografia`. También se conserva la ruta
  con `/` final. El antiguo envío JSON sin foto ahora devuelve 422: una planta
  nueva debe tener fotografía desde su creación.
- `PATCH /api/plantas/{id}`: acepta JSON para editar solo datos, o
  `multipart/form-data` para enviar datos y reemplazar la foto principal.
- En JavaScript usar `FormData`; no fijar manualmente `Content-Type` porque
  el navegador debe incluir el separador del formulario. En Postman usar
  Body → form-data y seleccionar File para `fotografia`.
- La respuesta conserva `fotografia_url` y ahora incluye la categoría real.
- JPG, PNG o WebP, hasta 8 MB y 25 megapíxeles. El servidor comprueba el archivo,
  corrige orientación y lo convierte a JPEG de hasta 2000 × 2000 sin metadatos EXIF.

La planta y la referencia de su imagen se guardan en una misma transacción.
Si falla la base de datos se revierte y se intenta eliminar la imagen recién
subida. Si esa limpieza falla, queda un aviso en los logs para revisión manual.
Al reemplazar una fotografía se conserva el recurso anterior en Cloudinary;
no se borran recursos históricos automáticamente.

## Comprobación

Pruebas locales con el proveedor simulado: foto requerida, archivo falso,
tamaño excesivo, creación, reemplazo, edición sin cambiar la foto, categorías,
fallo del proveedor y reversión ante fallo de base de datos. Las pruebas
PostgreSQL utilizan transacciones que se revierten y no llaman a Cloudinary.

Krisler confirmó en la APK contra Render: publicación, persistencia de imágenes,
edición de datos, reemplazo de fotografía, retiro y separación entre cuentas.

La consulta privada usa `GET /api/plantas/mias/{id}`: incluye retiradas y ocultas
solo para el dueño. El listado conserva su respuesta de lista, acepta búsqueda,
estado, página, límite y el filtro opcional `retirada=true/false`, con orden por
ID descendente. Flutter muestra diez registros por página y consulta por ID al
editar, sin depender de la página visible. Si una página contiene exactamente
diez registros se permite avanzar; la siguiente puede estar vacía y permite volver.

Comprobación manual de consultas y aceptación SCRUM-7 confirmada por Krisler.
Editar, retirar y aceptar respetan el bloqueo de la fila de planta. La ampliación
múltiple descrita a continuación requiere su propia comprobación en teléfono.


## Carga múltiple desde móvil (3 de octubre)

Se admiten de una a cinco fotos por publicación, hasta 8 MB por archivo, en
JPG, PNG o WebP. Se mantiene el esquema existente de planta y fotografia.

- POST `/api/plantas`: formulario multipart con los datos habituales y una o
  varias entradas `fotografias` de tipo File. La API valida todas antes de subirlas.
- PATCH `/api/plantas/{id}`: los archivos `fotografias` se agregan. Para elegir
  cuáles conservar, enviar `conservar_fotografias` como texto JSON con las URLs
  actuales, por ejemplo `["https://.../actual.jpg"]`. Las omitidas se retiran de
  la publicación. `[]` permite reemplazarlas todas si se adjuntan fotos nuevas.
  Omitir este campo conserva las actuales. Es posible quitar fotos sin adjuntar
  otras, enviando multipart con el campo de conservación y al menos una URL.
- El campo singular anterior `fotografia` sigue funcionando: crea una foto o
  reemplaza la primera al editar. No mezclar ambos campos de archivos.
- Solo puede editar el dueño si está DISPONIBLE, visible y no eliminada.
- El guardado de datos y registros de fotos es una transacción. Si falla una
  carga o la base, se revierten los cambios y se intenta limpiar cada archivo
  nuevo ya subido. No se borran archivos antiguos de Cloudinary en este flujo.
- La primera foto conservada es la principal; las nuevas se agregan al final.

En Postman usar Body → form-data: repetir la clave `fotografias` con tipo File
para cada imagen, y añadir los datos descriptivos como Text. La autorización
sigue siendo Bearer del dueño. Swagger documenta las dos alternativas de carga.

Pruebas manuales: publicar con tres fotos, comprobar la galería, editar conservando
una y agregando otra, quitar sin agregar, impedir guardar sin fotos e impedir una
sexta. Estas pruebas corresponden a la carga SCRUM-5/15 y su visualización SCRUM-11.
