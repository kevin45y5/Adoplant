# SCRUM-16 — Confirmación de entrega y recepción

Se reutiliza la implementación de adopciones que el equipo web integró en Main.
La app móvil consulta la misma API y los mismos registros; no se agregan tablas
ni dependencias. La ruta web `/confirmar` sigue funcionando sin cambios de contrato.

## Rutas autenticadas

- `GET /api/adopciones`: adopciones del usuario, en proceso y completadas.
- `GET /api/adopciones/{id}`: detalle privado con rol y ambas fechas.
- `POST /api/adopciones/{id}/entrega`: sin cuerpo, solo el donante.
- `POST /api/adopciones/{id}/recepcion`: sin cuerpo, solo el adoptante.
- `POST /api/adopciones/{id}/confirmar`: compatibilidad web, determina acción por identidad.

Éxito: 200, adopción con `estado`, `rol`, `fecha_entrega`, `fecha_recepcion`,
participantes y planta. 401 sin sesión válida; 403 cuenta bloqueada o acción del
rol contrario; 404 adopción inexistente o ajena. Si ocurre un error de base de
datos se revierte la transacción y se responde 503; consultar antes de reintentar.

Una sola confirmación mantiene EN_PROCESO y planta SOLICITADA. Ambas confirmaciones,
en cualquier orden, actualizan la adopción a COMPLETADA y la planta a ADOPTADA
atómicamente. Las repeticiones devuelven el registro y conservan las primeras
fechas, sin duplicar las notificaciones. El bloqueo de filas evita perder una
confirmación cuando ambos teléfonos envían al mismo tiempo.

## Móvil

Acceso desde el icono de manos en el catálogo (Mis adopciones) y desde el chat
(Confirmar entrega o recepción). Cada participante ve solo su botón y confirma
mediante un diálogo. La vista actualiza cada cinco segundos en primer plano;
las completadas permanecen consultables con participantes y fechas. Esto cubre
el seguimiento de SCRUM-16, sin añadir la historia independiente de historial.

## Validación

Pruebas dirigidas de permisos, ambos órdenes, repetición, notificaciones, chat,
puntos y confirmaciones simultáneas ejecutadas en PostgreSQL local. Flutter
comprueba los botones por rol, cancelación del diálogo y estado final.

Pendiente en teléfonos: desplegar esta API, instalar la APK nueva, abrir una
adopción aceptada; confirmar uno, comprobar EN PROCESO; confirmar el otro,
comprobar COMPLETADA en ambos, reabrir y comprobar fechas e historial del chat.
Después de completar, los puntos se conservan pero no se pueden cambiar.
