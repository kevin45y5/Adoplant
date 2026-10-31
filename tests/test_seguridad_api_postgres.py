"""SCRUM-120: siete escenarios de seguridad de la API Python local.

Opt-in: SCRUM120_TEST_DB=1 y DB_NAME=adopplant_test. Se revierten los datos.
No ejecuta peticiones contra Render ni valida la API C#.
"""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, func, select
from sqlalchemy.orm import Session

from app import dependencies, security
from app.database import engine, get_db
from app.main import app
from app.models import Administrador, Notificacion, Usuario
from app.routes import auth


pytestmark = pytest.mark.skipif(os.getenv("SCRUM120_TEST_DB") != "1",
                                reason="Requiere PostgreSQL local de pruebas")
CLAVE = "scrum120-clave-ficticia-solo-pruebas-" * 4
PASSWORD = "SoloPruebas120!"


@pytest.fixture
def api_segura(monkeypatch, request):
    assert engine.url.host in ("localhost", "127.0.0.1", "::1")
    assert engine.url.database == "adopplant_test", "Solo base desechable adopplant_test"
    monkeypatch.setattr(security, "JWT_SECRET_KEY", CLAVE)
    monkeypatch.setattr(dependencies, "JWT_SECRET_KEY", CLAVE)
    monkeypatch.setattr(auth, "JWT_SECRET_KEY", CLAVE)
    monkeypatch.setattr(auth, "correo_configurado", lambda: True)
    # Nunca se envían correos a servicios externos.
    monkeypatch.setattr(auth, "enviar_codigo_recuperacion", lambda *args: None)
    registros = []
    def registrar(respuesta):
        respuesta.read()
        cuerpo = respuesta.json()
        if isinstance(cuerpo, dict) and "access_token" in cuerpo:
            cuerpo = {**cuerpo, "access_token": "[OMITIDO]"}
        registros.append({"caso": request.node.name,
                          "metodo": respuesta.request.method,
                          "ruta": respuesta.request.url.raw_path.decode(),
                          "estado": respuesta.status_code,
                          "www_authenticate": respuesta.headers.get("www-authenticate"),
                          "respuesta": cuerpo})
    with engine.connect() as conexion:
        transaccion = conexion.begin()
        anteriores = app.dependency_overrides.copy()
        try:
            with Session(bind=conexion, join_transaction_mode="create_savepoint") as db:
                sufijo = uuid4().hex[:12]
                usuarios = []
                hash_clave = security.crear_hash(PASSWORD)
                for i, rol in enumerate(("admin", "usuario", "otro")):
                    u = Usuario(nombre=rol, apellido="SCRUM120", correo=f"{rol}-{sufijo}@example.com",
                                telefono=f"120{i}{sufijo}", contrasena=hash_clave)
                    db.add(u)
                    usuarios.append(u)
                db.flush()
                db.add(Administrador(id_usuario=usuarios[0].id_usuario))
                aviso = Notificacion(tipo="SOLICITUD_ADOPCION", mensaje="Aviso privado SCRUM120",
                                     id_usuario=usuarios[2].id_usuario)
                db.add(aviso)
                db.commit()
                app.dependency_overrides[get_db] = lambda: db
                with TestClient(app, raise_server_exceptions=False) as cliente:
                    cliente.event_hooks["response"].append(registrar)
                    yield SimpleNamespace(client=cliente, db=db, usuarios=usuarios, aviso=aviso,
                                          conexion=conexion)
        finally:
            app.dependency_overrides.clear()
            app.dependency_overrides.update(anteriores)
            transaccion.rollback()
            salida = os.getenv("SCRUM120_LOG_DIR")
            if salida:
                destino = Path(salida)
                destino.mkdir(parents=True, exist_ok=True)
                (destino / (request.node.name + ".json")).write_text(
                    json.dumps(registros, ensure_ascii=False, indent=2), encoding="utf-8")


def bearer(usuario, **cambios):
    ahora = datetime.now(timezone.utc)
    datos = {"sub": str(usuario.id_usuario), "iat": ahora, "exp": ahora + timedelta(minutes=30)}
    datos.update(cambios)
    return {"Authorization": "Bearer " + jwt.encode(datos, CLAVE, algorithm="HS256")}


def login(entorno, identificador, contrasena=PASSWORD):
    return entorno.client.post("/api/auth/login", json={
        "identificador": identificador, "contrasena": contrasena,
    })


def test_csec_01_sin_token(api_segura):
    for ruta in ("/api/usuarios/me", "/api/admin/usuarios", "/api/notificaciones"):
        r = api_segura.client.get(ruta)
        assert r.status_code == 401
        assert r.headers["www-authenticate"] == "Bearer"
        assert r.json() == {"detail": "Token ausente, inválido o vencido"}


def test_csec_02_firma_invalida_y_payload_modificado(api_segura):
    usuario = api_segura.usuarios[1]
    original = bearer(usuario)["Authorization"].split()[1]
    partes = original.split(".")
    import base64
    payload = json.loads(base64.urlsafe_b64decode(partes[1] + "=" * (-len(partes[1]) % 4)))
    payload["sub"] = str(api_segura.usuarios[0].id_usuario)
    partes[1] = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    falso = jwt.encode(payload, "otra-clave-ficticia-" * 5, algorithm="HS256")
    for token in (".".join(partes), falso):
        r = api_segura.client.get("/api/usuarios/me", headers={"Authorization": "Bearer " + token})
        assert r.status_code == 401
        assert r.json() == {"detail": "Token ausente, inválido o vencido"}


def test_csec_03_token_expirado(api_segura):
    ahora = datetime.now(timezone.utc)
    r = api_segura.client.get("/api/usuarios/me", headers=bearer(
        api_segura.usuarios[1], iat=ahora-timedelta(hours=2), exp=ahora-timedelta(hours=1)))
    assert r.status_code == 401
    assert r.headers["www-authenticate"] == "Bearer"


def test_csec_04_roles_administracion_python(api_segura):
    # Adaptación Python; NO acredita /api/metricas de C#.
    for indice, esperado in ((1, 403), (0, 200)):
        r = api_segura.client.get("/api/admin/usuarios", headers=bearer(api_segura.usuarios[indice]))
        assert r.status_code == esperado
        assert "contrasena" not in r.text and "$argon2" not in r.text


def test_csec_05_intentos_repetidos_sin_filtracion(api_segura):
    # Diez intentos acotados; prueba de mensajes, no de carga ni rate limiting.
    for _ in range(5):
        for correo in (api_segura.usuarios[1].correo, "ausente-scrum120@example.com"):
            r = login(api_segura, correo, "Incorrecta120!")
            assert r.status_code == 401
            assert r.json() == {"detail": "Credenciales inválidas"}
    assert login(api_segura, api_segura.usuarios[1].correo).status_code == 200


def test_csec_06_inyeccion_sql_parametrizada(api_segura):
    ataques = ("' OR '1'='1' --", "x@example.com' OR 1=1 --", "'; SELECT 1; --")
    sentencias = []
    def observar(conn, cursor, statement, parameters, context, executemany):
        sentencias.append((statement, parameters))
    total = api_segura.db.scalar(select(func.count()).select_from(Usuario))
    event.listen(api_segura.conexion, "before_cursor_execute", observar)
    try:
        for ataque in ataques:
            inicio = len(sentencias)
            r = login(api_segura, ataque)
            assert r.status_code == 401
            assert r.json() == {"detail": "Credenciales inválidas"}
            valor_consultado = ataque.lower() if "@" in ataque else ataque
            assert any(isinstance(params, dict) and valor_consultado in params.values()
                       for _, params in sentencias[inicio:])
            assert all(ataque not in sql for sql, _ in sentencias[inicio:])
            r = api_segura.client.get("/api/admin/usuarios", params={"buscar": ataque},
                                      headers=bearer(api_segura.usuarios[0]))
            assert r.status_code == 200
            assert r.json()["usuarios"] == []
            assert "Traceback" not in r.text and "psycopg" not in r.text
    finally:
        event.remove(api_segura.conexion, "before_cursor_execute", observar)
    assert api_segura.db.scalar(select(func.count()).select_from(Usuario)) == total


def test_csec_07_enumeracion_login_recuperacion_y_recursos(api_segura):
    existente = api_segura.usuarios[1].correo
    inexistente = "ausente-scrum120@example.com"
    respuestas = [login(api_segura, correo, "Incorrecta120!") for correo in (existente, inexistente)]
    assert [(r.status_code, r.json()) for r in respuestas] == [
        (401, {"detail": "Credenciales inválidas"})] * 2
    respuestas = [api_segura.client.post("/api/auth/recuperacion", json={"correo": correo})
                  for correo in (existente, inexistente)]
    assert [(r.status_code, r.json()) for r in respuestas] == [
        (202, {"mensaje": auth.MENSAJE_RECUPERACION})] * 2
    cabecera = bearer(api_segura.usuarios[1])
    for identificador in (api_segura.aviso.id_notificacion, 2147483647):
        r = api_segura.client.get(f"/api/notificaciones/{identificador}", headers=cabecera)
        assert r.status_code == 404
        assert r.json() == {"detail": "Notificacion no encontrada"}
    r = api_segura.client.get(f"/api/notificaciones/{api_segura.aviso.id_notificacion}",
                              headers=bearer(api_segura.usuarios[2]))
    assert r.status_code == 200
