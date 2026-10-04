import os
import pytest
from sqlalchemy import select, func
from test_solicitudes_postgres import entorno, enviar
from app.models import Notificacion, Planta
from app.security import crear_token_acceso

pytestmark = pytest.mark.skipif(os.getenv('SCRUM6_TEST_DB') != '1', reason='Requiere PostgreSQL local')


@pytest.mark.parametrize('orden', [('donante','adoptante'), ('adoptante','donante')])
def test_confirmaciones_privadas_guardadas_y_notificadas(entorno, orden):
    client, db, datos = entorno
    def headers(rol):
        return {'Authorization':'Bearer '+crear_token_acceso(datos['usuarios'][rol]['id'])}
    solicitud = enviar(entorno).json()
    r = client.patch('/api/solicitudes/'+str(solicitud['id_solicitud'])+'/decision',
                     headers=headers('donante'), json={'estado':'ACEPTADA'})
    assert r.status_code == 200, r.text
    rows = client.get('/api/adopciones', headers=headers('donante')).json()
    a = next(row for row in rows if row['id_solicitud'] == solicitud['id_solicitud'])
    ruta = '/api/adopciones/'+str(a['id_adopcion'])
    assert client.get(ruta, headers=headers('otro')).status_code == 404
    assert client.post(ruta+'/confirmar', headers=headers('otro')).status_code == 404
    assert client.post(ruta+'/confirmar').status_code == 401
    first = client.post(ruta+'/confirmar', headers=headers(orden[0]))
    assert first.status_code == 200, first.text
    assert first.json()['estado'] == 'EN_PROCESO'
    count = db.scalar(select(func.count()).select_from(Notificacion))
    retry = client.post(ruta+'/confirmar', headers=headers(orden[0]))
    assert retry.json() == first.json()
    assert db.scalar(select(func.count()).select_from(Notificacion)) == count
    second = client.post(ruta+'/confirmar', headers=headers(orden[1]))
    assert second.status_code == 200, second.text
    assert second.json()['estado'] == 'COMPLETADA'
    assert second.json()['fecha_entrega'] and second.json()['fecha_recepcion']
    assert db.get(Planta, solicitud['id_planta']).estado == 'ADOPTADA'
    for rol in ('donante','adoptante'):
        notices=client.get('/api/notificaciones', headers=headers(rol)).json()
        assert any(n['tipo']=='ADOPCION_COMPLETADA' for n in notices)
