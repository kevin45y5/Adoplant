"""Carreras reales con conexiones independientes y datos locales desechables."""
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import pytest
from fastapi import HTTPException
from sqlalchemy import select, delete, text
from sqlalchemy.orm import Session
from app.database import engine
from app.models import Adopcion, Fotografia, Notificacion, Planta, SolicitudAdopcion, Usuario
from app.routes.solicitudes import decidir_solicitud
from app.routes.plantas import modificar_planta, retirar_planta
from app.schemas import PlantaUpdate
from scripts.preparar_postman import crear_datos

pytestmark = pytest.mark.skipif(os.getenv('SCRUM6_TEST_DB') != '1', reason='PostgreSQL local')

@pytest.fixture
def carrera():
    assert engine.url.host in ('localhost', '127.0.0.1'), 'Solo base local'
    with Session(engine) as db:
        datos = crear_datos(db)
        datos.pop('clave', None)
        pid = datos['plantas']['disponible']
        categoria = db.get(Planta, pid).id_categoria
        db.add(Fotografia(id_planta=pid, url='https://example.com/prueba.jpg'))
        ids = []
        for rol in ['adoptante', 'otro']:
            s = SolicitudAdopcion(id_planta=pid, id_adoptante=datos['usuarios'][rol]['id'], mensaje='Carrera', estado='PENDIENTE')
            db.add(s); db.flush(); ids.append(s.id_solicitud)
        db.commit()
    try:
        yield datos, ids
    finally:
        with Session(engine) as db:
            plantas = list(datos['plantas'].values())
            db.execute(delete(Notificacion).where(Notificacion.id_planta.in_(plantas)))
            db.execute(delete(Adopcion).where(Adopcion.id_planta.in_(plantas)))
            db.execute(delete(SolicitudAdopcion).where(SolicitudAdopcion.id_planta.in_(plantas)))
            db.execute(delete(Fotografia).where(Fotografia.id_planta.in_(plantas)))
            db.execute(delete(Planta).where(Planta.id_planta.in_(plantas)))
            db.execute(text('DELETE FROM public.categoria WHERE id_categoria=:id'), {'id': categoria})
            db.execute(delete(Usuario).where(Usuario.id_usuario.in_([u['id'] for u in datos['usuarios'].values()])))
            db.commit()

@pytest.mark.parametrize('rival', ['aceptar', 'retirar', 'editar'])
def test_operaciones_simultaneas(carrera, rival):
    datos, ids = carrera
    pid = datos['plantas']['disponible']
    uid = datos['usuarios']['donante']['id']
    barrera = Barrier(2)
    def operar(primera):
        with Session(engine) as db:
            db.execute(text("SET LOCAL lock_timeout = '5s'"))
            usuario = db.get(Usuario, uid)
            barrera.wait(timeout=5)
            try:
                if primera or rival == 'aceptar':
                    decidir_solicitud(db, ids[0 if primera else 1], uid, 'ACEPTADA')
                elif rival == 'retirar':
                    retirar_planta(pid, usuario, db)
                else:
                    modificar_planta(pid, (PlantaUpdate(nombre='Editada antes de aceptar'), None), usuario, db)
                return 200
            except HTTPException as e:
                db.rollback()
                return e.status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        a = pool.submit(operar, True); b = pool.submit(operar, False)
        resultados = [a.result(timeout=15), b.result(timeout=15)]
    with Session(engine) as db:
        planta = db.get(Planta, pid)
        adopciones = db.scalars(select(Adopcion).where(Adopcion.id_planta == pid)).all()
        solicitudes = db.scalars(select(SolicitudAdopcion).where(SolicitudAdopcion.id_planta == pid)).all()
        if rival == 'aceptar':
            assert sorted(resultados) == [200, 409]
        elif rival == 'retirar':
            assert sorted(resultados) in ([200, 403], [200, 409])
        else:
            assert resultados[0] == 200 and resultados[1] in (200, 403)
        if planta.eliminada:
            assert not adopciones and all(s.estado == 'RECHAZADA' for s in solicitudes)
        else:
            assert planta.estado == 'SOLICITADA' and len(adopciones) == 1
            assert sum(s.estado == 'ACEPTADA' for s in solicitudes) == 1
            assert sum(s.estado == 'RECHAZADA' for s in solicitudes) == 1
