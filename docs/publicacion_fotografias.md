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

Pendiente antes de dar por validada la integración: subir una foto real desde
la APK contra Render, verla de nuevo después de cerrar la app, editarla y
comprobar que la misma URL es accesible desde otro dispositivo.
Este bloque no certifica todavía todos los criterios de SCRUM-5, en especial
la consulta privada completa y la concurrencia con el futuro módulo de aceptación.
