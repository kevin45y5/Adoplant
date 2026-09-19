# Revisión de historias y cobertura de operaciones del backend

Fecha: 18 de septiembre de 2026. Responsable de la revisión: asistencia a Krisler.

## Resultado

Las 17 historias originales describen correctamente el negocio, pero no hacían
explícitas todas las consultas por ID, modificaciones y retiros que se necesitan
para demostrar la gestión de recursos solicitada por el profesor.
Se conservan las 17 historias, códigos Jira y responsables. Se amplían 11 y se
mantienen 6 sin cambios funcionales. El texto completo para Jira está en
historias_de_usuario_revisadas.md. Las versiones anteriores se retiraron del proyecto
después de consolidar todos sus criterios en la versión revisada.

Esta revisión modifica requisitos locales; no actualiza Jira automáticamente ni
implementa endpoints. Las subtareas se prepararán después de actualizar historias.

## Qué se conserva

- Diagrama original, sus clases, relaciones y enumeraciones.
- Las 14 tablas del negocio y alembic_version. Ninguna migración ni dato modificado.
- Usuarios ACTIVO/BLOQUEADO, solicitudes PENDIENTE/ACEPTADA/RECHAZADA,
  categorías ACTIVA/INACTIVA y demás enumeraciones actuales.
- Registro y login existentes, autenticación por correo o teléfono.
- Fotografías obligatorias, reglas de solicitudes, confirmación doble e historial.
- API compartida entre web y móvil; interfaz administrativa prevista en la web.
- Chat y ubicación solo para participantes después de aceptar una solicitud.

El diagrama se mantiene como modelo de dominio. No representa exhaustivamente
las operaciones HTTP: consultas, edición de datos y retiros nuevos se especifican
en estas historias y en la matriz inferior. No se afirma que sus métodos dibujados
incluyan cada operación nueva ni que esto garantice la evaluación del profesor.
Ya existían diferencias de detalle entre diagrama conceptual y esquema físico;
esta revisión no pretende convertir uno en copia exacta del otro.

## Revisión por historia

| Jira | Responsable | Resultado y cambios |
|---|---|---|
| SCRUM-1 | Krisler | Amplía gestión de cuenta: consulta propia, edición de datos y comprobación de token/estado. Conserva registro y login. |
| SCRUM-2 | Krisler | Sin cambio funcional. Recuperación no necesita inventar un CRUD independiente. |
| SCRUM-5 | Fabiola | Añade consulta de propias, edición mientras disponible y retiro lógico con rechazo de pendientes. |
| SCRUM-6 | Kevin | Añade consulta de propias/por ID, corrección del mensaje y retiro físico solo si pendiente y sin adopción. |
| SCRUM-7 | Kevin | Precisa consulta autorizada por ID y aceptación transaccional con control de concurrencia. |
| SCRUM-8 | Fabrizio | Formaliza acceso tras aceptación y conserva historial; no añade borrado de chats o mensajes para forzar un CRUD. |
| SCRUM-9 | Fabrizio | Amplía a gestionar puntos: consultar, corregir y retirar, conservando el mensaje de conversación. |
| SCRUM-10 | Fabiola | Sin cambio funcional. Catálogo, filtros y carga progresiva ya están descritos. |
| SCRUM-11 | Fabiola | Sin cambio funcional. El detalle ya cubre consulta individual de planta. |
| SCRUM-13 | Kevin | Sin cambio funcional. Conserva historial de donaciones y adopciones. |
| SCRUM-14 | Fabrizio | Añade consulta individual, lectura y tratamiento de enlaces de solicitudes retiradas. |
| SCRUM-15 | Fabiola | Sin cambio funcional. Se distingue soporte de archivos en API de cámara/permisos móviles. |
| SCRUM-16 | Kevin | Sin cambio funcional. Confirmación doble; no se permite borrar una adopción. |
| SCRUM-17 | Manuel | Precisa consulta administrativa por ID, retiro lógico y conservación de adopciones. |
| SCRUM-18 | Krisler | Añade consulta individual y reactivación; bloqueo no significa eliminar ni baja voluntaria. |
| SCRUM-19 | Manuel | Explicita cómo entra un reporte en la bandeja y su búsqueda autorizada. |
| SCRUM-20 | Manuel | Explicita listado/búsqueda, detalle, duplicados y eliminación únicamente sin referencias. |

## Operaciones por integrante

Estas son operaciones planificadas, no endpoints ya implementados. Solo registro
y login están implementados y probados en el trabajo actual. Se consideran las
operaciones del recurso, no un CRUD obligatorio dentro de cada historia.

| Integrante y recurso | Crear | Buscar/listar | Obtener individual | Modificar | Retirar o gestionar estado |
|---|---|---|---|---|---|
| Krisler: usuario | Registro | Buscar usuarios, solo administrador | Perfil propio o detalle administrativo por ID | Datos personales propios | Administrador bloquea/reactiva sin borrar usuario |
| Fabiola: planta | Publicación con foto | Catálogo y publicaciones propias | Detalle | Datos y fotos de propia disponible | Retiro lógico de propia disponible |
| Kevin: solicitud | Solicitar planta | Enviadas/recibidas y filtros | Detalle autorizado | Mensaje propio pendiente; donante acepta/rechaza | Retirar únicamente propia pendiente sin adopción |
| Fabrizio: punto de encuentro | Compartir punto como mensaje | Puntos de un chat propio | Punto por ID | Corregir punto propio mientras adopción en proceso | Retirar punto propio, dejando aviso en el chat |
| Manuel: categoría | Crear categoría | Buscar/listar categorías | Categoría por ID | Renombrar | Desactivar; borrar físicamente solo sin referencias |

Para usuarios se sigue el ejemplo del profesor de actualizar el estatus. El bloqueo
es una actualización, no un DELETE físico ni una baja voluntaria. Si la rúbrica
exige literalmente un DELETE de usuario, este caso no debe presentarse como si lo
tuviera: esa exigencia no está confirmada por el último mensaje citado. No se
inventó un estado INACTIVO/ELIMINADO ni un procedimiento que destruya su historial.

## Contratos de rutas previstos para estas operaciones

No son nuevas subtareas ni sustituyen rutas de recuperación, adopción, chat,
notificaciones, moderación y reportes ya previstas.

| Recurso | Métodos y rutas |
|---|---|
| Usuario | POST /api/auth/registro; POST /api/auth/login; GET y PATCH /api/usuarios/me; GET /api/admin/usuarios; GET /api/admin/usuarios/{id}; PATCH /api/admin/usuarios/{id}/estado |
| Planta | POST y GET /api/plantas; GET /api/plantas/mias (registrar antes de /{id}); GET, PATCH y DELETE /api/plantas/{id} |
| Solicitud | POST y GET /api/solicitudes; GET, PATCH y DELETE /api/solicitudes/{id}. PATCH distingue corrección del mensaje por el adoptante de decisión de estado por el donante; prohíbe mezclar ambas acciones. |
| Punto | POST /api/chats/{id}/mensajes con tipo UBICACION; GET /api/chats/{id}/puntos; GET, PATCH y DELETE /api/puntos-encuentro/{id}. El POST crea punto y mensaje juntos; no se duplica la creación en otra ruta. |
| Categoría | GET /api/categorias (activas); POST y GET /api/admin/categorias; GET, PATCH y DELETE /api/admin/categorias/{id}. El administrador consulta categorías activas e inactivas. |

## Comprobación contra la base y el diagrama

Se inspeccionaron columnas y enumeraciones de la base local mediante consultas de
solo lectura y las restricciones del script de estructura. Se volvió a revisar
el diagrama original del usuario.

- Usuario: ya tiene nombre, apellido, correo, teléfono y estado. No se agregan roles
  almacenados en usuario; administrador usa su relación existente. La edición no
  modifica contraseñas, IDs ni estados por campos arbitrarios del cliente.
- Planta: ya tiene visible/eliminada y campos de moderación. Retirar utiliza estos
  campos, no añade un estado RETIRADA al enum. Las pendientes se rechazan juntas;
  las aceptadas impiden el retiro por el dueño para conservar la adopción.
- Solicitud: mensaje y estado existentes soportan edición y decisión. El borrado
  de una pendiente es compatible con las FK: adopcion impide retirar aceptadas y
  notificacion.id_solicitud admite NULL y tiene ON DELETE SET NULL. Las notificaciones
  vinculadas se actualizan a aviso de retiro en la misma transacción.
- Punto: ya tiene latitud, longitud, descripción y vínculo único con mensaje.
  La cardinalidad opcional del punto en el diagrama permite que un mensaje quede
  sin punto. Retiro: borrar punto, cambiar mensaje.tipo a TEXTO y contenido a un
  aviso no vacío; se cumplen los CHECK existentes y se conserva la conversación.
  No se borra ningún mensaje de texto ni se añade borrado lógico ficticio.
- Categoría: nombre y estado existentes; la FK de planta impide borrar cualquiera
  referenciada, incluso histórica. Se mantiene esa regla conservadora.

No se inventan campos para auditoría de ediciones. Una fecha de creación no se
presenta como fecha de edición; una coordenada corregida reemplaza su valor actual,
sin prometer un historial de versiones que el esquema no almacena.

## Próximo paso

Actualizar en Jira las descripciones y criterios de las historias existentes con
el archivo revisado. Conservar sus códigos y responsables. No marcar como hechas
funciones que solo se definieron aquí. Después redactar el nuevo desglose de
subtareas; el anterior era preliminar y no incorpora todas estas ampliaciones.
No volver a usar el objetivo anterior de seis endpoints como backend completo.
