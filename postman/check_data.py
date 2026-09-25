import sys
sys.path.insert(0, '.')
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("INSERT INTO public.categoria (id_categoria, nombre, estado) VALUES (1, 'General', 'ACTIVA') ON CONFLICT DO NOTHING"))
    conn.commit()
    
    result = conn.execute(text("SELECT id_categoria, nombre, estado FROM public.categoria"))
    rows = result.mappings().all()
    for r in rows:
        print(dict(r))
    
    result = conn.execute(text("SELECT id_usuario, nombre, correo, estado FROM public.usuario"))
    rows = result.mappings().all()
    for r in rows:
        print(dict(r))
    
    result = conn.execute(text("SELECT id_planta, nombre, estado_planta FROM public.planta"))
    rows = result.mappings().all()
    for r in rows:
        print(dict(r))