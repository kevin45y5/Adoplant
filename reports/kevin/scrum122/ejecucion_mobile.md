# SCRUM-122 — Estado de ejecución E2E móvil

**Incidencia:** [SCRUM-122 — Prueba E2E de adopción completa desde la app móvil PlantHaven](https://jdavidg555-1788882610120.atlassian.net/browse/SCRUM-122)

**Plan vinculado:** [SCRUM-114](https://jdavidg555-1788882610120.atlassian.net/browse/SCRUM-114) — Plan de pruebas del ciclo G5 (28 pruebas)

**Ejecución vinculada:** [SCRUM-115](https://jdavidg555-1788882610120.atlassian.net/browse/SCRUM-115) — Ejecución del plan de pruebas del ciclo G5

**Fecha de revisión:** 30 de octubre de 2026

## Resultado

**Estado: BLOCKED / NOT EXECUTED.** Los diez casos móviles no se ejecutaron. No se asignan resultados PASS o FAIL sin haber corrido PlantHaven en un dispositivo/emulador.

La incidencia pide una ejecución E2E de la app PlantHaven Flutter, conectada a la API FastAPI, en un emulador Android o dispositivo, usando cuentas de adoptante/donante y una planta disponible. El flujo completo pasa por login, catálogo, detalle, solicitud, aceptación, chat, punto de encuentro, confirmación de entrega/recepción, adopción completada y cierre de sesión.

## Verificación del entorno disponible

El único repositorio local en este espacio de trabajo es [Adoplant](https://github.com/kevin45y5/Adoplant), backend Python/FastAPI y web. En ese checkout no se encontraron `pubspec.yaml`, archivos Dart de integración, Appium ni Patrol. Las comprobaciones locales dieron:

| Requisito | Resultado |
|---|---|
| Código Flutter/PlantHaven | No está en el checkout disponible |
| Flutter / Dart | No disponible en PATH |
| Android Debug Bridge / emulador | No disponible en PATH |
| Appium | No disponible en PATH |
| API local FastAPI | Estaba ejecutándose en `http://127.0.0.1:8000`; la raíz, `/docs` y la conexión PostgreSQL respondieron correctamente |
| Cuentas móviles de prueba / planta publicada | No acreditadas para este flujo |

Las 124 pruebas Python y 45 pruebas web de este backend no son evidencia de los diez casos E2E de la app móvil y no se cuentan como resultados de SCRUM-122.

## Resultado por caso

| Caso | Escenario | Estado | Motivo |
|---|---|---|---|
| C-E2E-MOB-01 | Pantalla de bienvenida / login | Blocked | Falta app móvil ejecutable |
| C-E2E-MOB-02 | Catálogo y filtros | Blocked | Falta app móvil ejecutable |
| C-E2E-MOB-03 | Detalle y fotografías | Blocked | Falta app móvil ejecutable |
| C-E2E-MOB-04 | Enviar solicitud | Blocked | Falta app y cuenta adoptante/planta de prueba |
| C-E2E-MOB-05 | Donante acepta y se crea el chat | Blocked | Falta app y cuenta donante/planta de prueba |
| C-E2E-MOB-06 | Chat entre usuarios | Blocked | Falta app y datos de adopción aceptada |
| C-E2E-MOB-07 | Punto de encuentro | Blocked | Falta app y flujo previo de adopción |
| C-E2E-MOB-08 | Confirmación de entrega y recepción | Blocked | Falta app y flujo previo de adopción |
| C-E2E-MOB-09 | Estado de adopción completada e historial | Blocked | Falta app y flujo previo de adopción |
| C-E2E-MOB-10 | Cierre de sesión | Blocked | Falta app móvil ejecutable |

## Para desbloquear y ejecutar

1. Proporcionar o vincular el repositorio Flutter de PlantHaven en este espacio de trabajo.
2. Preparar Flutter/Dart y un emulador Android o dispositivo de prueba.
3. Configurar `API_BASE_URL` del cliente móvil hacia la API local accesible desde el emulador.
4. Preparar dos cuentas de prueba y una publicación disponible, aisladas de producción.
5. Ejecutar los diez casos con Patrol/Appium o el procedimiento manual definido en Jira y adjuntar logs/capturas por caso.

**Recomendación de trazabilidad:** mantener SCRUM-122 sin resolver hasta que los diez casos tengan resultado y evidencia; actualizar el estado de cada test case según la ejecución real.
