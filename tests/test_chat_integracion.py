"""Chat privado, aceptación real e historial; PostgreSQL local con rollback."""
import os
import pytest
from sqlalchemy import text
from tests.test_integracion_grupal_postgres import grupo, headers  # noqa: F401

pytestmark = pytest.mark.skipif(os.getenv('SCRUM6_TEST_DB') != '1', reason='Requiere PostgreSQL local')


def test_chat_aceptacion_privacidad_paginacion_y_finalizacion(grupo):
    c, db, datos, _ = grupo
    datos.pop('clave', None)
    donor, adopter, outsider = [headers(datos, role) for role in ('donante', 'adoptante', 'otro')]
    plant = datos['plantas']['disponible']
    payload = {'id_planta': plant}
    assert c.post('/api/chats', json=payload, headers=donor).status_code == 403
    request = c.post('/api/solicitudes', json={**payload, 'mensaje': 'Quiero cuidar la planta'}, headers=adopter)
    assert request.status_code == 201
    accepted = c.patch(f"/api/solicitudes/{request.json()['id_solicitud']}", json={'estado': 'ACEPTADA'}, headers=donor)
    assert accepted.status_code == 200, accepted.text
    first = c.post('/api/chats', json=payload, headers=donor)
    assert first.status_code == 201, first.text
    chat = first.json()['id_chat']
    assert len(first.json()['participantes']) == 2
    second = c.post('/api/chats', json=payload, headers=adopter)
    assert second.status_code == 200 and second.json()['id_chat'] == chat
    assert c.post('/api/chats', json=payload, headers=outsider).status_code == 403
    path = f'/api/chats/{chat}/mensajes'
    assert c.get(path, headers=outsider).status_code == 403
    assert c.post(path, json={'contenido': 'No autorizado'}, headers=outsider).status_code == 403
    assert c.post(path, json={'contenido': '   '}, headers=donor).status_code == 422
    assert c.post(path, json={'contenido': 'a' * 2001}, headers=donor).status_code == 422
    ids = []
    for who, message in [(donor, 'Hola'), (adopter, 'Hola, ¿cuándo nos vemos?'), (donor, 'Mañana')]:
        result = c.post(path, json={'contenido': message}, headers=who)
        assert result.status_code == 201, result.text
        ids.append(result.json()['id_mensaje'])
    assert c.get(path + '?pagina=2&tamano_pagina=1', headers=adopter).json()['mensajes'][0]['id_mensaje'] == ids[1]
    incremental = c.get(path + f'?despues_de={ids[0]}', headers=adopter).json()
    assert [m['id_mensaje'] for m in incremental['mensajes']] == ids[1:]
    assert c.get(path + f'?despues_de={ids[-1]}', headers=donor).json()['mensajes'] == []
    assert chat in [x['id_chat'] for x in c.get('/api/chats', headers=adopter).json()]
    assert chat not in [x['id_chat'] for x in c.get('/api/chats', headers=outsider).json()]
    db.execute(text("UPDATE public.adopcion SET estado='COMPLETADA', fecha_entrega=now(), fecha_recepcion=now() WHERE id_planta=:p"), {'p': plant})
    db.commit()
    assert len(c.get(path, headers=adopter).json()['mensajes']) == 3
    assert c.post('/api/chats', json=payload, headers=donor).status_code == 200
    db.execute(text("UPDATE public.usuario SET estado='BLOQUEADO' WHERE id_usuario=:id"), {'id': datos['usuarios']['adoptante']['id']})
    db.commit()
    assert c.get(path, headers=adopter).status_code == 403
