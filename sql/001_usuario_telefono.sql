-- HU 1: teléfono obligatorio y único. Conserva los registros existentes.
-- Si existen teléfonos nulos o repetidos, la transacción falla sin cambiar datos.
BEGIN;
ALTER TABLE public.usuario ALTER COLUMN telefono SET NOT NULL;
CREATE UNIQUE INDEX uq_usuario_telefono ON public.usuario (btrim(telefono));
COMMIT;
