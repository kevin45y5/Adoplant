import os
import pytest
from sqlalchemy import select
from app.models import Fotografia
from tests.test_integracion_grupal_postgres import grupo, headers

pytestmark = pytest.mark.skipif(os.getenv('SCRUM6_TEST_DB') != '1', reason='PostgreSQL local')

def test_detalle_fotos_estados_y_visibilidad(grupo):
    c, db, datos, _ = grupo
    datos.pop('clave', None)
    auth = headers(datos, 'adoptante')
    id = datos['plantas']['disponible']
    db.add(Fotografia(id_planta=id, url='https://example.com/segunda.jpg'))
    db.commit()
    r = c.get(f'/api/plantas/{id}', headers=auth)
    assert r.status_code == 200
    body = r.json()
    urls = list(db.scalars(select(Fotografia.url).where(Fotografia.id_planta == id).order_by(Fotografia.id_fotografia)))
    assert body['fotografias'] == urls and body['fotografia_url'] == urls[0]
    assert {'categoria', 'tamano', 'nivel_cuidado', 'necesidad_luz', 'necesidad_agua', 'ubicacion', 'descripcion'} <= body.keys()
    assert not {'correo', 'telefono', 'contrasena', 'mensajes', 'latitud', 'longitud'} & body.keys()
    assert body['puede_solicitar']
    assert not c.get(f'/api/plantas/{id}', headers=headers(datos, 'donante')).json()['puede_solicitar']
    for case, state in [('solicitada', 'SOLICITADA'), ('adoptada', 'ADOPTADA')]:
        body = c.get(f"/api/plantas/{datos['plantas'][case]}", headers=auth).json()
        assert body['estado_planta'] == state and not body['puede_solicitar']
    for case in ['oculta', 'eliminada']:
        assert c.get(f"/api/plantas/{datos['plantas'][case]}", headers=auth).status_code == 404
    assert c.get('/api/plantas/2147483647', headers=auth).status_code == 404
