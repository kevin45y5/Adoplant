import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import pytest
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from app.database import engine
from app.models import Adopcion, Planta, Usuario
from app.routes.adopciones import confirmar_entrega, confirmar_recepcion
from app.routes.solicitudes import decidir_solicitud
from test_gestion_concurrencia_postgres import carrera  # noqa: F401

pytestmark = pytest.mark.skipif(os.getenv('SCRUM6_TEST_DB') != '1', reason='PostgreSQL local')


def test_confirmaciones_simultaneas_no_pierden_fechas(carrera):
    datos, solicitudes = carrera
    pid = datos['plantas']['disponible']
    with Session(engine) as db:
        decidir_solicitud(db, solicitudes[0], datos['usuarios']['donante']['id'], 'ACEPTADA')
        aid = db.scalar(select(Adopcion.id_adopcion).where(Adopcion.id_planta == pid))
    barrier = Barrier(2)
    def confirmar(rol):
        with Session(engine) as db:
            db.execute(text("SET LOCAL lock_timeout = '5s'"))
            user = db.get(Usuario, datos['usuarios'][rol]['id'])
            barrier.wait(timeout=5)
            fn = confirmar_entrega if rol == 'donante' else confirmar_recepcion
            return fn(aid, db, user)
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(confirmar, rol) for rol in ('donante', 'adoptante')]
        results = [job.result(timeout=15) for job in jobs]
    assert any(r['estado'] == 'COMPLETADA' for r in results)
    with Session(engine) as db:
        row = db.get(Adopcion, aid)
        assert row.fecha_entrega is not None and row.fecha_recepcion is not None
        assert row.estado == 'COMPLETADA'
        assert db.get(Planta, pid).estado == 'ADOPTADA'
