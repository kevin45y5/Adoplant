import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock
from app.dependencies import obtener_usuario_actual, obtener_administrador_actual

def test_c109_01_peticion_sin_cabecera_authorization():
    with pytest.raises(HTTPException) as exc:
        obtener_usuario_actual(token=None, db=MagicMock())
    
    assert exc.value.status_code == 401
    assert exc.value.detail == "Token ausente, inválido o vencido"
    assert exc.value.headers.get("WWW-Authenticate") == "Bearer"

def test_c109_02_token_firma_invalida():
    with pytest.raises(HTTPException) as exc:
        obtener_usuario_actual(token="token_invalido_firma", db=MagicMock())
    assert exc.value.status_code == 401

def test_c109_03_token_expirado():
    with pytest.raises(HTTPException) as exc:
        obtener_usuario_actual(token="token_expirado", db=MagicMock())
    assert exc.value.status_code == 401

def test_c109_04_token_sin_claims_requeridos():
    with pytest.raises(HTTPException) as exc:
        obtener_usuario_actual(token="token_sin_sub_exp_iat", db=MagicMock())
    assert exc.value.status_code == 401

def test_c109_05_token_sub_no_numerico_o_ceros_izquierda():
    with pytest.raises(HTTPException) as exc:
        obtener_usuario_actual(token="token_sub_abc", db=MagicMock())
    assert exc.value.status_code == 401

def test_c109_06_token_sub_mayor_int_max():
    with pytest.raises(HTTPException) as exc:
        obtener_usuario_actual(token="token_sub_9999999999", db=MagicMock())
    assert exc.value.status_code == 401

def test_c109_07_usuario_inexistente_en_bd():
    db = MagicMock()
    db.query().filter().first.return_value = None
    with pytest.raises(HTTPException) as exc:
        obtener_usuario_actual(token="token_valido", db=db)
    assert exc.value.status_code == 401

def test_c109_08_usuario_bloqueado():
    db = MagicMock()
    usuario_bloqueado = MagicMock(estado="BLOQUEADO")
    db.query().filter().first.return_value = usuario_bloqueado

    with pytest.raises(HTTPException) as exc:
        obtener_usuario_actual(token="token_valido", db=db)
    
    assert exc.value.status_code == 403
    assert exc.value.detail == "La cuenta está bloqueada"

def test_c109_09_usuario_activo():
    db = MagicMock()
    usuario_activo = MagicMock(estado="ACTIVO")
    db.query().filter().first.return_value = usuario_activo

    res = obtener_usuario_actual(token="token_valido", db=db)
    assert res == usuario_activo

def test_c109_10_obtener_admin_sin_fila_administrador():
    db = MagicMock()
    usuario_normal = MagicMock(id_usuario=1)
    db.query().filter().first.return_value = None

    with pytest.raises(HTTPException) as exc:
        obtener_administrador_actual(usuario=usuario_normal, db=db)
    
    assert exc.value.status_code == 403
    assert exc.value.detail == "Se requieren permisos de administrador"

def test_c109_11_obtener_admin_exitoso():
    db = MagicMock()
    usuario_admin = MagicMock(id_usuario=1)
    db.query().filter().first.return_value = MagicMock(id_administrador=1)

    res = obtener_administrador_actual(usuario=usuario_admin, db=db)
    assert res == usuario_admin
