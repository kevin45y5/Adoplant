"""Pruebas con datos locales nuevos y rollback; no utiliza Render."""
import os
import pytest
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from app.models import Adopcion, Notificacion, Planta, SolicitudAdopcion
from app.security import crear_token_acceso
from tests.test_solicitudes_postgres import entorno, enviar

pytestmark = pytest.mark.skipif(os.getenv('SCRUM6_TEST_DB') != '1', reason='PostgreSQL local')

def decidir(entorno, sid, estado='ACEPTADA', rol='donante'):
    c, _, datos = entorno
    return c.patch(f'/api/solicitudes/{sid}', json={'estado': estado}, headers={
        'Authorization': 'Bearer ' + crear_token_acceso(datos['usuarios'][rol]['id'])})

def test_aceptar_atomico_y_restricciones_publicacion(entorno):
    c, db, datos = entorno
    a = enviar(entorno).json()['id_solicitud']
    b = enviar(entorno, rol='otro').json()['id_solicitud']
    r = decidir(entorno, a)
    assert r.status_code == 200, r.text
    db.expire_all()
    assert db.get(SolicitudAdopcion, a).estado == 'ACEPTADA'
    assert db.get(SolicitudAdopcion, b).estado == 'RECHAZADA'
    pid = datos['plantas']['disponible']
    assert db.get(Planta, pid).estado == 'SOLICITADA'
    adopcion = db.scalar(select(Adopcion).where(Adopcion.id_planta == pid))
    assert adopcion.estado == 'EN_PROCESO'
    assert adopcion.id_adoptante == datos['usuarios']['adoptante']['id']
    assert db.scalar(select(Notificacion).where(Notificacion.id_solicitud == a,
        Notificacion.tipo == 'SOLICITUD_ACEPTADA')).id_usuario == adopcion.id_adoptante
    assert decidir(entorno, b).status_code == 409
    assert decidir(entorno, a).status_code == 409
    h = {'Authorization': 'Bearer ' + crear_token_acceso(datos['usuarios']['donante']['id'])}
    assert c.patch(f'/api/plantas/{pid}', headers=h, json={'nombre':'No debe cambiar'}).status_code == 403
    assert c.delete(f'/api/plantas/{pid}', headers=h).status_code == 403
    assert enviar(entorno, rol='otro').status_code == 409

def test_rechazo_individual_permisos_y_consulta(entorno):
    c, db, datos = entorno
    a = enviar(entorno).json()['id_solicitud']
    b = enviar(entorno, rol='otro').json()['id_solicitud']
    assert decidir(entorno, a, rol='adoptante').status_code == 404
    assert decidir(entorno, a, rol='otro').status_code == 404
    assert decidir(entorno, a, 'RECHAZADA').status_code == 200
    db.expire_all()
    assert db.get(SolicitudAdopcion, b).estado == 'PENDIENTE'
    assert db.get(Planta, datos['plantas']['disponible']).estado == 'DISPONIBLE'
    h = {'Authorization':'Bearer '+crear_token_acceso(datos['usuarios']['donante']['id'])}
    r = c.get('/api/solicitudes?tipo=recibidas&estado=PENDIENTE',headers=h)
    assert r.status_code == 200
    assert [x['id_solicitud'] for x in r.json()] == [b]
    assert r.json()[0]['nombre_adoptante'] and r.json()[0]['nombre_planta']
    assert c.patch(f'/api/solicitudes/{b}',headers=h,json={'mensaje':'x','estado':'ACEPTADA'}).status_code == 422
    assert decidir(entorno, b).status_code == 200

def test_fallo_transaccion_revierte_todos_los_cambios(entorno, monkeypatch):
    _, db, datos = entorno
    a = enviar(entorno).json()['id_solicitud']
    b = enviar(entorno, rol='otro').json()['id_solicitud']
    def fail():
        db.flush()
        raise SQLAlchemyError('fallo simulado antes de confirmar')
    monkeypatch.setattr(db,'commit',fail)
    assert decidir(entorno,a).status_code == 503
    db.expire_all()
    assert db.get(SolicitudAdopcion,a).estado == 'PENDIENTE'
    assert db.get(SolicitudAdopcion,b).estado == 'PENDIENTE'
    assert db.get(Planta,datos['plantas']['disponible']).estado == 'DISPONIBLE'
    assert db.scalar(select(func.count()).select_from(Adopcion).where(Adopcion.id_solicitud == a)) == 0
    assert db.scalar(select(func.count()).select_from(Notificacion).where(Notificacion.id_solicitud == a,
        Notificacion.tipo == 'SOLICITUD_ACEPTADA')) == 0


@pytest.mark.parametrize('campo,valor', [('visible', False), ('eliminada', True)])
def test_no_aceptar_publicacion_retirada_u_oculta(entorno, campo, valor):
    _, db, datos = entorno
    sid = enviar(entorno).json()['id_solicitud']
    setattr(db.get(Planta, datos['plantas']['disponible']), campo, valor)
    if campo == 'eliminada':
        db.get(Planta, datos['plantas']['disponible']).visible = False
    db.commit()
    assert decidir(entorno, sid).status_code == 409


def test_sesion_y_payload_de_decision(entorno):
    c, _, datos = entorno
    sid = enviar(entorno).json()['id_solicitud']
    assert c.patch(f'/api/solicitudes/{sid}',json={'estado':'ACEPTADA'}).status_code == 401
    assert decidir(entorno, sid, rol='bloqueado').status_code == 403
    assert decidir(entorno, sid, 'PENDIENTE').status_code == 422
