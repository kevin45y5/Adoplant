# Subtareas definitivas del backend para Jira

Versión del 18 de septiembre de 2026, basada en las historias revisadas de AdopPlant.
Estas subtareas se crean dentro de las historias existentes. Jira asignará automáticamente
el código de cada subtarea. Todas las rutas usan el prefijo `/api` y sirven tanto a la web
como a la aplicación móvil.

## Cómo registrar las subtareas

1. Crear cada subtarea dentro del SCRUM indicado.
2. Copiar el título y la descripción correspondientes.
3. Asignarla al responsable indicado.
4. Mantenerla Por hacer salvo que el avance esté expresamente confirmado aquí.
5. Al terminar, adjuntar el commit, pruebas y petición documentada en Postman.

No incluir contraseñas, claves, tokens ni códigos de recuperación en Jira. Las subtareas
de pruebas y documentación son parte del trabajo del responsable del módulo.

---

# Krisler

## SCRUM-1 Registro, inicio de sesión y gestión de cuenta

### Subtarea 1 — Implementar registro de usuarios

**Título:** Backend: implementar POST /api/auth/registro

**Descripción:** Crear el endpoint de registro con nombre, apellido, correo, teléfono,
contraseña y confirmación. Validar campos, política de contraseña y coincidencia. Rechazar
correo o teléfono duplicado, guardar únicamente el hash, crear la cuenta ACTIVA y no
devolver secretos en respuestas o errores.

**Estado real:** Implementada y probada. Falta asociar el commit y las evidencias.

### Subtarea 2 — Implementar inicio de sesión

**Título:** Backend: implementar POST /api/auth/login con JWT

**Descripción:** Permitir login mediante correo o teléfono. Verificar contraseña y estado
ACTIVO, responder «Credenciales inválidas» cuando corresponda y generar un token JWT con
vencimiento. No incluir información privada dentro del token.

**Estado real:** Implementada y probada por correo, teléfono y contraseña incorrecta.
Bloqueo probado con usuario simulado; falta evidencia integral con gestión administrativa.

### Subtarea 3 — Proteger endpoints con JWT

**Título:** Backend: verificar token y obtener usuario activo

**Descripción:** Crear una dependencia reutilizable que lea el token Bearer, valide firma,
algoritmo, vencimiento e identificador, consulte al usuario y compruebe que siga ACTIVO.
Rechazar token ausente, inválido o vencido, y bloquear también tokens emitidos antes de que
la cuenta fuera bloqueada. Esta función será usada por todos los módulos.

### Subtarea 4 — Consultar la cuenta propia

**Título:** Backend: implementar GET /api/usuarios/me

**Descripción:** Devolver al usuario autenticado su ID, nombre, apellido, correo, teléfono,
estado y fecha de registro. No aceptar otro ID ni devolver contraseña, hash, permisos o datos
de recuperación. Requerir cuenta activa.

### Subtarea 5 — Modificar datos personales

**Título:** Backend: implementar PATCH /api/usuarios/me

**Descripción:** Permitir modificar nombre, apellido, correo y teléfono de la cuenta propia.
Aplicar las mismas validaciones del registro y controlar duplicados. No permitir cambiar ID,
estado, fecha, permisos o contraseña desde este endpoint.

### Subtarea 6 — Probar y documentar gestión de cuenta

**Título:** Pruebas y Postman: registro, login, perfil y autenticación

**Descripción:** Probar éxitos, campos inválidos, duplicados, credenciales incorrectas,
tokens ausentes, inválidos y vencidos, cuenta bloqueada, consulta y edición propias. Añadir
pruebas automatizadas y guardar las peticiones con ejemplos seguros en Postman y Swagger.

## SCRUM-2 Recuperar Contraseña

### Subtarea 1 — Solicitar recuperación

**Título:** Backend: implementar POST /api/auth/recuperacion

**Descripción:** Recibir un correo, generar un código aleatorio, guardar únicamente su hash
con expiración, intentos y estado de uso, e iniciar su envío al correo registrado. Utilizar
una respuesta genérica para no revelar si la cuenta existe. Configurar el servicio de correo
con variables de entorno.

### Subtarea 2 — Restablecer contraseña

**Título:** Backend: implementar POST /api/auth/restablecer-contrasena

**Descripción:** Validar correo, código, expiración, uso e intentos. Recibir nueva contraseña
y confirmación con la misma política del registro. Actualizar el hash y marcar el código como
utilizado dentro de una transacción. No devolver el código ni los hashes.

### Subtarea 3 — Probar y documentar recuperación

**Título:** Pruebas y Postman: recuperación de contraseña

**Descripción:** Probar solicitud, correo enviado, código correcto, incorrecto, vencido y
reutilizado, límite de intentos y contraseña inválida. Verificar que la contraseña anterior
deje de funcionar y la nueva permita login. Documentar el flujo sin publicar códigos reales.

## SCRUM-18 Gestión de Usuarios

### Subtarea 1 — Verificar permisos administrativos

**Título:** Backend: crear dependencia de administrador

**Descripción:** Reutilizar el usuario autenticado y comprobar su relación con la tabla
`administrador`. Impedir acceso administrativo a usuarios normales o bloqueados. Compartir
esta dependencia con moderación, reportes y categorías.

### Subtarea 2 — Buscar usuarios

**Título:** Backend: implementar GET /api/admin/usuarios

**Descripción:** Permitir a administradores buscar usuarios por nombre, correo o ID, con
paginación. Excluir contraseñas, hashes y datos de recuperación. Validar parámetros y no
exponer el listado a usuarios normales.

### Subtarea 3 — Obtener usuario por ID

**Título:** Backend: implementar GET /api/admin/usuarios/{id}

**Descripción:** Consultar el perfil y estado de un usuario específico para administración.
Responder correctamente ante ID inexistente y nunca devolver secretos o conversaciones.

### Subtarea 4 — Bloquear o reactivar usuario

**Título:** Backend: implementar PATCH /api/admin/usuarios/{id}/estado

**Descripción:** Permitir cambiar únicamente entre ACTIVO y BLOQUEADO. Conservar todas sus
relaciones e historial. El bloqueo debe impedir login y uso de endpoints protegidos incluso
con un token emitido antes. No presentar esta operación como eliminación física.

### Subtarea 5 — Probar y documentar administración de usuarios

**Título:** Pruebas y Postman: búsqueda, detalle y estado de usuarios

**Descripción:** Probar búsqueda, paginación, detalle, ID inexistente, bloqueo, reactivación,
usuario normal y administrador. Verificar login y token después del bloqueo. Documentar los
endpoints administrativos en Postman.

---

# Fabiola

## SCRUM-5 Publicación y gestión de plantas propias

### Subtarea 1 — Preparar modelo y esquemas de planta

**Título:** Backend: modelar planta y validar datos de publicación

**Descripción:** Representar las tablas `planta` y relaciones necesarias sin recrearlas.
Crear esquemas de entrada y salida para nombre, categoría, tamaño, cuidados, salud,
necesidades de luz y agua, descripción y ubicación aproximada. Validar categoría activa.

### Subtarea 2 — Publicar planta

**Título:** Backend: implementar POST /api/plantas

**Descripción:** Permitir publicar a usuarios autenticados y activos, obteniendo el dueño
desde el token. Exigir todos los datos obligatorios y al menos una fotografía. Guardar como
DISPONIBLE, visible y no eliminada. Evitar registros incompletos si falla la operación.

### Subtarea 3 — Consultar publicaciones propias

**Título:** Backend: implementar GET /api/plantas/mias

**Descripción:** Listar las publicaciones del usuario autenticado con búsqueda, estado y
paginación. Incluir publicaciones retiradas en esta vista privada cuando corresponda. Definir
esta ruta antes de `/api/plantas/{id}` para evitar confundir «mias» con un ID.

### Subtarea 4 — Modificar una publicación propia

**Título:** Backend: implementar PATCH /api/plantas/{id}

**Descripción:** Permitir al dueño editar datos y fotografías solo cuando la planta esté
DISPONIBLE, visible y no eliminada. Conservar al menos una foto. No permitir cambiar dueño,
estado de adopción ni campos administrativos. Controlar concurrencia con aceptación o retiro.

### Subtarea 5 — Retirar una publicación propia

**Título:** Backend: implementar DELETE /api/plantas/{id} como retiro lógico

**Descripción:** Permitir al dueño retirar una planta DISPONIBLE usando `eliminada=true` y
`visible=false`. Rechazar sus solicitudes pendientes en la misma transacción. Conservar fotos,
historial y relaciones. Impedir retiro cuando exista adopción en curso o completada.

### Subtarea 6 — Probar y documentar gestión de plantas

**Título:** Pruebas y Postman: crear, consultar, modificar y retirar plantas

**Descripción:** Probar titularidad, autenticación, categoría, campos, fotografía obligatoria,
edición, retiro, estados no permitidos y concurrencia. Documentar cuerpos, archivos y
respuestas en Postman.

## SCRUM-10 Catálogo y Filtros

### Subtarea 1 — Implementar catálogo

**Título:** Backend: implementar GET /api/plantas

**Descripción:** Devolver únicamente plantas DISPONIBLES, visibles y no eliminadas, con los
datos necesarios para el catálogo y una fotografía representativa. No incluir chat, puntos de
encuentro ni ubicación exacta privada.

### Subtarea 2 — Añadir filtros y paginación

**Título:** Backend: filtrar y paginar el catálogo

**Descripción:** Añadir filtros por tamaño y nivel de cuidado, permitir combinarlos y devolver
resultados paginados con orden estable e indicación de continuidad. Validar límites y valores.

### Subtarea 3 — Probar y documentar catálogo

**Título:** Pruebas y Postman: catálogo, filtros y paginación

**Descripción:** Probar filtros individuales y combinados, páginas, catálogo vacío y parámetros
inválidos. Confirmar que plantas solicitadas, adoptadas, ocultas o retiradas no aparezcan.

## SCRUM-11 Detalle de la Planta

### Subtarea 1 — Consultar planta por ID

**Título:** Backend: implementar GET /api/plantas/{id}

**Descripción:** Devolver información completa, categoría, tamaño, cuidados, luz, agua,
fotografías, ubicación aproximada y estado. Responder adecuadamente ante ID inexistente.

### Subtarea 2 — Proteger visibilidad y privacidad

**Título:** Backend: aplicar reglas de visibilidad al detalle de planta

**Descripción:** Evitar acceso público a publicaciones ocultas o eliminadas y no incluir
ubicaciones privadas ni chats. Devolver el estado necesario para que el cliente determine si
puede mostrar la acción de solicitar; el endpoint de solicitudes aplicará la regla real.

### Subtarea 3 — Probar y documentar detalle

**Título:** Pruebas y Postman: detalle y estados de planta

**Descripción:** Probar estados DISPONIBLE, SOLICITADA y ADOPTADA, fotografías, cuidados,
ID inexistente y publicaciones moderadas. Verificar ausencia de información privada.

## SCRUM-15 Publicación Rápida con Cámara

### Subtarea 1 — Validar archivos de imagen

**Título:** Backend: recibir y validar fotografías de plantas

**Descripción:** Aceptar imágenes provenientes de web, cámara o galería mediante el mismo
mecanismo. Validar contenido, extensión, tamaño y cantidad permitida. Generar nombres seguros
y rechazar archivos que no sean imágenes.

### Subtarea 2 — Almacenar fotografías y exponer URLs

**Título:** Backend: guardar fotografías y registrar sus URLs

**Descripción:** Guardar archivos en un almacenamiento compatible con el despliegue y crear
sus registros en `fotografia`. Asociarlos a la planta, devolver URLs consultables y limpiar
archivos si falla la transacción.

### Subtarea 3 — Probar y documentar fotografías

**Título:** Pruebas y Postman: carga y consulta de fotografías

**Descripción:** Probar imágenes válidas, formatos no permitidos, tamaño o cantidad excedidos,
integración con publicación y consulta desde detalle. Documentar el envío multipart en Postman.

**Nota:** solicitar permisos y abrir cámara o galería corresponde a Flutter, no a la API.

---

# Kevin

## SCRUM-6 Envío y gestión de solicitudes propias

### Subtarea 1 — Preparar modelo y esquemas de solicitud

**Título:** Backend: modelar y validar solicitudes de adopción

**Descripción:** Representar la tabla `solicitud_adopcion` existente y crear esquemas para
crear, consultar y corregir mensajes. Validar texto no vacío de hasta 500 caracteres y los
estados existentes, sin crear estados nuevos.

### Subtarea 2 — Enviar solicitud

**Título:** Backend: implementar POST /api/solicitudes

**Descripción:** Permitir a un usuario activo solicitar una planta DISPONIBLE ajena. Obtener
el adoptante del token, guardar PENDIENTE y rechazar duplicados activos. No cambiar la planta
a SOLICITADA por una petición pendiente. Generar la notificación al donante.

### Subtarea 3 — Consultar solicitudes propias y por ID

**Título:** Backend: implementar GET /api/solicitudes y GET /api/solicitudes/{id}

**Descripción:** Permitir al adoptante listar, buscar y consultar sus solicitudes. Permitir
al donante consultar las recibidas para sus plantas. Mostrar mensaje, fecha, planta y estado,
impidiendo acceso de terceros.

### Subtarea 4 — Corregir mensaje pendiente

**Título:** Backend: actualizar mensaje mediante PATCH /api/solicitudes/{id}

**Descripción:** Permitir al adoptante corregir solo el mensaje de una solicitud propia que
siga PENDIENTE y cuya planta esté DISPONIBLE. No cambiar adoptante, planta, fecha o estado por
esta acción. Evitar mezclar esta operación con una decisión del donante.

### Subtarea 5 — Retirar solicitud pendiente

**Título:** Backend: implementar DELETE /api/solicitudes/{id}

**Descripción:** Eliminar únicamente una solicitud propia PENDIENTE y sin adopción asociada.
Actualizar sus notificaciones conservadas para indicar el retiro y retirar el enlace al ID.
Impedir eliminar solicitudes ACEPTADAS o RECHAZADAS. Controlar concurrencia con aceptación.

### Subtarea 6 — Probar y documentar solicitudes propias

**Título:** Pruebas y Postman: crear, consultar, corregir y retirar solicitudes

**Descripción:** Probar límites, planta propia o no disponible, duplicados, permisos, edición,
retiro y carreras con aceptación. Verificar la notificación y documentar todas las operaciones.

## SCRUM-7 Gestión de Solicitudes

### Subtarea 1 — Consultar solicitudes recibidas

**Título:** Backend: listar solicitudes recibidas del donante

**Descripción:** Utilizar las consultas de solicitudes para mostrar al donante únicamente las
recibidas en sus plantas, con interesado, mensaje, fecha y estado. Permitir filtros y detalle.

### Subtarea 2 — Aceptar solicitud de forma transaccional

**Título:** Backend: aceptar solicitud mediante PATCH /api/solicitudes/{id}

**Descripción:** Validar donante, planta DISPONIBLE y solicitud PENDIENTE. En una transacción,
aceptar la elegida, rechazar las demás pendientes, crear adopción EN_PROCESO, cambiar planta
a SOLICITADA y notificar al adoptante. Bloquear dos aceptaciones simultáneas.

### Subtarea 3 — Rechazar solicitud individual

**Título:** Backend: rechazar solicitud mediante PATCH /api/solicitudes/{id}

**Descripción:** Permitir al donante rechazar una solicitud PENDIENTE de su planta, manteniendo
las otras pendientes. Rechazar transiciones inválidas y operaciones de terceros.

### Subtarea 4 — Probar y documentar gestión de solicitudes

**Título:** Pruebas y Postman: solicitudes recibidas, aceptación y rechazo

**Descripción:** Probar listado autorizado, múltiples candidatos, aceptación, rechazo,
notificaciones, adopción creada, estados de planta y concurrencia. Documentar las acciones.

## SCRUM-13 Historial de Adopciones

### Subtarea 1 — Consultar historial

**Título:** Backend: implementar GET /api/adopciones/historial

**Descripción:** Obtener del token al usuario y devolver por separado plantas dadas y recibidas,
con fechas y estado. Consultar las relaciones existentes sin crear una tabla de historial.

### Subtarea 2 — Conservar y proteger historial

**Título:** Backend: integrar adopciones completadas y privacidad del historial

**Descripción:** Incluir adopciones completadas para ambos participantes con sus fechas. Conservar
los registros aunque la publicación se retire o modere. Impedir consultar el historial ajeno.

### Subtarea 3 — Probar y documentar historial

**Título:** Pruebas y Postman: historial de donaciones y adopciones

**Descripción:** Probar usuario sin movimientos, donante, adoptante, ambos papeles, fechas,
estado final, privacidad y conservación de datos relacionados.

## SCRUM-16 Confirmación de Entrega y Recepción

### Subtarea 1 — Confirmar entrega

**Título:** Backend: implementar POST /api/adopciones/{id}/entrega

**Descripción:** Permitir únicamente al donante registrar fecha de entrega en una adopción
EN_PROCESO. Validar participantes y hacer la repetición segura sin cambiar la primera fecha.

### Subtarea 2 — Confirmar recepción

**Título:** Backend: implementar POST /api/adopciones/{id}/recepcion

**Descripción:** Permitir únicamente al adoptante registrar fecha de recepción. Una sola
confirmación no completa la adopción y una repetición no altera la fecha guardada.

### Subtarea 3 — Completar adopción

**Título:** Backend: completar adopción tras ambas confirmaciones

**Descripción:** Tras cualquiera de las confirmaciones, comprobar ambas fechas. Si existen,
actualizar adopción a COMPLETADA y planta a ADOPTADA en la misma transacción. Controlar
confirmaciones simultáneas y reflejar el resultado en el historial.

### Subtarea 4 — Probar y documentar confirmaciones

**Título:** Pruebas y Postman: entrega, recepción y finalización

**Descripción:** Probar cada orden posible, confirmación única, ambas, repeticiones, terceros,
estados finales e historial. Documentar ambos endpoints.

---

# Fabrizio

## SCRUM-8 Chat entre adoptante y donante

### Subtarea 1 — Preparar modelos y acceso al chat

**Título:** Backend: modelar chat, participantes y mensajes

**Descripción:** Representar las tablas existentes y preparar esquemas de respuesta. Comprobar
pertenencia al chat en todas las operaciones. No recrear tablas ni exponer conversaciones.

### Subtarea 2 — Crear u obtener chat autorizado

**Título:** Backend: implementar POST /api/chats

**Descripción:** Crear u obtener el chat solo cuando exista solicitud ACEPTADA y adopción. Crear
donante y adoptante seleccionado como participantes en una transacción y evitar duplicados.

### Subtarea 3 — Enviar y consultar mensajes

**Título:** Backend: implementar POST y GET /api/chats/{id}/mensajes

**Descripción:** Guardar mensajes de texto no vacíos con remitente y fecha. Consultar el historial
ordenado y paginado. Autorizar únicamente a los dos participantes y conservarlo tras completar.

### Subtarea 4 — Listar chats propios

**Título:** Backend: implementar GET /api/chats

**Descripción:** Listar únicamente conversaciones del usuario autenticado, con la información
necesaria para abrirlas. No incluir chats ni ubicaciones de terceros.

### Subtarea 5 — Probar y documentar chat

**Título:** Pruebas y Postman: chat, mensajes e historial privado

**Descripción:** Probar acceso tras aceptación, ausencia de aceptación, envío, historial,
paginación, mensaje vacío, usuario ajeno y adopción completada. Documentar el flujo REST.

## SCRUM-9 Gestión del Punto de Encuentro

### Subtarea 1 — Crear punto como mensaje de ubicación

**Título:** Backend: compartir punto mediante POST /api/chats/{id}/mensajes

**Descripción:** Aceptar tipo UBICACION con latitud, longitud y descripción opcional. Validar
rangos, participante y adopción EN_PROCESO. Guardar mensaje y punto juntos en una transacción.

### Subtarea 2 — Listar y obtener puntos privados

**Título:** Backend: implementar GET /api/chats/{id}/puntos y GET /api/puntos-encuentro/{id}

**Descripción:** Permitir únicamente a los participantes listar y consultar sus puntos. Devolver
coordenadas estáticas para que web o móvil abra un mapa externo. No rastrear ubicación real.

### Subtarea 3 — Corregir punto propio

**Título:** Backend: implementar PATCH /api/puntos-encuentro/{id}

**Descripción:** Permitir al remitente corregir coordenadas y descripción mientras la adopción
siga EN_PROCESO. Mantener el mismo mensaje, autor y fecha. Validar rangos y titularidad.

### Subtarea 4 — Retirar punto propio

**Título:** Backend: implementar DELETE /api/puntos-encuentro/{id}

**Descripción:** Permitir al remitente retirar el punto durante una adopción EN_PROCESO. Eliminar
el registro de coordenadas y convertir su mensaje a TEXTO con «Punto de encuentro retirado por
el remitente», conservando ID, autor y fecha. No borrar la conversación.

### Subtarea 5 — Probar y documentar puntos de encuentro

**Título:** Pruebas y Postman: crear, consultar, modificar y retirar puntos

**Descripción:** Probar coordenadas, descripción, permisos, adopción completada, retiro y
privacidad frente al catálogo y terceros. Documentar el JSON y respuestas.

## SCRUM-14 Notificaciones

### Subtarea 1 — Preparar servicio común

**Título:** Backend: crear servicio reutilizable de notificaciones

**Descripción:** Representar la tabla y crear una función para registrar destinatario, tipo,
mensaje, fecha y referencias a planta o solicitud. Permitir que solicitudes, aceptación y
moderación la utilicen dentro de sus transacciones.

### Subtarea 2 — Consultar notificaciones propias

**Título:** Backend: implementar GET /api/notificaciones y GET /api/notificaciones/{id}

**Descripción:** Listar y consultar únicamente notificaciones del usuario autenticado. Incluir
referencias necesarias para navegar al recurso autorizado y tratar enlaces retirados.

### Subtarea 3 — Marcar notificación como leída

**Título:** Backend: implementar PATCH /api/notificaciones/{id}

**Descripción:** Permitir que el destinatario cambie `leida` a verdadero. Rechazar notificación
inexistente o ajena. No permitir cambiar destinatario, contenido o referencias arbitrariamente.

### Subtarea 4 — Probar y documentar notificaciones

**Título:** Pruebas y Postman: generación, consulta y lectura de notificaciones

**Descripción:** Probar interés en planta, aceptación, moderación, privacidad, lectura y solicitud
retirada. Documentar las rutas. Las notificaciones push externas quedan fuera de este backend.

---

# Manuel

## SCRUM-17 Moderación de Publicaciones

### Subtarea 1 — Consultar publicaciones administrativas

**Título:** Backend: implementar GET /api/admin/plantas y GET /api/admin/plantas/{id}

**Descripción:** Permitir a administradores buscar, listar y consultar todas las publicaciones,
incluidas ocultas o eliminadas lógicamente. Mostrar datos de revisión sin exponer chats o puntos.

### Subtarea 2 — Moderar publicación

**Título:** Backend: implementar PATCH /api/admin/plantas/{id}/moderacion

**Descripción:** Exigir motivo y registrar administrador y fecha. Permitir ocultar o eliminar
lógicamente usando campos existentes. Conservar fotos, solicitudes, adopciones e historial.
Rechazar pendientes que no puedan prosperar sin cancelar una adopción existente.

### Subtarea 3 — Notificar al donante

**Título:** Backend: notificar el resultado de la moderación

**Descripción:** Usar el servicio común para informar al dueño qué publicación fue retirada y
el motivo. Guardar moderación y notificación de forma consistente.

### Subtarea 4 — Probar y documentar moderación

**Título:** Pruebas y Postman: consulta y moderación de publicaciones

**Descripción:** Probar administrador, usuario normal, motivo faltante, ID inexistente, retiro del
catálogo, notificación y conservación del historial. Documentar las rutas.

## SCRUM-19 Atención a Reportes y Denuncias

### Subtarea 1 — Registrar reporte

**Título:** Backend: implementar POST /api/reportes

**Descripción:** Obtener al reportante desde el token, recibir usuario reportado y motivo no vacío,
validar existencia y evitar autorreporte. Crear el reporte EN_REVISION.

### Subtarea 2 — Buscar y consultar reportes

**Título:** Backend: implementar GET /api/admin/reportes y GET /api/admin/reportes/{id}

**Descripción:** Permitir a administradores buscar por usuario o estado, paginar y consultar el
detalle con reportante, reportado, motivo y fecha. Incluir ID del perfil reportado.

### Subtarea 3 — Actualizar estado del reporte

**Título:** Backend: implementar PATCH /api/admin/reportes/{id}

**Descripción:** Permitir cambiar entre EN_REVISION y RESUELTO y asociar al administrador que lo
gestiona. Rechazar estados inválidos y usuarios sin permisos.

### Subtarea 4 — Probar y documentar reportes

**Título:** Pruebas y Postman: creación y gestión de reportes

**Descripción:** Probar reporte válido, autorreporte, motivo vacío, usuarios inexistentes,
búsqueda, detalle, cambio de estado y permisos. Documentar todas las rutas.

## SCRUM-20 Gestión de Especies o Categorías

### Subtarea 1 — Preparar modelo y validaciones

**Título:** Backend: modelar y validar categorías

**Descripción:** Representar `categoria` sin crear otra tabla de especies. Validar nombre no vacío,
unicidad sin distinguir mayúsculas o espacios y estados ACTIVA/INACTIVA existentes.

### Subtarea 2 — Consultar categorías públicas

**Título:** Backend: implementar GET /api/categorias

**Descripción:** Devolver únicamente categorías ACTIVAS para nuevas publicaciones. Permitir su uso
por web y móvil sin exigir permisos administrativos.

### Subtarea 3 — Crear y buscar categorías administrativas

**Título:** Backend: implementar POST y GET /api/admin/categorias

**Descripción:** Permitir a administradores crear categorías ACTIVAS y buscar/listar ACTIVAS e
INACTIVAS por nombre o estado, con paginación.

### Subtarea 4 — Obtener y modificar categoría

**Título:** Backend: implementar GET y PATCH /api/admin/categorias/{id}

**Descripción:** Consultar por ID, renombrar y activar/desactivar. Una categoría inactiva no puede
elegirse en nuevas publicaciones, pero no modifica las existentes.

### Subtarea 5 — Eliminar categoría sin referencias

**Título:** Backend: implementar DELETE /api/admin/categorias/{id}

**Descripción:** Eliminar físicamente únicamente si ninguna planta la referencia. Si existe alguna
referencia, incluso histórica, rechazar la eliminación y permitir desactivarla. Mantener la
restricción actual de PostgreSQL.

### Subtarea 6 — Probar y documentar categorías

**Título:** Pruebas y Postman: CRUD y estados de categorías

**Descripción:** Probar creación, búsqueda, detalle, edición, duplicados, activación,
desactivación, eliminación libre, rechazo con referencias y permisos administrativos.

---

# Orden de coordinación

1. Krisler entrega la verificación reutilizable de token y administrador.
2. Manuel entrega consulta de categorías activas antes de finalizar publicación.
3. Fabrizio entrega el servicio común de notificaciones antes de integrar solicitudes y moderación.
4. Fabiola entrega modelos y consultas de planta antes de finalizar solicitudes.
5. Kevin entrega aceptación y adopción antes de habilitar chat y puntos.
6. Cada integrante trabaja en una rama creada desde Develop e integra primero en Develop.
7. Solo se lleva a Main código revisado, probado y documentado, porque esa rama será evaluada.

# Definición de terminado para cada subtarea

- Código integrado sin secretos ni recreación de tablas.
- Pruebas automatizadas apropiadas ejecutadas correctamente.
- Casos de éxito, error y permisos comprobados en Postman.
- Swagger muestra el endpoint, campos y respuestas principales.
- Petición guardada y descrita en la colección compartida de Postman.
- Commit con el código Jira y el nombre del responsable en el formato solicitado.
- Enlace al commit y evidencia añadidos a la subtarea de Jira.
