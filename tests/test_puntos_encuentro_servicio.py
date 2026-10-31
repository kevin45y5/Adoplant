import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock
from app.services.puntos_encuentro import (
    autorizar_chat,
    adopcion_chat,
    exigir_en_proceso,
    respuesta_punto
)

def test_c110_04_autorizar_chat_inexistente():
    db = MagicMock()
    db.get.return_value = None

    with pytest.raises(HTTPException) as exc:
        autorizar_chat(db, id_chat=999, id_usuario=1)
    
    assert exc.value.status_code == 404
    assert exc.value.detail == "Chat no encontrado"

def test_c110_05_autorizar_chat_sin_participacion():
    db = MagicMock()
    db.get.side_effect = lambda model, key: None if model.__name__ == 'ChatParticipante' else MagicMock()

    with pytest.raises(HTTPException) as exc:
        autorizar_chat(db, id_chat=1, id_usuario=99)
    
    assert exc.value.status_code == 403
    assert exc.value.detail == "No tienes permiso para consultar este chat"

def test_c110_06_autorizar_chat_participante_valido():
    db = MagicMock()
    chat_mock = MagicMock()
    db.get.side_effect = lambda model, key: chat_mock if model.__name__ == 'Chat' else MagicMock()

    res = autorizar_chat(db, id_chat=1, id_usuario=1)
    assert res == chat_mock

def test_c110_07_adopcion_chat_sin_solicitud_aceptada():
    db = MagicMock()
    db.query().filter().first.return_value = None

    res = adopcion_chat(db, id_chat=1, bloquear=False)
    assert res is None

def test_c110_08_adopcion_chat_con_bloqueo():
    db = MagicMock()
    adopcion_mock = MagicMock()
    db.query().filter().with_for_update().first.return_value = adopcion_mock

    res = adopcion_chat(db, id_chat=1, bloquear=True)
    assert res == adopcion_mock

def test_c110_09_exigir_en_proceso_sin_adopcion():
    with pytest.raises(HTTPException) as exc:
        exigir_en_proceso(adopcion=None)
    
    assert exc.value.status_code == 409
    assert exc.value.detail == "Solo puedes cambiar puntos durante una adopción EN_PROCESO"

def test_c110_10_exigir_en_proceso_estado_incorrecto():
    adopcion = MagicMock(estado="PENDIENTE")
    
    with pytest.raises(HTTPException) as exc:
        exigir_en_proceso(adopcion=adopcion)
    
    assert exc.value.status_code == 409

def test_c110_11_exigir_en_proceso_exito():
    adopcion = MagicMock(estado="EN_PROCESO")
    res = exigir_en_proceso(adopcion=adopcion)
    assert res == adopcion

def test_c110_12_respuesta_punto_en_proceso_y_propio():
    punto = MagicMock(mensaje=MagicMock(id_usuario=10))
    res = respuesta_punto(punto, en_proceso=True, id_usuario=10)
    assert res["puede_editar"] is True

def test_c110_13_respuesta_punto_en_proceso_y_ajeno():
    punto = MagicMock(mensaje=MagicMock(id_usuario=10))
    res = respuesta_punto(punto, en_proceso=True, id_usuario=99)
    assert res["puede_editar"] is False

def test_c110_14_respuesta_punto_fuera_de_proceso():
    punto = MagicMock(mensaje=MagicMock(id_usuario=10))
    res = respuesta_punto(punto, en_proceso=False, id_usuario=10)
    assert res["puede_editar"] is False
