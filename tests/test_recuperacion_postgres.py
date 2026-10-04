"""Pruebas de SCRUM-2 contra PostgreSQL local; cada caso revierte sus datos."""

import os
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine, get_db
from app.main import app
from app.models import RecuperacionContrasena, Usuario
from app.routes import auth
from app.security import crear_hash


pytestmark = pytest.mark.skipif(
    os.getenv("SCRUM2_TEST_DB") != "1", reason="Requiere PostgreSQL local"
)

CORREO = "scrum2-prueba@example.com"
ANTERIOR = "Anterior123"
NUEVA = "NuevaClave123"


@pytest.fixture
def recuperacion(monkeypatch):
    correos = []
    monkeypatch.setattr(auth, "correo_configurado", lambda: True)
    monkeypatch.setattr(auth, "enviar_codigo_recuperacion", lambda destino, codigo: correos.append((destino, codigo)))
    with engine.connect() as connection:
        outer = connection.begin()
        with Session(bind=connection, join_transaction_mode="create_savepoint") as db:
            usuario = Usuario(nombre="Prueba", apellido="SCRUM2", correo=CORREO,
                              telefono="79998877", contrasena=crear_hash(ANTERIOR))
            db.add(usuario)
            db.commit()
            anteriores = app.dependency_overrides.copy()
            app.dependency_overrides[get_db] = lambda: db
            try:
                with TestClient(app) as client:
                    yield client, db, usuario, correos
            finally:
                app.dependency_overrides = anteriores
        outer.rollback()


def solicitar(client, correo=CORREO):
    return client.post("/api/auth/recuperacion", json={"correo": correo})


def restablecer(client, codigo, **cambios):
    datos = {"correo": CORREO, "codigo": codigo,
             "nueva_contrasena": NUEVA, "confirmar_contrasena": NUEVA}
    datos.update(cambios)
    return client.post("/api/auth/restablecer-contrasena", json=datos)


def login(client, clave):
    return client.post("/api/auth/login", json={"identificador": CORREO, "contrasena": clave})


def test_flujo_completo_y_reutilizacion(recuperacion):
    client, db, usuario, correos = recuperacion
    assert solicitar(client).status_code == 202
    codigo = correos[0][1]
    registro = db.scalar(select(RecuperacionContrasena).where(RecuperacionContrasena.id_usuario == usuario.id_usuario))
    assert registro.codigo_hash != codigo
    assert codigo not in registro.codigo_hash
    assert login(client, ANTERIOR).status_code == 200
    assert restablecer(client, codigo).status_code == 200
    assert registro.utilizado is True
    assert restablecer(client, codigo).status_code == 400
    assert login(client, ANTERIOR).status_code == 401
    assert login(client, NUEVA).status_code == 200


def test_correo_desconocido_y_limite_de_envios(recuperacion):
    client, db, usuario, correos = recuperacion
    desconocido = solicitar(client, "desconocido@example.com")
    conocido = solicitar(client)
    assert desconocido.status_code == conocido.status_code == 202
    assert desconocido.json() == conocido.json()
    assert len(correos) == 1
    assert solicitar(client).status_code == 202
    assert len(correos) == 1


def test_codigo_incorrecto_y_limite_de_intentos(recuperacion):
    client, db, usuario, correos = recuperacion
    solicitar(client)
    codigo = correos[0][1]
    incorrecto = "00000000" if codigo != "00000000" else "99999999"
    for _ in range(5):
        assert restablecer(client, incorrecto).status_code == 400
    assert restablecer(client, codigo).status_code == 400
    assert login(client, ANTERIOR).status_code == 200


def test_codigo_vencido_y_contrasena_invalida(recuperacion):
    client, db, usuario, correos = recuperacion
    solicitar(client)
    codigo = correos[0][1]
    assert restablecer(client, codigo, nueva_contrasena="soloLetras",
                       confirmar_contrasena="soloLetras").status_code == 422
    assert restablecer(client, codigo, confirmar_contrasena="OtraClave123").status_code == 422
    class RelojAdelantado:
        @staticmethod
        def now(tz):
            return datetime.now(tz) + timedelta(minutes=16)
    from pytest import MonkeyPatch
    # El esquema impide fechas de vencimiento anteriores a la creación.
    with MonkeyPatch.context() as parche:
        parche.setattr(auth, "datetime", RelojAdelantado)
        assert restablecer(client, codigo).status_code == 400
    registro = db.scalar(select(RecuperacionContrasena).where(RecuperacionContrasena.id_usuario == usuario.id_usuario))
    assert registro.utilizado is True


def test_fallo_de_correo_no_deja_codigo_utilizable(recuperacion, monkeypatch):
    import httpx
    client, db, usuario, correos = recuperacion
    def fallar(destino, codigo):
        raise httpx.ConnectError("prueba de fallo")
    monkeypatch.setattr(auth, "enviar_codigo_recuperacion", fallar)
    assert solicitar(client).status_code == 202
    assert db.scalar(select(RecuperacionContrasena).where(RecuperacionContrasena.id_usuario == usuario.id_usuario)) is None


def verificar(client, codigo):
    return client.post('/api/auth/verificar-codigo', json={'correo': CORREO, 'codigo': codigo})


def test_verificacion_rechaza_incorrecto_y_permite_el_del_correo(recuperacion):
    client, db, usuario, correos = recuperacion
    solicitar(client)
    codigo = correos[-1][1]
    incorrecto = '00000000' if codigo != '00000000' else '99999999'
    assert verificar(client, incorrecto).status_code == 400
    assert verificar(client, codigo).status_code == 200
    assert login(client, ANTERIOR).status_code == 200
    assert restablecer(client, codigo).status_code == 200
    assert verificar(client, codigo).status_code == 400


def test_verificacion_comparte_limite_con_restablecimiento(recuperacion):
    client, db, usuario, correos = recuperacion
    solicitar(client)
    codigo = correos[-1][1]
    incorrecto = '00000000' if codigo != '00000000' else '99999999'
    for _ in range(4):
        assert verificar(client, incorrecto).status_code == 400
    assert restablecer(client, incorrecto).status_code == 400
    assert verificar(client, codigo).status_code == 400


def test_verificacion_codigo_vencido(recuperacion, monkeypatch):
    client, db, usuario, correos = recuperacion
    solicitar(client)
    class RelojAdelantado:
        @staticmethod
        def now(tz):
            return datetime.now(tz) + timedelta(minutes=16)
    monkeypatch.setattr(auth, 'datetime', RelojAdelantado)
    assert verificar(client, correos[-1][1]).status_code == 400


def test_reenvio_invalida_codigo_anterior_y_acepta_solo_ultimo(recuperacion, monkeypatch):
    client, db, usuario, correos = recuperacion
    valores = iter([12345678, 87654321])
    monkeypatch.setattr(auth.secrets, 'randbelow', lambda _: next(valores))
    solicitar(client)
    primero = correos[-1][1]
    class RelojReenvio:
        @staticmethod
        def now(tz):
            return datetime.now(tz) + timedelta(minutes=2)
    monkeypatch.setattr(auth, 'datetime', RelojReenvio)
    solicitar(client)
    ultimo = correos[-1][1]
    assert primero != ultimo
    assert verificar(client, primero).status_code == 400
    assert verificar(client, ultimo).status_code == 200
    assert restablecer(client, primero).status_code == 400
    assert restablecer(client, ultimo).status_code == 200


def test_codigo_solo_corresponde_a_su_correo(recuperacion):
    client, db, usuario, correos = recuperacion
    solicitar(client)
    response = client.post('/api/auth/verificar-codigo', json={
        'correo': 'otra-cuenta@example.com', 'codigo': correos[-1][1],
    })
    assert response.status_code == 400
    assert verificar(client, correos[-1][1]).status_code == 200
