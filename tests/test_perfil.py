from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

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


def test_edicion_parcial_conserva_datos(perfil):
    cliente, db, token = perfil
    usuario = db.get.return_value
    anteriores = vars(usuario).copy()
    respuesta = cliente.patch(
        "/api/usuarios/me", json={"nombre": " Lucia Maria "},
        headers={"Authorization": "Bearer " + token()},
    )
    assert respuesta.status_code == 200
    assert usuario.nombre == "Lucia Maria"
    for campo, valor in anteriores.items():
        if campo != "nombre":
            assert getattr(usuario, campo) == valor
    assert "contrasena" not in respuesta.json()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(usuario)
    db.get.assert_called_once_with(Usuario, 7)


def test_edicion_normaliza_correo_y_telefono(perfil):
    cliente, db, token = perfil
    respuesta = cliente.patch(
        "/api/usuarios/me",
        json={"correo": " LUCIA.NUEVA@EXAMPLE.COM ", "telefono": " 73334455 ",
              "apellido": " Nuevo "},
        headers={"Authorization": "Bearer " + token()},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["correo"] == "lucia.nueva@example.com"
    assert respuesta.json()["telefono"] == "73334455"
    assert respuesta.json()["apellido"] == "Nuevo"


@pytest.mark.parametrize("datos", [
    {}, {"nombre": "   "}, {"apellido": ""}, {"correo": "incorrecto"},
    {"telefono": ""}, {"nombre": None}, {"correo": None},
    {"apellido": None}, {"telefono": None}, {"nombre": "a" * 101},
    {"apellido": "a" * 101}, {"telefono": "1" * 21},
    {"id_usuario": 8}, {"estado": "BLOQUEADO"}, {"fecha_registro": "2026-01-01"},
    {"permisos": ["admin"]}, {"contrasena": "NoDebeCambiar123!"},
])
def test_edicion_rechaza_datos_sin_modificar_usuario(perfil, datos):
    cliente, db, token = perfil
    anteriores = vars(db.get.return_value).copy()
    respuesta = cliente.patch(
        "/api/usuarios/me", json=datos,
        headers={"Authorization": "Bearer " + token()},
    )
    assert respuesta.status_code == 422
    assert vars(db.get.return_value) == anteriores
    db.commit.assert_not_called()
    assert "NoDebeCambiar123!" not in respuesta.text


@pytest.mark.parametrize("restriccion,mensaje,codigo", [
    ("uq_usuario_correo", "El correo electrónico ya está registrado", 409),
    ("uq_usuario_telefono", "El número de teléfono ya está registrado", 409),
    ("otra", "No se pudo actualizar la cuenta", 500),
])
def test_edicion_maneja_conflictos(perfil, restriccion, mensaje, codigo):
    cliente, db, token = perfil
    error = Exception("detalle interno que no debe exponerse")
    error.diag = SimpleNamespace(constraint_name=restriccion)
    db.commit.side_effect = IntegrityError("UPDATE", {}, error)
    respuesta = cliente.patch(
        "/api/usuarios/me", json={"correo": "ocupado@example.com", "nombre": "Nuevo"},
        headers={"Authorization": "Bearer " + token()},
    )
    assert respuesta.status_code == codigo
    assert respuesta.json() == {"detail": mensaje}
    db.rollback.assert_called_once()
    db.refresh.assert_not_called()


@pytest.mark.parametrize("caso", ["ausente", "invalido", "vencido", "bloqueado"])
def test_edicion_protegida(perfil, caso):
    cliente, db, token = perfil
    headers = {"Authorization": "Bearer " + token(vencido=caso == "vencido")}
    if caso == "ausente":
        headers = {}
    elif caso == "invalido":
        headers = {"Authorization": "Bearer invalido"}
    elif caso == "bloqueado":
        db.get.return_value.estado = "BLOQUEADO"
    respuesta = cliente.patch("/api/usuarios/me", json={"nombre": "Nuevo"}, headers=headers)
    assert respuesta.status_code == (403 if caso == "bloqueado" else 401)
    assert db.get.return_value.nombre == "Lucia"
    db.commit.assert_not_called()
