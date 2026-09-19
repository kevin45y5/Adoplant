# Historias de usuario revisadas de AdopPlant

Versión de trabajo del 18 de septiembre de 2026. Conserva las 17 historias y sus códigos Jira.
Revisión autorizada para precisar operaciones de backend sin alterar el diagrama ni el esquema de datos.

## Alcance y uso

Este archivo contiene las descripciones y criterios completos para actualizar las historias existentes en Jira, no subtareas.
Esta versión consolidada reemplaza los documentos anteriores dentro del proyecto. Los títulos ampliados son sugeridos; no cambian los códigos.
Los criterios añadidos se identifican como nuevos; el resto conserva los criterios originales.
La API es común para web y móvil. Pantallas, botones, cámara, permisos y apertura de mapas siguen siendo trabajo de los clientes.
La entrega actual es backend: satisfacer sus validaciones no completa automáticamente los criterios visuales de una historia.

No se agregan clases, tablas, campos ni valores de enumeraciones. Las operaciones se implementan en servicios/rutas sobre entidades existentes.
Se mantiene el diagrama como modelo de dominio, sin afirmar que enumera todos los métodos HTTP o las funciones del código.
Las operaciones nuevas aún no están programadas; registro y login siguen siendo lo implementado y probado hasta ahora.
Para el análisis de cobertura por integrante, consultar revision_historias_backend.md.

Reglas comunes: cada operación protegida comprueba token, cuenta activa, titularidad y rol; un ID conocido no concede acceso.
Las respuestas y errores no exponen secretos. Las consultas no públicas se limitan a los participantes autorizados.
Los cambios concurrentes deben conservar restricciones e historial; no se recrean tablas ni se ejecutan borrados para esta revisión.

## SCRUM-1 — Registro, inicio de sesión y gestión de cuenta

Historia original: HU 1. Responsable: Krisler.

Revisión: descripción o criterios ampliados.

Historia de Usuario: Como usuario, quiero registrarme, iniciar sesión mediante correo o teléfono, consultar mi cuenta y modificar mis datos personales desde la web o la aplicación móvil, para mantener mi información actualizada y acceder de forma segura.

Criterios de Aceptación

Escenario 1: Registro exitoso con validación de contraseña

Dado que un visitante no registrado se encuentra en el formulario de creación de cuenta,

Cuando ingresa su nombre, apellido, correo electrónico, número de teléfono y una contraseña que cumple con los requisitos (mínimo 8 caracteres, al menos una letra, un número y coincide con la confirmación),

Entonces el sistema debe registrar al usuario y crear su cuenta exitosamente.

Escenario 2: Validación de datos duplicados

Dado que un visitante intenta registrarse en la plataforma,

Cuando ingresa un correo electrónico o un número de teléfono que ya se encuentran registrados previamente en el sistema,

Entonces el sistema debe bloquear el registro y notificar que esos datos ya están en uso.

Escenario 3: Inicio de sesión exitoso y redirección

Dado que un usuario con cuenta activa se encuentra en la pantalla de inicio de sesión,

Cuando ingresa su correo electrónico o número de teléfono y su contraseña correcta,

Entonces el sistema debe autenticar el acceso y redirigir al usuario directamente al catálogo principal.

Escenario 4: Manejo de credenciales incorrectas

Dado que un usuario intenta acceder a la plataforma,

Cuando introduce un correo, teléfono o contraseña que no coinciden con los registros,

Entonces el sistema debe denegar el acceso y mostrar explícitamente el mensaje "Credenciales inválidas".

### Escenario 5: Consulta de la cuenta propia — añadido

Dado que el usuario tiene una sesión activa, cuando consulta su perfil mediante su identificador o la referencia a su cuenta actual, entonces recibe nombre, apellido, correo, teléfono, estado y fecha de registro, sin contraseña, hash ni datos de recuperación. No puede consultar perfiles privados ajenos.

### Escenario 6: Edición de datos personales — añadido

Dado que el usuario está autenticado y activo, cuando modifica nombre, apellido, correo o teléfono de su cuenta, entonces se validan los campos y la unicidad de correo y teléfono antes de guardar. No puede modificar su ID, estado administrativo, fecha de registro ni permisos por esta operación. La contraseña se gestiona por el flujo específico existente.

### Escenario 7: Validación de acceso protegido — añadido

Dado que una petición requiere autenticación, cuando llega sin token válido, con token vencido o con una cuenta bloqueada, entonces se deniega la operación. El bloqueo también afecta a tokens emitidos antes del cambio de estado.

## SCRUM-2 — Recuperación de contraseña

Historia original: HU 2. Responsable: Krisler.

Revisión: criterios originales conservados; suficiente para su función de negocio.

Historia de Usuario: Como usuario que olvidó su contraseña, quiero poder recuperarla por medio de mi correo electrónico, para crear una nueva contraseña y volver a ingresar a mi cuenta desde la aplicación móvil o la plataforma web.

Criterios de Aceptación

Escenario 1: Acceso a la recuperación de contraseña

Dado que un usuario no autenticado se encuentra en la pantalla de inicio de sesión,

Cuando visualiza las opciones de acceso,

Entonces el sistema debe mostrar claramente la opción "¿Olvidaste tu contraseña?" y permitirle hacer clic en ella.

Escenario 2: Solicitud de recuperación vía correo

Dado que el usuario ha seleccionado la opción de recuperar contraseña,

Cuando ingresa su correo electrónico registrado y envía la solicitud,

Entonces el sistema debe generar y enviar un enlace o código de recuperación a esa dirección de correo.

Escenario 3: Creación de nueva contraseña válida

Dado que el usuario utiliza el enlace o código de recuperación recibido,

Cuando ingresa y confirma una nueva contraseña que cumple con los requisitos de seguridad (mínimo 8 caracteres, al menos una letra y un número),

Entonces el sistema debe actualizar la contraseña de la cuenta exitosamente.

Escenario 4: Inicio de sesión con credenciales actualizadas

Dado que el usuario ha cambiado su contraseña correctamente,

Cuando regresa a la pantalla de inicio de sesión e ingresa su correo con la nueva contraseña,

Entonces el sistema debe autenticar el acceso y permitirle ingresar a su cuenta.

## SCRUM-5 — Publicación y gestión de plantas propias

Historia original: HU 3. Responsable: Fabiola.

Revisión: descripción o criterios ampliados.

Historia de Usuario: Como usuario registrado, quiero publicar, consultar, modificar y retirar mis publicaciones de plantas, con información y fotografías, para mantener actualizado lo que ofrezco en adopción.

Criterios de Aceptación

Escenario 1: Verificación de sesión iniciada

Dado que un usuario intenta acceder a la sección de publicar una planta,

Cuando el sistema procesa la solicitud,

Entonces debe validar que el usuario tenga una sesión iniciada activa para permitirle ver el formulario.

Escenario 2: Publicación exitosa y visibilidad en el catálogo

Dado que un usuario autenticado completa el formulario de publicación,

Cuando ingresa los datos básicos (nombre, tipo, tamaño, cuidados, estado, ubicación), adjunta una fotografía y guarda los cambios,

Entonces el sistema debe guardar la planta con el estado "Disponible" y hacer que aparezca automáticamente en el listado de adopción de la web y la aplicación móvil.

Escenario 3: Validación de campos obligatorios

Dado que un usuario está creando una nueva publicación de adopción,

Cuando intenta enviar el formulario con campos obligatorios vacíos o sin adjuntar la fotografía requerida,

Entonces el sistema debe impedir la publicación y mostrar una alerta resaltando los datos que faltan por completar.

### Escenario 4: Consulta de publicaciones propias — añadido

Dado que el donante está autenticado, cuando busca o consulta por ID sus publicaciones, entonces obtiene sus datos y estados, incluyendo las retiradas de su propio listado privado. El catálogo público mantiene sus filtros de disponibilidad y visibilidad.

### Escenario 5: Edición de una publicación disponible — añadido

Dado que el usuario es el dueño de una publicación DISPONIBLE, visible y no eliminada, cuando modifica sus datos descriptivos, cuidados o fotografías, entonces el sistema valida los mismos requisitos de publicación y conserva al menos una fotografía. No permite cambiar dueño, estado de adopción ni campos administrativos. Una nueva categoría debe estar activa; conservar la categoría original no obliga a cambiar publicaciones anteriores. Publicaciones SOLICITADAS o ADOPTADAS no se editan por esta acción.

### Escenario 6: Retiro de una publicación propia — añadido

Dado que el donante es dueño de una planta DISPONIBLE, cuando solicita retirarla, entonces se marca eliminada y no visible utilizando los campos existentes, se conservan planta y fotografías, se rechazan las solicitudes pendientes y deja de aceptar solicitudes. No se eliminan registros relacionados ni se inventa un nuevo estado de planta. Una planta con adopción en curso o completada no se retira mediante esta acción.

### Escenario 7: Protección ante operaciones simultáneas — añadido

Dado que coinciden una aceptación y una edición o retiro de la misma planta, cuando se procesan, entonces el sistema controla la concurrencia para impedir retirar o editar una planta que acaba de quedar SOLICITADA.

## SCRUM-6 — Envío y gestión de solicitudes propias

Historia original: HU 4. Responsable: Kevin.

Revisión: descripción o criterios ampliados.

Historia de Usuario: Como adoptante, quiero enviar solicitudes con una justificación, consultar las que envié y corregir o retirar las que siguen pendientes, para gestionar mi interés en las plantas sin alterar adopciones ya acordadas.

Criterios de Aceptación

Escenario 1: Envío exitoso de solicitud

Dado que un usuario adoptante se encuentra en el perfil de una planta con estado "Disponible",

Cuando redacta un mensaje de justificación de hasta 500 caracteres y confirma el envío,

Entonces el sistema debe registrar la solicitud con el estado inicial "Pendiente".

Escenario 2: Notificación al propietario

Dado que una solicitud de adopción ha sido enviada y registrada correctamente,

Cuando el sistema procesa el envío,

Entonces debe generar y enviar inmediatamente una notificación al usuario dueño de la planta.

Escenario 3: Límite de caracteres excedido

Dado que el adoptante está escribiendo el mensaje para la solicitud,

Cuando el texto introducido supera el límite máximo de 500 caracteres,

Entonces el sistema debe bloquear el botón de envío y mostrar una advertencia indicando que se ha superado el tamaño permitido.

Escenario 4: Restricción por disponibilidad de la planta

Dado que un usuario visualiza el catálogo o accede a un enlace directo de una planta,

Cuando la planta tiene un estado diferente a "Disponible" (ej. "Adoptada" o "Solicitada"),

Entonces el sistema no debe permitir el envío de nuevas solicitudes y debe ocultar o deshabilitar el botón correspondiente.

### Escenario 5: Consulta de solicitudes propias — añadido

Dado que el adoptante está autenticado, cuando lista o busca por planta y estado sus solicitudes o consulta una por ID, entonces solo obtiene solicitudes propias con mensaje, fecha, planta y estado. El donante puede consultar las recibidas para sus plantas mediante la historia de gestión.

### Escenario 6: Corrección del mensaje pendiente — añadido

Dado que una solicitud propia permanece PENDIENTE y la planta continúa DISPONIBLE, cuando el adoptante corrige su mensaje, entonces se valida texto no vacío de hasta 500 caracteres. No permite cambiar adoptante, planta, fecha ni decidir su aceptación.

### Escenario 7: Retiro de solicitud pendiente — añadido

Dado que una solicitud propia permanece PENDIENTE y no tiene adopción asociada, cuando el adoptante la retira, entonces se elimina únicamente esa solicitud. Las notificaciones conservadas dejan de enlazarla y se actualizan para indicar su retiro. No se borra una solicitud ACEPTADA o RECHAZADA ni una adopción; no se agrega el estado CANCELADA. El retiro se controla en una transacción para no competir con la aceptación.

### Escenario 8: Restricciones de identidad y duplicados — añadido

Dado que un usuario envía una solicitud, cuando se valida, entonces debe ser un usuario activo distinto del donante y no tener otra solicitud PENDIENTE o ACEPTADA para la misma planta. Enviar una solicitud pendiente no bloquea nuevas solicitudes de otras personas ni cambia la planta a SOLICITADA.

## SCRUM-7 — Gestión de solicitudes recibidas

Historia original: HU 5. Responsable: Kevin.

Revisión: descripción o criterios ampliados.

Historia de Usuario: Como donante, quiero ver todas las solicitudes de adopción recibidas para mi planta. Así puedo revisar a los interesados y elegir a quién entregarla.

Criterios de Aceptación

Escenario 1: Visualización de solicitudes y acciones

Dado que el donante accede a la pantalla de gestión de su planta publicada,

Cuando visualiza el listado de personas interesadas,

Entonces el sistema debe mostrar todas las solicitudes recibidas y habilitar los botones de "Aceptar" y "Rechazar" para cada candidato.

Escenario 2: Aceptación y rechazo automático en lote

Dado que el donante tiene múltiples solicitudes en estado pendiente para una sola planta,

Cuando hace clic en "Aceptar" a un candidato específico,

Entonces el sistema debe aprobar esa solicitud y cambiar automáticamente el estado de todas las demás solicitudes pendientes a "Rechazadas".

Escenario 3: Notificación al usuario seleccionado

Dado que el donante aprueba a un candidato,

Cuando el sistema procesa la aceptación,

Entonces debe generar y enviar inmediatamente una notificación de éxito al usuario elegido.

Escenario 4: Rechazo individual de un candidato

Dado que el donante evalúa individualmente la lista de interesados,

Cuando presiona el botón "Rechazar" en una solicitud particular,

Entonces el sistema debe descartar únicamente a ese candidato, manteniendo las demás solicitudes como pendientes.

### Escenario 5: Consistencia al aceptar una solicitud — añadido

Dado que el donante acepta una solicitud pendiente de su planta disponible, cuando termina la operación, entonces quedan la elegida ACEPTADA, las otras pendientes RECHAZADAS, la adopción EN_PROCESO, la planta SOLICITADA y la notificación al elegido. Todo se confirma junto o no se aplica. Dos peticiones simultáneas no pueden aceptar candidatos distintos.

### Escenario 6: Consulta por ID y permisos — añadido

Dado que una persona consulta o gestiona una solicitud por su identificador, cuando se comprueban permisos, entonces solo el donante de esa planta puede aceptarla o rechazarla y solo sus participantes pueden consultar su detalle. Un rechazo individual conserva las otras solicitudes pendientes.

## SCRUM-8 — Chat entre adoptante y donante

Historia original: HU 6. Responsable: Fabrizio.

Revisión: descripción o criterios ampliados.

Historia de Usuario: Como donante o adoptante seleccionado mediante una solicitud aceptada, quiero chatear con la otra persona para coordinar la entrega y consultar después la conversación desde web o móvil.

Criterios de Aceptación

Escenario 1: Envío y recepción bidireccional de mensajes

Dado que un adoptante accede a la opción de contactar al donante,

Cuando escribe y envía un mensaje de texto,

Entonces el sistema debe entregarlo al destinatario y permitir que ambos se comuniquen fluidamente dentro de la misma sala de chat.

Escenario 2: Persistencia del historial de conversación

Dado que dos usuarios han intercambiado mensajes para coordinar una adopción,

Cuando cualquiera de los dos sale de la pantalla o cierra la aplicación y vuelve a ingresar al chat,

Entonces el sistema debe cargar y mostrar todo el historial de la conversación previamente guardada.

Escenario 3: Compartir ubicación privada

Dado que el adoptante y el donante están conversando en el chat interno,

Cuando uno de los usuarios selecciona la herramienta de compartir ubicación,

Entonces el sistema debe enviar un mapa o las coordenadas exactas de encuentro únicamente dentro de ese hilo de mensajes.

Escenario 4: Protección de la ubicación frente a terceros

Dado que se ha compartido una ubicación específica mediante el chat privado,

Cuando cualquier otro usuario visite la publicación pública de esa planta en el catálogo,

Entonces el sistema debe asegurar que esa dirección u ubicación exacta permanezca oculta y no se muestre públicamente.

### Escenario 5: Habilitación después de la aceptación — añadido

Dado que una solicitud fue ACEPTADA y generó una adopción, cuando el donante o adoptante seleccionado inicia o consulta el chat de la planta, entonces el sistema permite el acceso a esos dos participantes. Una solicitud pendiente, rechazada o retirada no habilita el chat.

### Escenario 6: Conservación de conversaciones — añadido

Dado que existe un chat autorizado, cuando se consulta su historial después de cerrar la aplicación o completar la adopción, entonces se recuperan sus mensajes. No se añade eliminación de conversaciones ni edición o borrado de mensajes de texto para completar un CRUD. Los puntos de encuentro retirados conservan un mensaje informativo según la historia del mapa.

## SCRUM-9 — Gestión del punto de encuentro en mapa

Historia original: HU 7. Responsable: Fabrizio.

Revisión: descripción o criterios ampliados.

Historia de Usuario: Como participante de una adopción aceptada, quiero compartir, consultar, corregir o retirar un punto de encuentro dentro del chat desde web o móvil, para coordinar el lugar de entrega sin compartir mi ubicación en tiempo real.

Criterios de Aceptación

Escenario 1: Selección y envío del punto de encuentro

Dado que un usuario se encuentra en la pantalla del mapa dentro del chat de coordinación,

Cuando fija un marcador en una ubicación específica y confirma su selección,

Entonces el sistema debe enviar ese punto de encuentro exacto como un mensaje visible para ambas personas en el chat.

Escenario 2: Privacidad de la ubicación (sin rastreo)

Dado que los usuarios están utilizando el mapa para organizar la entrega,

Cuando interactúan con el visor geográfico,

Entonces el sistema debe mantener los marcadores de forma estática y asegurar que en ningún momento se muestre la ubicación en tiempo real de los involucrados.

Escenario 3: Generación de ruta externa (Cómo llegar)

Dado que se ha compartido un punto de encuentro en la conversación,

Cuando un usuario presiona el botón "Cómo llegar" sobre dicha ubicación,

Entonces el sistema debe capturar las coordenadas y abrir automáticamente la aplicación de mapas externa por defecto del dispositivo (ej. Google Maps o Apple Maps) para trazar la ruta.

### Escenario 4: Consulta privada por identificador — añadido

Dado que existe un punto compartido en un chat autorizado, cuando cualquiera de sus dos participantes lo consulta por ID o lista los puntos de ese chat, entonces recibe las coordenadas y descripción. Terceros no pueden acceder ni buscar puntos ajenos.

### Escenario 5: Corrección del punto compartido — añadido

Dado que el usuario envió el punto y la adopción sigue EN_PROCESO, cuando corrige latitud, longitud o descripción, entonces se valida latitud entre -90 y 90 y longitud entre -180 y 180. Se actualiza el mismo punto, conservando su mensaje y remitente. Ambos participantes consultan la ubicación vigente; no se promete historial de versiones de coordenadas.

### Escenario 6: Retiro del punto sin borrar la conversación — añadido

Dado que el usuario es quien compartió el punto y la adopción sigue EN_PROCESO, cuando retira la ubicación, entonces se elimina únicamente el registro punto_encuentro y su mensaje se conserva convertido a TEXTO con el contenido «Punto de encuentro retirado por el remitente». Ambos cambios ocurren juntos. Se mantienen ID, remitente y fecha del mensaje, sin guardar coordenadas en el aviso. La consulta posterior de ese punto responde que no existe.

### Escenario 7: Conservación tras completar la adopción — añadido

Dado que la adopción está COMPLETADA, cuando los participantes consultan la conversación, entonces conservan el acceso al historial y puntos que no fueron retirados. No pueden crear, modificar ni retirar puntos en una adopción completada.

**Implementación sobre el esquema actual:** el punto pertenece a un mensaje. Crear un punto crea también su mensaje; retirarlo conserva el mensaje como aviso de texto. No elimina el chat ni requiere un indicador de borrado nuevo.

## SCRUM-10 — Catálogo y filtros

Historia original: HU 8. Responsable: Fabiola.

Revisión: criterios originales conservados; suficiente para su función de negocio.

Historia de Usuario: Como usuario, quiero ver un catálogo de las plantas disponibles y poder filtrarlas, para encontrar fácilmente una planta que se adapte a mis preferencias y cuidados que puedo brindar.

Criterios de Aceptación

Escenario 1: Visualización del catálogo en cuadrícula

Dado que el usuario ingresa a la sección del catálogo de la plataforma,

Cuando el sistema procesa la consulta de publicaciones,

Entonces debe mostrar únicamente las plantas que tengan el estado "Disponible" presentadas en una vista de cuadrícula.

Escenario 2: Filtrado dinámico de publicaciones

Dado que el usuario se encuentra explorando el catálogo,

Cuando selecciona o cambia filtros de búsqueda según el tamaño o el nivel de cuidado,

Entonces el sistema debe actualizar la lista de resultados de forma inmediata sin necesidad de recargar la página web o vista.

Escenario 3: Carga progresiva al navegar (Scroll infinito / Paginación)

Dado que el usuario está desplazándose por el catálogo y llega al final de los elementos visibles,

Cuando continúa la navegación hacia abajo,

Entonces el sistema debe cargar y mostrar automáticamente el siguiente grupo de plantas disponibles sin interrumpir la experiencia.

## SCRUM-11 — Detalle de la planta

Historia original: HU 9. Responsable: Fabiola.

Revisión: criterios originales conservados; suficiente para su función de negocio.

Historia de Usuario: Como usuario interesado en adoptar, quiero ver la información completa de una planta, para conocer sus características y cuidados antes de solicitar su adopción.

Criterios de Aceptación

Escenario 1: Visualización de información y fotografías

Dado que el usuario selecciona una planta desde el catálogo,

Cuando accede a la pantalla de detalle de la publicación,

Entonces el sistema debe mostrar toda la información descriptiva y las fotografías de la planta.

Escenario 2: Visualización de cuidados necesarios

Dado que el usuario consulta los detalles de una planta,

Cuando revisa la sección de cuidados de la publicación,

Entonces el sistema debe mostrar la información específica sobre las necesidades de luz y agua.

Escenario 3: Indicador del estado de la planta

Dado que el usuario está en la vista de detalle de una planta,

Cuando el sistema carga la información de la publicación,

Entonces debe mostrar el estado actual de la planta como Disponible, Solicitada o Adoptada.

Escenario 4: Habilitación de botón de solicitud

Dado que el usuario visualiza una planta con estado "Disponible",

Cuando el sistema presenta la pantalla de detalle,

Entonces debe mostrar de forma visible el botón "Solicitar Adopción".

## SCRUM-13 — Historial de adopciones

Historia original: HU 10. Responsable: Kevin.

Revisión: criterios originales conservados; suficiente para su función de negocio.

Historia de Usuario: Como usuario, quiero consultar un historial de las plantas que he dado y recibido en adopción para llevar un registro de mis adopciones realizadas.

Criterios de Aceptación

Escenario 1: Visualización de plantas dadas en adopción

Dado que el usuario ingresa a la sección de historial,

Cuando consulta el apartado de donaciones,

Entonces el sistema debe mostrar el listado de las plantas que ha publicado y dado en adopción.

Escenario 2: Visualización de plantas recibidas

Dado que el usuario ingresa a la sección de historial,

Cuando consulta el apartado de adopciones,

Entonces el sistema debe mostrar el listado de las plantas que ha recibido de otros donantes.

Escenario 3: Información de fecha y estado

Dado que el usuario visualiza los registros en su historial,

Cuando el sistema carga las publicaciones del listado,

Entonces cada registro debe mostrar la fecha de la transacción y el estado final de la adopción.

## SCRUM-14 — Notificación de interés en una planta

Historia original: HU 11. Responsable: Fabrizio.

Revisión: descripción o criterios ampliados.

Historia de Usuario: Como donante, quiero recibir una notificación cuando alguien esté interesado en adoptar una de mis plantas, para poder revisar la solicitud a tiempo.

Criterios de Aceptación

Escenario 1: Recepción e información de la notificación

Dado que un adoptante envía una solicitud por una planta del donante,

Cuando el sistema procesa el envío de la solicitud,

Entonces debe generar una notificación para el donante indicando qué planta fue solicitada.

Escenario 2: Acceso directo a la solicitud

Dado que el donante recibe la notificación de adopción,

Cuando interactúa o selecciona la notificación,

Entonces el sistema debe dirigirlo directamente a la vista con el detalle de la solicitud recibida.

### Escenario 3: Consulta y lectura de notificaciones propias — añadido

Dado que el usuario está autenticado, cuando lista sus notificaciones, consulta una por ID o la marca como leída, entonces solo opera sobre las que le pertenecen. La respuesta contiene los identificadores necesarios para navegar al recurso autorizado.

### Escenario 4: Solicitud retirada antes de abrir la notificación — añadido

Dado que una solicitud pendiente fue retirada, cuando el destinatario abre la notificación conservada, entonces se informa que fue retirada y no se ofrece un enlace a un recurso inexistente. No se pierde la notificación ni se crea otra solicitud.

## SCRUM-15 — Fotografías desde la aplicación móvil

Historia original: HU 12. Responsable: Fabiola.

Revisión: criterios originales conservados; suficiente para su función de negocio.

Historia de Usuario: Como donante, quiero tomar o seleccionar fotografías de mi planta desde la aplicación móvil, para agregarlas fácilmente al momento de publicarla en adopción.

Criterios de Aceptación

Escenario 1: Solicitud de permisos de acceso

Dado que el donante intenta tomar o seleccionar una foto desde la aplicación móvil,

Cuando es la primera vez que accede a estas funciones de captura o almacenamiento,

Entonces la aplicación debe solicitar la autorización formal para acceder a la cámara y galería del dispositivo.

Escenario 2: Captura de fotografía con la cámara

Dado que el donante cuenta con los permisos de cámara activos,

Cuando elige la opción de tomar una nueva foto durante la publicación,

Entonces el sistema debe activar la cámara del dispositivo y adjuntar la foto capturada al formulario.

Escenario 3: Selección de fotografías desde la galería

Dado que el donante cuenta con los permisos de galería activos,

Cuando elige la opción de seleccionar imágenes guardadas en el dispositivo,

Entonces el sistema debe abrir el almacenamiento de fotos y permitir seleccionar las imágenes deseadas.

Escenario 4: Visualización correcta en la publicación

Dado que el donante ha adjuntado las fotos y finalizado la publicación,

Cuando la planta es guardada y registrada en la plataforma,

Entonces las imágenes tomadas o seleccionadas deben cargarse y mostrarse correctamente en la ficha de la planta.

**Alcance backend:** recibir, validar y almacenar imágenes y devolver referencias accesibles. La cámara y los permisos siguen pendientes hasta desarrollar Flutter.

## SCRUM-16 — Confirmación de entrega y recepción

Historia original: HU 13. Responsable: Kevin.

Revisión: criterios originales conservados; suficiente para su función de negocio.

Historia de Usuario: Como usuario, quiero confirmar la entrega y recepción de la planta, para que la adopción quede registrada como completada cuando ambas personas confirmen el intercambio.

Criterios de Aceptación

Escenario 1: Marcado de entrega por parte del donante

Dado que el donante se encuentra en el seguimiento de la adopción en curso,

Cuando selecciona la opción de marcar la planta como "Entregada",

Entonces el sistema debe registrar su confirmación y guardar la fecha de entrega.

Escenario 2: Marcado de recepción por parte del adoptante

Dado que el adoptante se encuentra en el seguimiento de la adopción en curso,

Cuando selecciona la opción de marcar la planta como "Recibida",

Entonces el sistema debe registrar su confirmación y guardar la fecha de recepción.

Escenario 3: Cambio de estado a adopción completada

Dado que ambos usuarios han interactuado con la plataforma para validar el intercambio,

Cuando el sistema verifica que tanto el donante confirmó la entrega como el adoptante confirmó la recepción,

Entonces la adopción debe actualizar su estado automáticamente a "Completada".

Escenario 4: Actualización en el historial de los usuarios

Dado que una adopción alcanza el estado "Completada",

Cuando los usuarios involucrados consulten sus cuentas,

Entonces el sistema debe mostrar el registro completo de la adopción en el historial tanto del donante como del adoptante.

## SCRUM-17 — Moderación de publicaciones

Historia original: HU 14. Responsable: Manuel.

Revisión: descripción o criterios ampliados.

Historia de Usuario: Como administrador, quiero revisar el listado completo de plantas publicadas, para poder eliminar u ocultar aquellas que contengan spam, contenido inapropiado o no cumplan con las reglas de la plataforma.

Criterios de Aceptación

Escenario 1: Visualización del listado de publicaciones

Dado que el administrador accede al módulo de moderación del panel web,

Cuando el sistema procesa la consulta de información,

Entonces debe mostrar una tabla detallada con todas las publicaciones registradas y su estado actual.

Escenario 2: Opción de eliminar u ocultar publicación

Dado que el administrador se encuentra revisando el listado de plantas,

Cuando identifica una publicación que incumple las normas,

Entonces el sistema debe habilitar el botón de "Eliminar/Ocultar" para dicha publicación.

Escenario 3: Notificación de motivo al donante

Dado que el administrador ejecuta la acción de eliminar u ocultar una planta,

Cuando confirma el retiro de la publicación,

Entonces el sistema debe enviar un mensaje automático al donante explicando el motivo de la eliminación.

### Escenario 4: Consulta administrativa por identificador — añadido

Dado que el administrador consulta una publicación por ID desde moderación, cuando se verifican sus permisos, entonces puede revisar sus datos y estado incluso si no es visible públicamente. Esto no habilita acceso a chats ni ubicaciones privadas.

### Escenario 5: Eliminación lógica y conservación de relaciones — añadido

Dado que el administrador retira una publicación, cuando aplica la moderación, entonces utiliza visible y eliminada, registra motivo, fecha y administrador, y notifica al donante. Conserva fotografías, solicitudes y adopciones. Rechaza pendientes que ya no puedan prosperar, sin cancelar ni borrar una adopción existente.

## SCRUM-18 — Administración de usuarios

Historia original: HU 15. Responsable: Krisler.

Revisión: descripción o criterios ampliados.

Historia de Usuario: Como administrador, quiero buscar usuarios, consultar su perfil por ID y bloquear o reactivar cuentas, para administrar el acceso a la plataforma conservando sus publicaciones e historial.

Criterios de Aceptación

Escenario 1: Búsqueda de usuarios registrados

Dado que el administrador se encuentra en el módulo de gestión de usuarios,

Cuando realiza una búsqueda ingresando un nombre, correo electrónico o ID de usuario,

Entonces el sistema debe filtrar y mostrar los perfiles coincidentes con los criterios ingresados.

Escenario 2: Cambio de estado de usuario

Dado que el administrador revisa el perfil de un usuario con estado "Activo",

Cuando ejecuta la acción para modificar su estado a "Bloqueado",

Entonces el sistema debe actualizar y registrar el nuevo estado de la cuenta.

Escenario 3: Restricción de inicio de sesión

Dado que un usuario tiene asignado el estado "Bloqueado",

Cuando intenta iniciar sesión desde la página web o la aplicación móvil,

Entonces el sistema debe denegar el acceso e impedir el ingreso a la plataforma.

### Escenario 4: Consulta privada del perfil por ID — añadido

Dado que un administrador autenticado selecciona un usuario, cuando consulta su ID, entonces obtiene sus datos de perfil y estado sin contraseña ni hash. Un usuario normal solo puede consultar o modificar su cuenta conforme a la historia de gestión de cuenta.

### Escenario 5: Reactivación de cuenta — añadido

Dado que una cuenta está BLOQUEADA, cuando un administrador autorizado decide reactivarla, entonces su estado vuelve a ACTIVO y puede iniciar sesión con sus credenciales. Solo se utilizan los estados existentes ACTIVO y BLOQUEADO.

### Escenario 6: Bloqueo sin eliminación de datos — añadido

Dado que se suspende el acceso a una cuenta, cuando cambia a BLOQUEADO, entonces se deniegan login y operaciones protegidas incluso con tokens previos. Se mantienen sus relaciones. Este cambio administrativo no representa una solicitud de baja voluntaria ni una eliminación física de usuario.

## SCRUM-19 — Bandeja de reportes

Historia original: HU 16. Responsable: Manuel.

Revisión: descripción o criterios ampliados.

Historia de Usuario: Como administrador, quiero tener una bandeja de entrada para recibir reportes de usuarios, para poder evaluar las situaciones notificadas y tomar medidas correctivas.

Criterios de Aceptación

Escenario 1: Visualización del detalle de reportes

Dado que el administrador ingresa a la bandeja de entrada de reportes,

Cuando selecciona o abre un reporte recibido,

Entonces el sistema debe mostrar la información de quién envía el reporte, a qué usuario se reporta y el motivo escrito.

Escenario 2: Gestión de estados del reporte

Dado que el administrador se encuentra revisando un reporte en la bandeja,

Cuando modifica el seguimiento de la incidencia,

Entonces el sistema debe permitirle cambiar y guardar el estado como "En Revisión" o "Resuelto".

Escenario 3: Acceso directo al perfil reportado

Dado que el administrador evalúa un reporte en la plataforma,

Cuando hace clic en el acceso directo del usuario reportado,

Entonces el sistema debe redirigirlo directamente a su perfil para permitir la aplicación de sanciones si es necesario.

### Escenario 4: Creación de un reporte — añadido

Dado que un usuario activo necesita informar una conducta indebida, cuando indica al usuario reportado y un motivo no vacío, entonces el sistema registra quién reporta y crea el reporte EN_REVISION. No permite reportarse a sí mismo ni reportar un usuario inexistente.

### Escenario 5: Búsqueda y consulta administrativa — añadido

Dado que un administrador revisa reportes, cuando busca por usuario o estado o consulta un ID, entonces recibe solo información autorizada y puede actualizar EN_REVISION o RESUELTO. El acceso al perfil utiliza el ID del reportado y las reglas de administración de usuarios.

## SCRUM-20 — Administración de categorías

Historia original: HU 17. Responsable: Manuel.

Revisión: descripción o criterios ampliados.

Historia de Usuario: Como administrador, quiero crear, buscar, consultar por ID, editar, desactivar y eliminar categorías sin uso, para mantener organizada la clasificación de plantas y conservar las referencias históricas.

Criterios de Aceptación

Escenario 1: Creación de nueva categoría

Dado que el administrador se encuentra en la sección de gestión de categorías,

Cuando completa el formulario simple con el nombre de una nueva categoría y confirma la acción,

Entonces el sistema debe registrar y habilitar la nueva categoría en la plataforma.

Escenario 2: Edición de categoría existente

Dado que el administrador selecciona una categoría del listado,

Cuando modifica su nombre y guarda los cambios,

Entonces el sistema debe actualizar la información de la categoría correctamente.

Escenario 3: Restricción de eliminación de categorías en uso

Dado que una categoría tiene plantas activas vinculadas a ella,

Cuando el administrador intenta eliminarla del sistema,

Entonces el sistema debe impedir la eliminación permanente de dicha categoría.

Escenario 4: Desactivación u ocultamiento para futuras publicaciones

Dado que una categoría no se puede eliminar por tener plantas activas vinculadas,

Cuando el administrador ejecuta la opción de desactivarla o cambiar su estado,

Entonces el sistema debe ocultarla de la lista de selección para que no pueda ser elegida en futuras publicaciones.

### Escenario 5: Búsqueda y consulta de categorías — añadido

Dado que se consulta la clasificación, cuando un usuario obtiene las categorías para publicar, entonces solo recibe ACTIVAS; un administrador puede buscar por nombre o estado y consultar una por ID, incluidas INACTIVAS.

### Escenario 6: Eliminación de categorías sin referencias — añadido

Dado que una categoría no está vinculada a ninguna planta, cuando un administrador solicita eliminarla, entonces el sistema puede eliminarla. Si cualquier planta la referencia, incluso histórica, se impide el borrado y se ofrece desactivarla, conservando la restricción actual de PostgreSQL.

### Escenario 7: Validación de nombres y referencias — añadido

Dado que se crea o renombra una categoría, cuando el nombre está vacío o duplica otro sin distinguir mayúsculas y espacios exteriores, entonces se rechaza. Desactivar una categoría no modifica las publicaciones existentes y evita elegirla en nuevas publicaciones.

**Precisión del escenario 3 original:** la restricción ya existente protege toda categoría referenciada, no solo las que tienen plantas activas; el escenario añadido de eliminación explicita esta condición.

