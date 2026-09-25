import sys
sys.path.insert(0, '.')
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # 1. Planta: renombrar 'estado' a 'estado_planta'
    conn.execute(text("ALTER TABLE public.planta RENAME COLUMN estado TO estado_planta"))
    conn.commit()
    
    # 2. Fotografia: renombrar y agregar columnas faltantes
    conn.execute(text("ALTER TABLE public.fotografia RENAME COLUMN id_foto TO id_fotografia"))
    conn.commit()
    conn.execute(text("ALTER TABLE public.fotografia RENAME COLUMN fecha_carga TO fecha_subida"))
    conn.commit()
    conn.execute(text("ALTER TABLE public.fotografia ADD COLUMN IF NOT EXISTS es_principal BOOLEAN NOT NULL DEFAULT false"))
    conn.commit()
    conn.execute(text("ALTER TABLE public.fotografia ADD COLUMN IF NOT EXISTS tipo VARCHAR(50)"))
    conn.commit()
    
    # Verificar
    result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='planta' AND table_schema='public' ORDER BY ordinal_position"))
    print("planta:", [r[0] for r in result])
    result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='fotografia' AND table_schema='public' ORDER BY ordinal_position"))
    print("fotografia:", [r[0] for r in result])
    print("Migracion completa")