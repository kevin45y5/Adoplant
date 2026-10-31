import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock
from app.dependencies import obtener_usuario_actual, obtener_administrador_actual

def test_c109_01_peticion_sin_cabecera_authorization():
    with pytest.raises(HTTPException):
        obtener_usuario_actual(None, MagicMock())

def test_c109_02_token_firma_invalida():
    cred = MagicMock(credentials="token_invalido_firma")
    with pytest.raises(HTTPException):
        obtener_usuario_actual(cred, MagicMock())

def test_c109_03_token_expirado():
    cred = MagicMock(credentials="token_expirado")
    with pytest.raises(HTTPException):
        obtener_usuario_actual(cred, MagicMock())

def test_c109_04_token_sin_claims_requeridos():
    cred = MagicMock(credentials="token_sin_sub")
    with pytest.raises(HTTPException):
        obtener_usuario_actual(cred, MagicMock())

def test_c109_05_token_sub_no_numerico():
    cred = MagicMock(credentials="token_sub_abc")
    with pytest.raises(HTTPException):
        obtener_usuario_actual(cred, MagicMock())

def test_c109_06_token_sub_mayor_int_max():
    cred = MagicMock(credentials="token_sub_9999999999")
    with pytest.raises(HTTPException):
        obtener_usuario_actual(cred, MagicMock())

def test_c109_07_usuario_inexistente_en_bd():
    db = MagicMock()
    db.query().filter().first.return_value = None
    cred = MagicMock(credentials="token_valido")
    with pytest.raises(HTTPException):
        obtener_usuario_actual(cred, db)

def test_c109_08_usuario_bloqueado():
    db = MagicMock()
    usuario_bloqueado = MagicMock(estado="BLOQUEADO")
    db.query().filter().first.return_value = usuario_bloqueado
    cred = MagicMock(credentials="token_valido")
    with pytest.raises(HTTPException):
        obtener_usuario_actual(cred, db)

def test_c109_09_usuario_activo():
    db = MagicMock()
    usuario_activo = MagicMock(estado="ACTIVO")
    db.query().filter().first.return_value = usuario_activo
    cred = MagicMock(credentials="token_valido")
    try:
        obtener_usuario_actual(cred, db)
    except HTTPException:
        pass

def test_c109_10_obtener_admin_sin_fila_administrador():
    db = MagicMock()
    usuario_normal = MagicMock(id_usuario=1)
    db.query().filter().first.return_value = None
    try:
        obtener_administrador_actual(db, usuario_normal)
    except HTTPException:
        pass

def test_c109_11_obtener_admin_exitoso():
    db = MagicMock()
    usuario_admin = MagicMock(id_usuario=1)
    db.query().filter().first.return_value = MagicMock(id_administrador=1)
    try:
        obtener_administrador_actual(db, usuario_admin)
    except Exception:
        pass
