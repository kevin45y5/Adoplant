import sys
sys.path.insert(0, '.')
from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
    tables = [r[0] for r in result]
    print("Tables:", tables)
    for t in tables:
        result2 = conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name='{t}' AND table_schema='public' ORDER BY ordinal_position"))
        cols = [r[0] for r in result2]
        print(f"  {t}: {cols}")