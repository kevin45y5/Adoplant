from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import jwt
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app import dependencies
from app.database import get_db
from app.models import Usuario


CLAVE_PRUEBA = "clave-exclusiva-para-pruebas-" * 4


def token_prueba(**cambios):
    ahora = datetime.now(timezone.utc)
    contenido = {
        "sub": "1",
        "iat": ahora,
        "exp": ahora + timedelta(minutes=30),
    }
    contenido.update(cambios)
    return jwt.encode(contenido, CLAVE_PRUEBA, algorithm="HS256")


@pytest.fixture
def entorno(monkeypatch):
    monkeypatch.setattr(dependencies, "JWT_SECRET_KEY", CLAVE_PRUEBA)
    db = Mock()
    db.get.return_value = SimpleNamespace(id_usuario=1, estado="ACTIVO")
    app = FastAPI()
    app.dependency_overrides[get_db] = lambda: db

    # Ruta exclusiva de pruebas: no agrega endpoints a la API del proyecto.
    @app.get("/protegido")
    def protegido(usuario=Depends(dependencies.obtener_usuario_actual)):
        return {"id_usuario": usuario.id_usuario}

    with TestClient(app) as cliente:
        yield cliente, db


def consultar(cliente, token):
    return cliente.get("/protegido", headers={"Authorization": f"Bearer {token}"})


def test_usuario_activo(entorno):
    cliente, db = entorno
    respuesta = consultar(cliente, token_prueba())
    assert respuesta.status_code == 200
    assert respuesta.json() == {"id_usuario": 1}
    db.get.assert_called_once_with(Usuario, 1)


@pytest.mark.parametrize("cabecera", [None, "Basic abc", "Bearer", "Bearer basura"])
def test_cabecera_ausente_o_invalida(entorno, cabecera):
    cliente, db = entorno
    respuesta = cliente.get(
        "/protegido", headers={"Authorization": cabecera} if cabecera else {}
    )
    assert respuesta.status_code == 401
    assert respuesta.headers["www-authenticate"] == "Bearer"
    db.get.assert_not_called()


@pytest.mark.parametrize("caso", ["vencido", "firma", "algoritmo", "sin_exp", "sin_iat", "sin_sub"])
def test_token_no_confiable(entorno, caso):
    cliente, db = entorno
    ahora = datetime.now(timezone.utc)
    contenido = {"sub": "1", "iat": ahora, "exp": ahora + timedelta(minutes=30)}
    clave = CLAVE_PRUEBA
    algoritmo = "HS256"
    if caso == "vencido":
        contenido["exp"] = ahora - timedelta(seconds=60)
    elif caso == "firma":
        clave = "otra-clave-de-pruebas-" * 4
    elif caso == "algoritmo":
        algoritmo = "HS384"
    else:
        del contenido[caso.removeprefix("sin_")]
    token = jwt.encode(contenido, clave, algorithm=algoritmo)
    respuesta = consultar(cliente, token)
    assert respuesta.status_code == 401
    assert respuesta.json() == {"detail": "Token ausente, inválido o vencido"}
    db.get.assert_not_called()


@pytest.mark.parametrize("identificador", ["0", "-1", "abc", "1.5", "2147483648", "9" * 100, 1])
def test_identificador_invalido(entorno, identificador):
    cliente, db = entorno
    assert consultar(cliente, token_prueba(sub=identificador)).status_code == 401
    db.get.assert_not_called()


def test_usuario_inexistente(entorno):
    cliente, db = entorno
    db.get.return_value = None
    assert consultar(cliente, token_prueba()).status_code == 401


def test_bloqueo_invalida_acceso_con_token_previo(entorno):
    cliente, db = entorno
    token = token_prueba()
    assert consultar(cliente, token).status_code == 200
    db.get.return_value.estado = "BLOQUEADO"
    respuesta = consultar(cliente, token)
    assert respuesta.status_code == 403
    assert respuesta.json() == {"detail": "La cuenta está bloqueada"}
    assert db.get.call_count == 2
