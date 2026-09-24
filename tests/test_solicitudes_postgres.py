"""Integración optativa: SCRUM6_TEST_DB=1 python -m pytest.

Cada caso utiliza una transacción exterior que siempre se revierte. No modifica
registros existentes. PostgreSQL puede consumir números de secuencia.
"""
import os

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import engine, get_db
from app.main import app
from app.models import Notificacion, Planta, SolicitudAdopcion
from app.routes import solicitudes
from app.security import crear_token_acceso
from scripts.preparar_postman import crear_datos

pytestmark = pytest.mark.skipif(os.getenv("SCRUM6_TEST_DB") != "1",
                                reason="Requiere SCRUM6_TEST_DB=1 y PostgreSQL local")


@pytest.fixture
def entorno():
    with engine.connect() as conexion:
        exterior = conexion.begin()
        with Session(bind=conexion, join_transaction_mode="create_savepoint") as db:
            datos = crear_datos(db)
            db.commit()
            anteriores = app.dependency_overrides.copy()
            app.dependency_overrides[get_db] = lambda: db
            try:
                with TestClient(app) as cliente:
                    yield cliente, db, datos
            finally:
                app.dependency_overrides = anteriores
        exterior.rollback()


def enviar(entorno, rol="adoptante", planta="disponible", **campos):
    cliente, _, datos = entorno
    headers = {} if rol is None else {"Authorization": "Bearer " + crear_token_acceso(
        datos["usuarios"][rol]["id"])}
    return cliente.post("/api/solicitudes", headers=headers, json={
        "id_planta": datos["plantas"][planta], "mensaje": "Quiero cuidarla", **campos})


def test_creacion_notificacion_y_otros_adoptantes(entorno):
    _, db, datos = entorno
    r = enviar(entorno, mensaje="a" * 500)
    assert r.status_code == 201, r.text
    cuerpo = r.json()
    assert cuerpo["estado"] == "PENDIENTE"
    assert cuerpo["id_adoptante"] == datos["usuarios"]["adoptante"]["id"]
    assert "contrasena" not in cuerpo
    aviso = db.scalar(select(Notificacion).where(Notificacion.id_solicitud == cuerpo["id_solicitud"]))
    assert aviso.id_usuario == datos["usuarios"]["donante"]["id"]
    assert aviso.id_planta == datos["plantas"]["disponible"]
    assert aviso.leida is False
    assert db.get(Planta, aviso.id_planta).estado == "DISPONIBLE"
    assert enviar(entorno).status_code == 409
    assert enviar(entorno, rol="otro").status_code == 201


@pytest.mark.parametrize("rol,planta,codigo", [
    (None, "disponible", 401), ("bloqueado", "disponible", 403),
    ("donante", "disponible", 403), ("adoptante", "solicitada", 409),
    ("adoptante", "adoptada", 409), ("adoptante", "oculta", 404),
    ("adoptante", "eliminada", 404),
])
def test_permisos_y_disponibilidad(entorno, rol, planta, codigo):
    assert enviar(entorno, rol=rol, planta=planta).status_code == codigo


@pytest.mark.parametrize("campos", [{"mensaje": " "}, {"mensaje": "a" * 501},
                                    {"id_adoptante": 1}, {"estado": "ACEPTADA"}])
def test_payload_no_permitido(entorno, campos):
    assert enviar(entorno, **campos).status_code == 422


def test_planta_inexistente(entorno):
    assert enviar(entorno, id_planta=2147483647).status_code == 404


def test_fallo_notificacion_revierte_solicitud(entorno, monkeypatch):
    _, db, datos = entorno

    def fallar(*args, **kwargs):
        raise SQLAlchemyError("Fallo simulado de notificaciones")

    monkeypatch.setattr(solicitudes, "notificar_solicitud", fallar)
    assert enviar(entorno).status_code == 503
    assert db.scalar(select(func.count()).select_from(SolicitudAdopcion).where(
        SolicitudAdopcion.id_planta == datos["plantas"]["disponible"])) == 0


@pytest.mark.parametrize("estado,codigo", [("ACEPTADA", 409), ("RECHAZADA", 201)])
def test_solicitud_anterior(entorno, estado, codigo):
    _, db, datos = entorno
    db.add(SolicitudAdopcion(id_planta=datos["plantas"]["disponible"],
                            id_adoptante=datos["usuarios"]["adoptante"]["id"],
                            mensaje="Solicitud anterior", estado=estado))
    db.commit()
    assert enviar(entorno).status_code == codigo


def actuar(entorno, metodo, ruta='', rol='adoptante', **kwargs):
    cliente, _, datos = entorno
    headers = {} if rol is None else {'Authorization': 'Bearer ' + crear_token_acceso(
        datos['usuarios'][rol]['id'])}
    return cliente.request(metodo, '/api/solicitudes' + ruta, headers=headers, **kwargs)


def test_consultas_privadas_filtros_y_paginacion(entorno):
    primera = enviar(entorno).json()
    segunda = enviar(entorno, rol='otro').json()
    assert [s['id_solicitud'] for s in actuar(entorno, 'GET').json()] == [primera['id_solicitud']]
    assert actuar(entorno, 'GET', rol='donante').json() == []
    recibidas = actuar(entorno, 'GET', rol='donante', params={'tipo': 'recibidas'}).json()
    assert {s['id_solicitud'] for s in recibidas} == {primera['id_solicitud'], segunda['id_solicitud']}
    assert len(actuar(entorno, 'GET', rol='donante', params={'tipo': 'recibidas', 'limite': 1, 'offset': 1}).json()) == 1
    assert actuar(entorno, 'GET', params={'estado': 'ACEPTADA'}).json() == []
    assert actuar(entorno, 'GET', params={'id_planta': entorno[2]['plantas']['adoptada']}).json() == []
    assert actuar(entorno, 'GET', params={'estado': 'PENDIENTE', 'id_planta': primera['id_planta']}).json()[0]['mensaje'] == primera['mensaje']
    ruta = '/' + str(primera['id_solicitud'])
    for rol in ['adoptante', 'donante']:
        assert actuar(entorno, 'GET', ruta, rol=rol).status_code == 200
    assert actuar(entorno, 'GET', ruta, rol='otro').status_code == 404


def test_editar_y_retirar_conserva_avisos(entorno):
    _, db, _ = entorno
    original = enviar(entorno).json()
    ruta = '/' + str(original['id_solicitud'])
    aviso = db.scalar(select(Notificacion.id_notificacion).where(
        Notificacion.id_solicitud == original['id_solicitud']))
    r = actuar(entorno, 'PATCH', ruta, json={'mensaje': '  Ahora tengo más espacio  '})
    assert r.status_code == 200
    assert r.json() == dict(original, mensaje='Ahora tengo más espacio')
    assert actuar(entorno, 'DELETE', ruta).status_code == 204
    assert actuar(entorno, 'GET', ruta).status_code == 404
    assert actuar(entorno, 'DELETE', ruta).status_code == 404
    notificacion = db.get(Notificacion, aviso)
    assert notificacion.id_solicitud is None
    assert 'retirada' in notificacion.mensaje
    assert notificacion.id_planta == original['id_planta']
    assert db.get(Planta, original['id_planta']).estado == 'DISPONIBLE'
    assert enviar(entorno).status_code == 201


@pytest.mark.parametrize('metodo', ['PATCH', 'DELETE'])
@pytest.mark.parametrize('rol,codigo', [('otro', 404), ('donante', 404), (None, 401), ('bloqueado', 403)])
def test_modificaciones_protegidas(entorno, metodo, rol, codigo):
    s = enviar(entorno).json()
    assert actuar(entorno, metodo, '/' + str(s['id_solicitud']), rol=rol,
                  **({'json': {'mensaje': 'Cambio'}} if metodo == 'PATCH' else {})).status_code == codigo
    assert actuar(entorno, 'GET', '/' + str(s['id_solicitud'])).json() == s


@pytest.mark.parametrize('estado', ['ACEPTADA', 'RECHAZADA'])
@pytest.mark.parametrize('metodo', ['PATCH', 'DELETE'])
def test_solicitudes_decididas_no_modificables(entorno, estado, metodo):
    _, db, _ = entorno
    s = enviar(entorno).json()
    db.get(SolicitudAdopcion, s['id_solicitud']).estado = estado
    db.commit()
    assert actuar(entorno, metodo, '/' + str(s['id_solicitud']),
                  **({'json': {'mensaje': 'Cambio'}} if metodo == 'PATCH' else {})).status_code == 409
    assert db.get(SolicitudAdopcion, s['id_solicitud']).estado == estado


@pytest.mark.parametrize('payload', [{}, {'mensaje': ''}, {'mensaje': ' '}, {'mensaje': 'a'*501},
                                    {'mensaje': None}, {'mensaje': 'bien', 'id_planta': 1},
                                    {'mensaje': 'bien', 'estado': 'ACEPTADA'}])
def test_edicion_valida_payload(entorno, payload):
    s = enviar(entorno).json()
    assert actuar(entorno, 'PATCH', '/' + str(s['id_solicitud']), json=payload).status_code == 422


def test_edicion_planta_no_disponible_y_retiro_pendiente(entorno):
    _, db, _ = entorno
    s = enviar(entorno).json()
    db.get(Planta, s['id_planta']).estado = 'SOLICITADA'
    db.commit()
    ruta = '/' + str(s['id_solicitud'])
    assert actuar(entorno, 'PATCH', ruta, json={'mensaje': 'Cambio'}).status_code == 409
    assert actuar(entorno, 'DELETE', ruta).status_code == 204


@pytest.mark.parametrize('metodo', ['GET', 'PATCH', 'DELETE'])
def test_id_inexistente_y_limites(entorno, metodo):
    kwargs = {'json': {'mensaje': 'Cambio'}} if metodo == 'PATCH' else {}
    assert actuar(entorno, metodo, '/2147483647', **kwargs).status_code == 404
    assert actuar(entorno, metodo, '/0', **kwargs).status_code == 422


@pytest.mark.parametrize('params', [{'tipo': 'todas'}, {'estado': 'CANCELADA'}, {'limite': 101},
                                   {'offset': -1}, {'id_planta': 0}])
def test_filtros_invalidos(entorno, params):
    assert actuar(entorno, 'GET', params=params).status_code == 422


@pytest.mark.parametrize('metodo', ['PATCH', 'DELETE'])
def test_adopcion_asociada_no_se_modifica(entorno, metodo):
    from sqlalchemy import text
    _, db, datos = entorno
    s = enviar(entorno).json()
    db.execute(text('''INSERT INTO public.adopcion
        (id_solicitud, id_planta, id_donante, id_adoptante)
        VALUES (:solicitud, :planta, :donante, :adoptante)'''),
        {'solicitud': s['id_solicitud'], 'planta': s['id_planta'],
         'donante': datos['usuarios']['donante']['id'], 'adoptante': s['id_adoptante']})
    db.commit()
    assert actuar(entorno, metodo, '/' + str(s['id_solicitud']),
                  **({'json': {'mensaje': 'Cambio'}} if metodo == 'PATCH' else {})).status_code == 409


def test_retiro_fallido_revierte_notificacion(entorno, monkeypatch):
    from sqlalchemy import event
    _, db, _ = entorno
    s = enviar(entorno).json()
    def fallar(mapper, connection, target):
        raise SQLAlchemyError('Fallo simulado al borrar')
    event.listen(SolicitudAdopcion, 'before_delete', fallar)
    try:
        assert actuar(entorno, 'DELETE', '/' + str(s['id_solicitud'])).status_code == 503
    finally:
        event.remove(SolicitudAdopcion, 'before_delete', fallar)
    assert db.get(SolicitudAdopcion, s['id_solicitud']) is not None
    aviso = db.scalar(select(Notificacion).where(Notificacion.id_solicitud == s['id_solicitud']))
    assert aviso is not None and 'retirada' not in aviso.mensaje
