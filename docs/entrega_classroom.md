# Presentación del Backend — Indicaciones y seguimiento

Este documento conserva las indicaciones de Classroom proporcionadas por Krisler.
Debe consultarse al planificar trabajo, pruebas, documentación y entregas.
Los requisitos funcionales siguen en `historias_de_usuario_revisadas.md` y las tareas
en `subtareas_backend_jira.md`. Este archivo no cambia las historias ni el esquema.

## 1. Objetivo indicado por el docente

Elaborar el backend de la aplicación mediante una API REST.

## 2. Entrega grupal — PDF

Un integrante del grupo entregará un documento PDF con:

- [ ] Portada oficial con el nombre de todos los integrantes del grupo.
- [ ] Diagrama de clases completo del proyecto. Si se trabaja con microservicios,
  adjuntar un diagrama por cada API.
- [ ] Tecnologías backend utilizadas en el desarrollo.
- [ ] Enlace a Jira con todas las historias de usuario y el desglose de tareas del backend.
- [ ] Enlace a Postman con la documentación de todos los endpoints. Se permite
  la importación desde Swagger.
- [ ] Enlace a GitHub con los repositorios del código fuente de las API desarrolladas.
- [ ] Enlaces a las API desarrolladas y publicadas en Somee, Render o un servicio similar.

**Aplicación a AdopPlant:** el equipo está formado por Krisler, Fabiola, Kevin,
Fabrizio y Manuel. El proyecto utiliza una API monolítica compartida por web y móvil.
Las casillas representan evidencias de entrega pendientes de verificar; no son
una afirmación de que el código correspondiente esté pendiente.

## 3. Entrega individual — PDF

Cada estudiante entregará un PDF individual con:

- [ ] Portada oficial con sus datos y los de la institución.
- [ ] Enlace a un video o documento PDF explicativo que muestre:
  - La historia de usuario desarrollada.
  - Las tareas asignadas en Jira para cada endpoint a su cargo.
  - La demostración práctica y las pruebas de funcionamiento de esos endpoints
    utilizando Postman.

## 4. Commits y control de versiones — Obligatorio

**Formato de los mensajes:**

```text
[Código_Jira] Nombre Integrante: Tarea trabajada - Descripción breve (opcional)
```

**Ejemplo del docente:**

```text
[PROY-12] Juan Pérez: Codificación del endpoint de crear Marcas - Se avanzó en el controlador de Marcas.
```

- Se pueden crear ramas por historia de usuario o acordar una estrategia de equipo.
- El repositorio debe contar con las ramas principales **Main** y **Develop**.
- **La revisión del avance se realizará directamente sobre Main.**
- Antes de entregar, verificar que los cambios probados estén integrados y subidos
  a Main. Tenerlos únicamente en Develop no cumple ese punto de revisión.

## 5. Aclaraciones previas del docente transmitidas por el usuario

Estas aclaraciones provienen de mensajes anteriores; se distinguen de la lista
de Classroom reproducida arriba.

- Mínimo un CRUD por integrante. Un único endpoint no equivale a un CRUD completo.
- Las operaciones indicadas son crear, modificar, eliminar, buscar y obtener por ID.
- La API responde a la lógica de negocio y las historias, y alimenta web y móvil.
- El docente utilizó cambio de estatus (baja o activación) en su ejemplo de usuarios.
  El reparto acordado aplica bloqueo/reactivación conservando datos; no eliminación física.
- Por ahora se trabaja en backend; las pantallas móviles no forman parte de ese trabajo.
- Swagger no es obligatorio, pero el docente recomienda generar documentación
  automática o un JSON importable en Postman.

El objetivo acordado del equipo es desarrollar el backend de las 17 historias.
No confundir ese objetivo con un requisito explícito de completar las 17 para esta
entrega: el texto recibido no fija ese porcentaje ni una fecha nueva. El anterior
objetivo del 25 % no sustituye los requisitos actuales ni el mínimo por integrante.

## 6. Swagger, OpenAPI y Postman en este proyecto

| Elemento | Qué es | Para qué se utiliza |
| --- | --- | --- |
| Swagger UI, `/docs` | Página interactiva de documentación de la API | Consultar y probar las operaciones disponibles. |
| OpenAPI, `/openapi.json` | Descripción estructurada de la API en JSON | Importar rutas, parámetros y esquemas en Postman. |
| Colección de Postman | Conjunto de peticiones guardadas | Organizar, ejecutar, documentar y demostrar endpoints. |
| Enlace de documentación de Postman | Documentación compartida de la colección | Incluirlo en el PDF grupal y verificar acceso del docente. |
| URL de la API publicada | Dirección accesible del backend desplegado | Probar la API fuera del equipo local e incluirla en la entrega. |

Importar OpenAPI ahorra crear manualmente cada petición, pero no demuestra que
funcione. Después se deben ejecutar las peticiones, completar descripciones y
guardar ejemplos de éxito y error sin secretos reales. El enlace local de Swagger
no reemplaza el enlace de Postman ni el de la API publicada.

### Primera importación a Postman

1. Mantener la API local encendida.
2. Comprobar que `http://127.0.0.1:8000/docs` abre en el navegador.
3. En Postman, seleccionar **Import** y pegar
   `http://127.0.0.1:8000/openapi.json`.
4. Importar como **Postman Collection** si aparece esa elección.
5. Nombrar la colección **AdopPlant API** y revisar las peticiones importadas.
6. Revisar que la URL o variable de servidor utilice `http://127.0.0.1:8000`.
7. Si no se puede importar desde la dirección local, guardar el JSON desde el
   navegador e importar ese archivo en Postman.

La dirección debe usar el puerto real del servidor si se ejecuta en otro puerto.
No importar `/docs`: esa dirección contiene la página visual, no la especificación.
Al agregar endpoints, actualizar la colección conservando las pruebas y ejemplos
ya preparados; no suponer que la importación se sincroniza automáticamente.

Referencia: [Importar datos en Postman](https://learning.postman.com/docs/getting-started/importing-and-exporting/importing-data).

## 7. Estado verificado el 28-09-2026

- API publicada: https://adopplant-api.onrender.com
- Swagger: https://adopplant-api.onrender.com/docs
- Postman de SCRUM-1 y SCRUM-18: https://documenter.getpostman.com/view/58260475/2sBYB4LSGg
- GitHub: https://github.com/kevin45y5/Adoplant (rama de evaluación: Main).
- OpenAPI público incluye siete operaciones de usuarios y cinco de solicitudes propias.
- Las pruebas manuales de usuarios en Render fueron confirmadas por el responsable:
  registro, login, consulta y edición propia, listado administrativo, consulta por ID,
  bloqueo, rechazo de acceso bloqueado y reactivación.
- Las colecciones recibidas de los otros integrantes no equivalen a código desplegado.
  Falta verificar e integrar los módulos restantes y completar su documentación pública.
- SCRUM-2 y SCRUM-9 no están acreditados como terminados en esta revisión.
- Reparto actualizado: SCRUM-8 corresponde a Manuel, SCRUM-9 a Krisler y
  Fabrizio conserva SCRUM-14. El resto del reparto se conserva.

## 8. Pendientes grupales

1. Comprobar el avance de cada integrante frente al mínimo de CRUD requerido.
2. Integrar únicamente código revisado y probado en Main y actualizar Render manualmente.
3. Añadir la documentación de los módulos entregados y comprobar sus enlaces públicos.
4. Completar portada, diagrama, tecnologías, Jira, GitHub, Postman y API en el PDF grupal.
5. Verificar acceso del docente y correspondencia entre documentación, Main y despliegue.

Los documentos personales de preparación del video no forman parte de este repositorio.
