"""CRUD privado de puntos sobre PostgreSQL local; datos revertidos al terminar."""
import os
import json
import pytest
from sqlalchemy import text
from tests.test_integracion_grupal_postgres import grupo, headers  # noqa: F401

pytestmark = pytest.mark.skipif(os.getenv('SCRUM6_TEST_DB') != '1', reason='Requiere PostgreSQL local')


@pytest.mark.parametrize("origen_web", [False, True])
def test_puntos_privados_corregir_retirar_y_conservar_al_completar(grupo, origen_web):
    c, db, datos, _ = grupo
    datos.pop('clave', None)
    donor, adopter, outsider = [headers(datos, role) for role in ('donante', 'adoptante', 'otro')]
    plant = datos['plantas']['disponible']
    solicitud = c.post('/api/solicitudes', headers=adopter, json={'id_planta': plant, 'mensaje': 'Quiero cuidarla'}).json()['id_solicitud']
    assert c.patch(f'/api/solicitudes/{solicitud}', headers=donor, json={'estado': 'ACEPTADA'}).status_code == 200
    chat = c.post('/api/chats', headers=donor, json={'id_planta': plant}).json()['id_chat']
    path = f'/api/chats/{chat}/mensajes'
    payload = {'tipo': 'UBICACION', 'latitud': 13.7, 'longitud': -89.7, 'descripcion': 'Parque central'}
    if origen_web:
        payload['contenido'] = '[PlantHaven:ubicacion:1]' + json.dumps({
            'kind': 'live', 'session': 'web-movil', 'lat': 13.7, 'lng': -89.7,
            'label': 'Parque central', 'at': 1700000000000, 'until': 1700000900000,
        })
    assert c.post(path, headers=outsider, json=payload).status_code == 403
    for bad in [{'latitud': 91}, {'longitud': -181}, {'latitud': None}, {'descripcion': 'x' * 256}]:
        assert c.post(path, headers=donor, json={**payload, **bad}).status_code == 422
    assert c.get(path, headers=donor).json()['total'] == 0
    sent = c.post(path, headers=donor, json=payload)
    assert sent.status_code == 201, sent.text
    message = sent.json()
    point = message['punto']['id_punto']
    url = f'/api/puntos-encuentro/{point}'
    assert message['punto']['puede_editar'] is True
    assert c.get(url, headers=adopter).json()['puede_editar'] is False
    assert c.get(url, headers=outsider).status_code == 403
    assert c.get(f'/api/chats/{chat}/puntos', headers=outsider).status_code == 403
    assert c.patch(url, headers=adopter, json={'latitud': 14}).status_code == 403
    assert c.delete(url, headers=adopter).status_code == 403
    assert c.patch(url, headers=donor, json={'latitud': None}).status_code == 422
    assert c.patch(url, headers=donor, json={}).status_code == 422
    changed = c.patch(url, headers=donor, json={'latitud': 14, 'descripcion': 'Entrada norte'})
    assert changed.status_code == 200, changed.text
    current = c.get(path, headers=adopter).json()['mensajes'][0]
    assert current['punto']['latitud'] == 14 and current['punto']['descripcion'] == 'Entrada norte'
    if origen_web:
        assert current['ubicacion']['lat'] == 14
        assert current['ubicacion']['label'] == 'Entrada norte'
        assert '[PlantHaven:ubicacion:1]' not in current['contenido']
    assert (current['id_mensaje'], current['fecha_hora'], current['id_usuario']) == (message['id_mensaje'], message['fecha_hora'], message['id_usuario'])
    assert c.delete(url, headers=donor).status_code == 204
    assert c.get(url, headers=donor).status_code == 404
    assert c.get(f'/api/chats/{chat}/puntos', headers=adopter).json() == []
    withdrawn = c.get(path, headers=adopter).json()['mensajes'][0]
    assert withdrawn['tipo'] == 'TEXTO' and withdrawn['punto'] is None
    assert withdrawn['contenido'] == 'Punto de encuentro retirado por el remitente'
    assert withdrawn['id_mensaje'] == message['id_mensaje'] and withdrawn['fecha_hora'] == message['fecha_hora']
    final_point = c.post(path, headers=adopter, json=payload).json()['punto']['id_punto']
    db.execute(text("UPDATE public.adopcion SET estado='COMPLETADA', fecha_entrega=now(), fecha_recepcion=now() WHERE id_planta=:p"), {'p': plant})
    db.commit()
    final_url = f'/api/puntos-encuentro/{final_point}'
    assert c.get(final_url, headers=adopter).json()['puede_editar'] is False
    assert len(c.get(f'/api/chats/{chat}/puntos', headers=donor).json()) == 1
    assert c.post(path, headers=adopter, json=payload).status_code == 409
    assert c.patch(final_url, headers=adopter, json={'longitud': -90}).status_code == 409
    assert c.delete(final_url, headers=adopter).status_code == 409
    assert c.get(final_url, headers=donor).status_code == 200
