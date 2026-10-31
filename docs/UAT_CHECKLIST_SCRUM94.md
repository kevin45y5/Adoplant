# Checklist de Pruebas de Aceptación (UAT) - SCRUM-94

**Objetivo:** Validar la consulta, creación, edición y baja de plantas y categorías desde las interfaces Web y Panel Admin.

## Pasos Ejecutados:
1. [X] **Acceso:** Login exitoso con credenciales de Administrador / Donante en `http://127.0.0.1:8000` y `http://localhost:5080`.
2. [X] **Consulta:** Carga de listados verificando campos: Nombre, Categoría y Estado (Respuestas 200 OK).
3. [X] **Creación:** Creación de planta/categoría completando campos obligatorios (Nombre y Categoría activa).
4. [X] **Edición:** Modificación de registro guardada y reflejada correctamente en pantalla.
5. [X] **Baja:** Desactivación de registro confirmando que ya no aparece en el catálogo público.

**Resultado:** 100% de casos en PASS. 0 errores bloqueantes o visuales.
