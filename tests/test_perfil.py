from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import jwt
import pytest
from fastapi.testclient import TestClient

from app import dependencies
from app.database import get_db
from app.main import app
from app.models import Usuario


@pytest.fixture
def perfil(monkeypatch):
    clave = "clave-solo-para-pruebas-de-perfil-" * 4
    monkeypatch.setattr(dependencies, "JWT_SECRET_KEY", clave)
    ahora = datetime.now(timezone.utc)
    db = Mock()
    db.get.return_value = SimpleNamespace(
        id_usuario=7, nombre="Lucia", apellido="Prueba",
        correo="lucia@example.com", telefono="72223344", estado="ACTIVO",
        fecha_registro=ahora, contrasena="hash-no-publicable",
        permisos=["privado"], recuperacion="no-publicable",
    )
    anteriores = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = lambda: db

    def token(vencido=False):
        return jwt.encode(
            {"sub": "7", "iat": ahora,
             "exp": ahora + timedelta(minutes=-1 if vencido else 30)},
            clave, algorithm="HS256",
        )

    try:
        with TestClient(app) as cliente:
            yield cliente, db, token
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(anteriores)


@pytest.mark.parametrize("consulta", ["", "?id_usuario=8"])
def test_perfil_propio_sin_secretos(perfil, consulta):
    cliente, db, token = perfil
    respuesta = cliente.get(
        "/api/usuarios/me" + consulta,
        headers={"Authorization": "Bearer " + token()},
    )
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert set(datos) == {
        "id_usuario", "nombre", "apellido", "correo", "telefono",
        "estado", "fecha_registro",
    }
    assert datos["id_usuario"] == 7
    db.get.assert_called_once_with(Usuario, 7)


@pytest.mark.parametrize("caso", ["ausente", "invalido", "vencido", "bloqueado", "inexistente"])
def test_perfil_rechaza_acceso(perfil, caso):
    cliente, db, token = perfil
    headers = {"Authorization": "Bearer " + token(vencido=caso == "vencido")}
    if caso == "ausente":
        headers = {}
    elif caso == "invalido":
        headers = {"Authorization": "Bearer invalido"}
    elif caso == "bloqueado":
        db.get.return_value.estado = "BLOQUEADO"
    elif caso == "inexistente":
        db.get.return_value = None
    respuesta = cliente.get("/api/usuarios/me", headers=headers)
    assert respuesta.status_code == (403 if caso == "bloqueado" else 401)
    assert set(respuesta.json()) == {"detail"}


def test_perfil_documentado_con_bearer():
    operacion = app.openapi()["paths"]["/api/usuarios/me"]["get"]
    assert {"HTTPBearer": []} in operacion["security"]
