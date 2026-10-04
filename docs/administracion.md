# Administrador de PlantHaven

Panel: `/views/admin.html`. Permite buscar usuarios y bloquearlos/reactivarlos, ocultar/mostrar publicaciones con un motivo y resolver/reabrir reportes. No permite bloquear la propia cuenta ni restaurar publicaciones retiradas desde este panel.

La API verifica el rol en la tabla `administrador` para cada operación. El correo no otorga permisos automáticamente. El menú Administración aparece en Inicio cuando `/api/admin/me` confirma el rol.

## Activar la cuenta solicitada

Correo designado: **revertlewandosky@gmail.com**. Debe estar registrado y activo en la misma base de datos que utiliza la API.

Después de desplegar este código, ejecutar desde la consola del servicio de Render, en la raíz del proyecto:

```sh
python -m scripts.asignar_admin
```

El comando asigna el rol únicamente a la cuenta existente con ese correo. Se puede repetir sin duplicar el rol. No cambia contraseñas ni crea cuentas. Si el correo no existe, termina sin modificar la base. Después, iniciar sesión normalmente y abrir Administración.

En la base local revisada esa cuenta no existe. La asignación en Render requiere ejecutar el comando anterior con la configuración del servidor; preparar el código local no modifica la base remota.
