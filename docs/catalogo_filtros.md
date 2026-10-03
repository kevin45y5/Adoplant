# SCRUM-10 — Catálogo y filtros

GET `/api/plantas` devuelve exclusivamente plantas DISPONIBLES, visibles y no
eliminadas. Conserva `total`, `pagina`, `limite` y `plantas`; añade `hay_mas` y
`filtros` (opciones de tamaño, cuidado, categoría y ubicación del catálogo completo).
No modifica tablas. Los detalles individuales continúan mostrando otros estados.

Parámetros opcionales combinables: `busqueda` (nombre parcial), `tamano`,
`nivel_cuidado`, `categoria` (nombre) y `ubicacion`. Estos últimos comparan el texto
completo sin distinguir mayúsculas ni espacios exteriores. Valores sin coincidencias
devuelven una lista vacía. No se impone una enumeración nueva a los datos existentes.
`pagina` empieza en 1; `limite` acepta 1 a 100. Orden: fecha descendente y luego ID
descendente. El parámetro anterior `estado` se conserva pero no permite obtener
plantas no disponibles por este catálogo.

Ejemplo para Postman: `{{baseUrl}}/api/plantas?tamano=Mediano&nivel_cuidado=Bajo&pagina=1&limite=12`.
La app carga 12 por página, combina filtros en el servidor y carga la siguiente al
acercarse al final. Descarta respuestas antiguas si cambian filtros; muestra error y
reintento sin perder páginas ya cargadas. Deslizar hacia abajo actualiza el catálogo.

Pruebas: cuadrícula, cada filtro y combinaciones, limpiar filtros, búsqueda sin
resultados, carga de la segunda página cuando hay más de 12 coincidencias y ausencia
de publicaciones solicitadas/adoptadas/ocultas/retiradas. Backend y prueba móvil
automatizados; pendiente confirmación manual en Render y APK.
