-- Migrar base de datos para que coincida con los modelos actuales
-- 1. Planta: renombrar 'estado' a 'estado_planta'
ALTER TABLE public.planta RENAME COLUMN estado TO estado_planta;

-- 2. Fotografia: renombrar y agregar columnas faltantes
ALTER TABLE public.fotografia RENAME COLUMN id_foto TO id_fotografia;
ALTER TABLE public.fotografia RENAME COLUMN fecha_carga TO fecha_subida;
ALTER TABLE public.fotografia ADD COLUMN IF NOT EXISTS es_principal BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE public.fotografia ADD COLUMN IF NOT EXISTS tipo VARCHAR(50);

-- 3. Actualizar la secuencia de fotografia si existe
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.sequences WHERE sequence_name = 'fotografia_id_fotografia_seq') THEN
        -- La secuencia ya debería existir con el nombre correcto por el serial
        NULL;
    END IF;
END $$;

-- Verificar que todo esté bien
SELECT column_name FROM information_schema.columns WHERE table_name='planta' AND table_schema='public' ORDER BY ordinal_position;
SELECT column_name FROM information_schema.columns WHERE table_name='fotografia' AND table_schema='public' ORDER BY ordinal_position;