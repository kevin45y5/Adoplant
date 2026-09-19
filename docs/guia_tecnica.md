# Guía técnica vigente de AdopPlant

Esta guía describe la arquitectura acordada. Los requisitos funcionales vigentes
están en `historias_de_usuario_revisadas.md` y su ejecución se organiza mediante
`subtareas_backend_jira.md`. Ante una diferencia, prevalecen esos dos archivos.

Actualización del 18 de septiembre de 2026: la meta abarca el backend de las 17
historias. Registro y login son las funciones implementadas hasta ahora. La misma
API alimentará la futura web y la aplicación Flutter. El chat y los puntos de
encuentro se habilitan únicamente después de aceptar una solicitud.

ADOPPLANT

Documentación técnica del proyecto

Arquitectura, tecnologías y estrategia de implementación

Proyecto académico de aplicación web y móvil para adopción de plantas

Institución: ______________________________

Módulo: __________________________________

Integrantes: ______________________________

Docente: __________________________________

Fecha: ____________________________________

1 Introducción

AdopPlant es un sistema académico orientado a facilitar la adopción responsable de plantas. Permitirá que una persona publique una planta que ya no puede cuidar y que otra persona solicite adoptarla. El sistema tendrá una página web y una aplicación móvil, pero ambas utilizarán la misma lógica de negocio, la misma API REST y la misma base de datos.

La solución se desarrollará con una arquitectura monolítica. El backend estará construido con Python y FastAPI; la interfaz web utilizará HTML, CSS, JavaScript, Bootstrap y Jinja2; la aplicación móvil se desarrollará con Flutter y Dart; y PostgreSQL almacenará la información. Postman se utilizará para verificar los endpoints de la API.

2 Objetivo general

Desarrollar una plataforma web y móvil que permita publicar plantas, consultar el catálogo, enviar y gestionar solicitudes de adopción, coordinar la entrega mediante chat y punto de encuentro, confirmar la entrega y conservar un historial, utilizando una API REST centralizada.

3 Alcance funcional

Registro, inicio de sesión, recuperación de contraseña y manejo de roles.

Publicación de plantas con fotografías, características, cuidados y ubicación aproximada.

Catálogo de plantas disponibles con búsqueda, filtros y carga progresiva.

Solicitudes de adopción con aceptación o rechazo por parte del donante.

Chat entre donante y adoptante para coordinar la entrega.

Selección y envío de un punto de encuentro sin compartir ubicación en tiempo real.

Confirmación de planta entregada y recibida antes de completar la adopción.

Notificaciones e historial de plantas dadas y recibidas.

Administración de publicaciones, usuarios, reportes y categorías.

4 Arquitectura seleccionada

4.1 Arquitectura monolítica

El backend se implementará como una sola aplicación FastAPI. La autenticación, publicaciones, solicitudes, chat, notificaciones, administración y acceso a datos formarán parte del mismo proyecto, se ejecutarán como una unidad y utilizarán una base de datos PostgreSQL compartida. No se crearán microservicios independientes.

La organización del código en carpetas no cambia la arquitectura seleccionada. Las carpetas únicamente facilitan el mantenimiento; el sistema continúa siendo una sola aplicación monolítica.

4.2 Relación entre los componentes

1.  El usuario realiza una acción desde la página web o desde la aplicación Flutter.

2.  El cliente envía una solicitud HTTP al endpoint correspondiente de FastAPI.

3.  FastAPI valida los datos y aplica las reglas del negocio.

4.  SQLAlchemy consulta o modifica la información almacenada en PostgreSQL.

5.  FastAPI devuelve una respuesta JSON con el resultado.

6.  La web o Flutter actualiza la pantalla para el usuario.

5 Tecnologías y herramientas

Área

Tecnología

Uso en AdopPlant

Arquitectura

Monolítica

Mantener toda la lógica del backend en una sola aplicación.

Lenguaje backend

Python

Implementar la lógica del sistema y los endpoints.

Framework API

FastAPI

Construir la API REST, validar solicitudes y devolver JSON.

Servidor

Uvicorn

Ejecutar la aplicación FastAPI durante desarrollo y despliegue.

Interfaz web

HTML5, CSS3 y JavaScript

Construir las pantallas que utilizará el navegador.

Estilos web

Bootstrap

Facilitar un diseño adaptable a diferentes pantallas.

Plantillas web

Jinja2

Generar páginas HTML desde la aplicación FastAPI.

Aplicación móvil

Flutter y Dart

Crear la aplicación para dispositivos móviles.

Base de datos

PostgreSQL

Guardar usuarios, plantas, solicitudes, mensajes y demás datos.

ORM

SQLAlchemy

Relacionar las clases de Python con las tablas de PostgreSQL.

Migraciones

Alembic

Registrar y aplicar cambios controlados en la estructura de la base de datos.

Validación

Pydantic

Validar tipos, campos obligatorios y estructuras de entrada y salida.

Autenticación

JWT

Mantener sesiones seguras mediante tokens de acceso.

Pruebas de API

Postman

Probar endpoints, parámetros, respuestas, errores y autenticación.

Documentación API

OpenAPI y Swagger

Documentar y ejecutar endpoints desde el navegador.

Versiones

Git y GitHub

Controlar cambios y permitir el trabajo colaborativo.

6 Backend y API REST

FastAPI será el núcleo del sistema. Recibirá solicitudes desde la web y Flutter mediante HTTP y responderá principalmente con datos JSON. Pydantic validará la información recibida y SQLAlchemy se encargará del acceso a PostgreSQL. La documentación interactiva estará disponible mediante Swagger durante el desarrollo.

Método

Endpoint de referencia

Propósito

POST

/api/auth/registro

Crear una cuenta de usuario.

POST

/api/auth/login

Validar credenciales y entregar un token.

GET

/api/plantas

Consultar plantas disponibles y aplicar filtros.

POST

/api/plantas

Publicar una planta con sus datos y fotografía.

GET

/api/plantas/{id}

Consultar el detalle de una planta.

POST

/api/solicitudes

Enviar una solicitud de adopción.

PATCH

/api/solicitudes/{id}

Aceptar o rechazar una solicitud.

GET

/api/chats/{id}/mensajes

Consultar el historial de mensajes.

POST

/api/chats/{id}/mensajes

Enviar un mensaje o punto de encuentro.

POST

/api/adopciones/{id}/entrega

Confirmar la entrega como donante.

POST

/api/adopciones/{id}/recepcion

Confirmar la recepción como adoptante.

GET

/api/notificaciones

Consultar notificaciones del usuario.

7 Página web

La página web utilizará HTML5 para la estructura, CSS3 y Bootstrap para el diseño adaptable, JavaScript para interacciones y solicitudes a la API, y Jinja2 para renderizar plantillas desde FastAPI. Los recursos web podrán permanecer en el mismo proyecto monolítico mediante carpetas de plantillas y archivos estáticos.

8 Aplicación móvil

Flutter construirá las pantallas de Android y consumirá los mismos endpoints REST utilizados por la página web. La aplicación manejará formularios, autenticación, catálogo, solicitudes, chat, fotografías, ubicación y notificaciones. Flutter no tendrá una base de datos central separada; la información oficial permanecerá en PostgreSQL.

Cámara y galería para agregar fotografías a una publicación.

Permisos del dispositivo solicitados solamente cuando sean necesarios.

Almacenamiento seguro del token de autenticación.

Consumo de la API mediante HTTPS en el entorno publicado.

Manejo visual de carga, éxito, errores y ausencia de conexión.

9 Base de datos

PostgreSQL centralizará los datos de ambas plataformas. Las tablas principales se relacionarán para conservar la trazabilidad completa del proceso de adopción. Las contraseñas nunca se almacenarán en texto plano; se guardará únicamente su hash seguro.

Entidad

Información principal

Usuarios

Cuenta, correo, contraseña protegida mediante hash y estado. Los administradores
se identifican mediante la relación existente en la tabla administrador.

Plantas

Información, fotografías, cuidados, ubicación aproximada y estado.

Solicitudes

Adoptante, planta, mensaje, fecha y estado de la solicitud.

Adopciones

Solicitud aceptada y confirmaciones de entrega y recepción.

Chats

Conversación asociada a la planta y habilitada por una solicitud aceptada y su adopción.

Mensajes

Emisor, contenido, fecha y posible punto de encuentro.

Notificaciones

Destinatario, tipo, contenido, fecha y estado de lectura.

Reportes

Usuario remitente, usuario reportado, motivo y resolución.

Categorías

Clasificación y estado visible u oculto de la categoría.

10 Autenticación y roles

Después de validar el correo y la contraseña, FastAPI generará un token JWT. La web y Flutter enviarán el token en las solicitudes protegidas. El backend verificará el token, el estado de la cuenta y el rol antes de permitir una acción.

Rol

Permisos principales

Adoptante

Consultar plantas, enviar solicitudes, chatear y confirmar recepción.

Donante

Publicar plantas, gestionar solicitudes, chatear y confirmar entrega.

Administrador

Gestionar publicaciones, usuarios, reportes y categorías.

11 Fotografías

Flutter permitirá tomar fotografías o seleccionarlas desde la galería. La web permitirá seleccionar archivos desde la computadora. FastAPI recibirá los archivos, validará formato y tamaño, almacenará la referencia y devolverá la URL necesaria para presentar las imágenes en las publicaciones.

12 Mapa y punto de encuentro

El mapa se utilizará únicamente para escoger un punto de encuentro y consultar cómo llegar. El sistema almacenará latitud, longitud y una descripción del lugar. El punto podrá compartirse dentro del chat después de aceptar una solicitud. No se mostrará la ubicación en tiempo real ni la dirección exacta del domicilio del usuario.

1.  El usuario abre la pantalla de ubicación desde el chat.

2.  Selecciona un lugar público en el mapa.

3.  La aplicación obtiene las coordenadas del marcador.

4.  FastAPI guarda el punto asociado a la conversación o adopción.

5.  El otro usuario recibe el punto dentro del chat.

6.  La opción Cómo llegar abre Google Maps u otro servicio compatible.

13 Chat y notificaciones

Para una primera entrega académica, los mensajes pueden guardarse mediante endpoints REST y actualizarse de forma periódica. Si se exige comunicación instantánea, FastAPI admite WebSockets, que permiten enviar y recibir mensajes sin recargar la pantalla. Para notificaciones con la aplicación cerrada puede integrarse Firebase Cloud Messaging; las notificaciones internas continuarán registrándose en PostgreSQL.

14 Reglas principales del negocio

Solo usuarios registrados y activos podrán publicar o solicitar plantas.

Toda planta nueva iniciará con el estado Disponible.

Solo se podrá solicitar una planta que se encuentre Disponible.

El mensaje de solicitud tendrá un máximo de 500 caracteres.

Al aceptar una solicitud, las demás solicitudes pendientes para esa planta serán rechazadas.

El chat y el punto de encuentro estarán disponibles para coordinar la adopción.

La adopción se completará únicamente cuando el donante confirme Entregada y el adoptante confirme Recibida.

Los usuarios bloqueados no podrán iniciar sesión en la web ni en la aplicación móvil.

Una categoría con plantas activas no se eliminará; podrá ocultarse para publicaciones futuras.

La ubicación exacta y la ubicación en tiempo real no serán públicas.

15 Estrategia de pruebas

Postman se utilizará para las pruebas funcionales manuales de la API. Cada conjunto de endpoints se organizará en colecciones y se probará con datos válidos, inválidos, incompletos y sin autorización. Las pruebas manuales se complementarán con pruebas automatizadas en el backend y pruebas de interfaz e integración en Flutter.

Tipo

Herramienta

Objetivo

Funcional

Postman

Comprobar métodos, respuestas y reglas de negocio.

Validación

Postman y Pydantic

Rechazar campos vacíos, tipos incorrectos y límites excedidos.

Autenticación

Postman

Verificar JWT, roles, sesiones y usuarios bloqueados.

Automatizada backend

pytest

Comprobar servicios y endpoints después de cambios.

Móvil

Flutter test

Comprobar widgets, navegación e integración con la API.

16 Seguridad y privacidad

Usar HTTPS al publicar el sistema.

Aplicar hash seguro a las contraseñas y nunca devolverlas en la API.

Guardar claves, secretos y configuración sensible en variables de entorno.

Validar extensiones y tamaño de fotografías.

Comprobar permisos y roles en el backend, no solamente en la interfaz.

No publicar domicilios ni ubicación en tiempo real.

Restringir las acciones administrativas al rol Administrador.

17 Organización sugerida del proyecto

La siguiente organización mantiene el backend como una sola aplicación monolítica y separa archivos únicamente para facilitar el trabajo del equipo.

adopplant/  main.py  models/  schemas/  routes/  services/  database/  templates/  static/  tests/  requirements.txt  .env.example

18 Flujo general de adopción

1.  El donante publica una planta y el sistema la registra como Disponible.

2.  El adoptante consulta el catálogo y abre el detalle.

3.  El adoptante envía una solicitud con un mensaje.

4.  El donante recibe la notificación y acepta o rechaza la solicitud.

5.  Al aceptar una solicitud, se habilita la coordinación mediante chat.

6.  Ambas personas acuerdan y comparten un punto de encuentro.

7.  El donante confirma que la planta fue entregada.

8.  El adoptante confirma que la planta fue recibida.

9.  La adopción cambia a Completada y aparece en ambos historiales.

19 Decisión tecnológica final

La combinación seleccionada es adecuada para el alcance académico de AdopPlant. FastAPI permite concentrarse en los conceptos de API REST, validación y documentación sin incorporar desde el inicio todas las funciones de un framework web completo. Flutter puede consumir la API sin incompatibilidades y Postman permite comprobar cada endpoint antes de conectarlo con las interfaces.

Decisión final: arquitectura monolítica, Python con FastAPI para el backend y la API REST, HTML5, CSS3, JavaScript, Bootstrap y Jinja2 para la página web, Flutter con Dart para la aplicación móvil, PostgreSQL como base de datos y Postman como herramienta principal de pruebas manuales de la API.
