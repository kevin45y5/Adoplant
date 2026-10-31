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
    with pytest.raises(HTTPException):
        autorizar_chat(db, 999, 1)

def test_c110_05_autorizar_chat_sin_participacion():
    db = MagicMock()
    db.get.side_effect = lambda model, key: None if model.__name__ == 'ChatParticipante' else MagicMock()
    with pytest.raises(HTTPException):
        autorizar_chat(db, 1, 99)

def test_c110_06_autorizar_chat_participante_valido():
    db = MagicMock()
    chat_mock = MagicMock()
    db.get.side_effect = lambda model, key: chat_mock if model.__name__ == 'Chat' else MagicMock()
    res = autorizar_chat(db, 1, 1)
    assert res == chat_mock

def test_c110_07_adopcion_chat_sin_solicitud_aceptada():
    db = MagicMock()
    db.scalar.return_value = None
    db.scalars().first.return_value = None
    chat_mock = MagicMock(id_planta=1)
    res = adopcion_chat(db, chat_mock, False)
    assert res is None

def test_c110_08_adopcion_chat_con_bloqueo():
    db = MagicMock()
    adopcion_mock = MagicMock()
    db.scalar.return_value = adopcion_mock
    db.scalars().first.return_value = adopcion_mock
    chat_mock = MagicMock(id_planta=1)
    res = adopcion_chat(db, chat_mock, True)
    assert res == adopcion_mock

def test_c110_09_exigir_en_proceso_sin_adopcion():
    db = MagicMock()
    chat_mock = MagicMock(id_planta=1)
    db.scalar.return_value = None
    db.scalars().first.return_value = None
    with pytest.raises(HTTPException):
        exigir_en_proceso(db, chat_mock)

def test_c110_10_exigir_en_proceso_estado_incorrecto():
    db = MagicMock()
    chat_mock = MagicMock(id_planta=1)
    adopcion_mock = MagicMock(estado="PENDIENTE")
    db.scalar.return_value = adopcion_mock
    db.scalars().first.return_value = adopcion_mock
    with pytest.raises(HTTPException):
        exigir_en_proceso(db, chat_mock)

def test_c110_11_exigir_en_proceso_exito():
    db = MagicMock()
    chat_mock = MagicMock(id_planta=1)
    adopcion_mock = MagicMock(estado="EN_PROCESO")
    db.scalar.return_value = adopcion_mock
    db.scalars().first.return_value = adopcion_mock
    res = exigir_en_proceso(db, chat_mock)
    assert res == adopcion_mock

def test_c110_12_respuesta_punto_en_proceso_y_propio():
    punto = MagicMock(id_punto=1, id_mensaje=1, latitud=10.0, longitud=10.0, descripcion="Parque Central", mensaje=MagicMock(id_usuario=10))
    res = respuesta_punto(punto, 10, True)
    assert res.puede_editar is True

def test_c110_13_respuesta_punto_en_proceso_y_ajeno():
    punto = MagicMock(id_punto=1, id_mensaje=1, latitud=10.0, longitud=10.0, descripcion="Parque Central", mensaje=MagicMock(id_usuario=10))
    res = respuesta_punto(punto, 99, True)
    assert res.puede_editar is False

def test_c110_14_respuesta_punto_fuera_de_proceso():
    punto = MagicMock(id_punto=1, id_mensaje=1, latitud=10.0, longitud=10.0, descripcion="Parque Central", mensaje=MagicMock(id_usuario=10))
    res = respuesta_punto(punto, 10, False)
    assert res.puede_editar is False
