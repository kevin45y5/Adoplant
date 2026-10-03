import os
from unittest.mock import Mock
import pytest
from fastapi import HTTPException
from sqlalchemy import select, func
from app.models import Planta, Fotografia
from tests.test_integracion_grupal_postgres import grupo, headers
from tests.test_publicacion_fotos_postgres import datos_publicacion
from tests.test_imagenes import imagen_png

pytestmark = pytest.mark.skipif(os.getenv('SCRUM6_TEST_DB') != '1', reason='PostgreSQL local')

@pytest.fixture
def fotos(grupo, monkeypatch):
    c, db, datos, _ = grupo
    datos.pop('clave', None)
    upload = Mock(side_effect=[(f'https://example.com/{i}.jpg', f'asset-{i}') for i in range(12)])
    cleanup = Mock()
    monkeypatch.setattr('app.routes.plantas.subir_imagen', upload)
    monkeypatch.setattr('app.routes.plantas.eliminar_imagen', cleanup)
    return c, db, datos, upload, cleanup

def files(n):
    return [('fotografias', (f'{i}.png', imagen_png(), 'image/png')) for i in range(n)]

def test_crear_editar_conservar_quitar_y_limites(fotos):
    import json
    c, db, datos, upload, _ = fotos
    auth = headers(datos, 'donante')
    r = c.post('/api/plantas', headers=auth, data=datos_publicacion(db, datos), files=files(3))
    assert r.status_code == 201, r.text
    body = r.json()
    assert len(body['fotografias']) == 3
    route = f"/api/plantas/{body['id_planta']}"
    keep = body['fotografias'][1:]
    r = c.patch(route, headers=auth, data={'conservar_fotografias':json.dumps(keep), 'nombre':'Editada'}, files=files(1))
    assert r.status_code == 200, r.text
    assert r.json()['fotografias'] == keep + ['https://example.com/3.jpg']
    assert r.json()['fotografia_url'] == keep[0]
    before = upload.call_count
    assert c.patch(route, headers=auth, data={'conservar_fotografias':'["https://ajena.example/a.jpg"]'}, files=files(1)).status_code == 422
    assert c.patch(route, headers=auth, files=files(3)).status_code == 422
    assert upload.call_count == before
    # multipart sin archivos para quitar sin agregar
    r = c.patch(route, headers=auth, files={'conservar_fotografias':(None, json.dumps(keep[:1]))})
    assert r.status_code == 200 and r.json()['fotografias'] == keep[:1]
    assert c.patch(route, headers=auth, files={'conservar_fotografias':(None,'[]')}).status_code == 422
    assert c.get(route, headers=auth).json()['fotografias'] == keep[:1]
    assert c.patch(route, headers=headers(datos,'adoptante'), files=files(1)).status_code == 403
    db.get(Planta, body['id_planta']).estado_planta = 'SOLICITADA'
    db.commit()
    assert c.patch(route, headers=auth, files=files(1)).status_code == 403

def test_segunda_foto_invalida_no_sube_ninguna(fotos):
    c, db, datos, upload, _ = fotos
    r = c.post('/api/plantas', headers=headers(datos,'donante'), data=datos_publicacion(db,datos), files=files(1)+[('fotografias',('mala.jpg',b'no es foto','image/jpeg'))])
    assert r.status_code == 422
    upload.assert_not_called()

def test_fallo_segunda_carga_revierte_y_limpia(fotos):
    c, db, datos, upload, cleanup = fotos
    before = db.scalar(select(func.count()).select_from(Planta))
    upload.side_effect = [('https://example.com/a.jpg','a'), HTTPException(502,'Fallo simulado')]
    r = c.post('/api/plantas', headers=headers(datos,'donante'), data=datos_publicacion(db,datos), files=files(2))
    assert r.status_code == 502
    assert db.scalar(select(func.count()).select_from(Planta)) == before
    cleanup.assert_called_once_with('a')

def test_fallo_edicion_conserva_fotos_y_texto(fotos):
    c, db, datos, upload, cleanup = fotos
    auth = headers(datos,'donante')
    route = f"/api/plantas/{datos['plantas']['disponible']}"
    before = c.get(route,headers=auth).json()
    upload.side_effect = [('https://example.com/a.jpg','a'), HTTPException(502,'Fallo simulado')]
    r = c.patch(route, headers=auth, data={'nombre':'No guardar', 'conservar_fotografias':'[]'}, files=files(2))
    assert r.status_code == 502
    after = c.get(route,headers=auth).json()
    assert (after['nombre'],after['fotografias']) == (before['nombre'],before['fotografias'])
    cleanup.assert_called_once_with('a')

def test_maximo_cinco_y_mezcla_rechazada(fotos):
    c, db, datos, upload, _ = fotos
    auth = headers(datos,'donante')
    body = datos_publicacion(db,datos)
    r = c.post('/api/plantas',headers=auth,data=body,files=files(6))
    assert r.status_code in (400,422)
    r = c.post('/api/plantas',headers=auth,data=body,files=files(1)+[('fotografia',('a.png',imagen_png(),'image/png'))])
    assert r.status_code == 422
    upload.assert_not_called()
