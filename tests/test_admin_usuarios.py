from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import dependencies, security
from app.database import get_db
from app.main import app
from app.models import Administrador, Usuario


@pytest.fixture
def admin_api(monkeypatch):
    # Base temporal en memoria: nunca utiliza PostgreSQL ni datos del usuario.
    engine = create_engine("sqlite://", poolclass=StaticPool,
                           connect_args={"check_same_thread": False},
                           execution_options={"schema_translate_map": {"public": None}})
    @event.listens_for(engine, "connect")
    def funciones_postgres(conn, record):
        conn.create_function("btrim", 1, lambda valor: valor.strip() if valor is not None else None)

    with engine.begin() as conn:
        conn.exec_driver_sql("CREATE TABLE usuario (id_usuario INTEGER PRIMARY KEY, nombre TEXT, apellido TEXT, correo TEXT, telefono TEXT, contrasena TEXT, estado TEXT, fecha_registro DATETIME)")
        conn.exec_driver_sql("CREATE TABLE administrador (id_administrador INTEGER PRIMARY KEY, id_usuario INTEGER UNIQUE)")
    clave = "clave-exclusiva-de-integracion-" * 4
    monkeypatch.setattr(security, "JWT_SECRET_KEY", clave)
    monkeypatch.setattr(dependencies, "JWT_SECRET_KEY", clave)
    password = "ClaveSoloPruebas123!"
    with Session(engine) as db:
        for identificador, nombre in [(1, "Admin"), (2, "Lucia"), (3, "Otra")]:
            db.add(Usuario(id_usuario=identificador, nombre=nombre, apellido="Prueba",
                           correo=f"persona{identificador}@example.com", telefono=str(70000000+identificador),
                           contrasena=security.crear_hash(password), estado="ACTIVO",
                           fecha_registro=datetime.now(timezone.utc)))
        db.add(Administrador(id_administrador=1, id_usuario=1))
        db.commit()
    def sesion():
        with Session(engine) as db:
            yield db
    anteriores = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = sesion
    try:
        with TestClient(app) as cliente:
            yield cliente, password
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(anteriores)
        engine.dispose()


def cabecera(cliente, password, usuario=1):
    respuesta = cliente.post("/api/auth/login", json={
        "identificador": f"persona{usuario}@example.com", "contrasena": password})
    assert respuesta.status_code == 200
    return {"Authorization": "Bearer " + respuesta.json()["access_token"]}


def test_flujo_administrativo_completo(admin_api):
    cliente, password = admin_api
    admin = cabecera(cliente, password)
    usuario = cabecera(cliente, password, 2)
    for buscar in ["lucia", "PERSONA2@EXAMPLE.COM", "2"]:
        respuesta = cliente.get("/api/admin/usuarios", params={"buscar": buscar}, headers=admin)
        assert respuesta.status_code == 200
        assert respuesta.json()["total"] == 1
        assert respuesta.json()["usuarios"][0]["id_usuario"] == 2
        assert "contrasena" not in respuesta.text
    pagina = cliente.get("/api/admin/usuarios?pagina=2&limite=1", headers=admin).json()
    assert pagina["total"] == 3
    assert pagina["usuarios"][0]["id_usuario"] == 2
    assert cliente.get("/api/admin/usuarios?buscar=%25", headers=admin).json()["total"] == 0
    detalle = cliente.get("/api/admin/usuarios/2", headers=admin).json()
    assert set(detalle) == {"id_usuario", "nombre", "apellido", "correo", "telefono", "estado", "fecha_registro"}
    assert cliente.patch("/api/admin/usuarios/2/estado", json={"estado": "BLOQUEADO"}, headers=admin).status_code == 200
    assert cliente.get("/api/usuarios/me", headers=usuario).status_code == 403
    assert cliente.patch("/api/usuarios/me", json={"nombre": "Cambio"}, headers=usuario).status_code == 403
    assert cliente.post("/api/auth/login", json={"identificador": "persona2@example.com", "contrasena": password}).status_code == 403
    assert cliente.patch("/api/admin/usuarios/2/estado", json={"estado": "ACTIVO"}, headers=admin).status_code == 200
    assert cliente.get("/api/usuarios/me", headers=cabecera(cliente, password, 2)).json() == detalle


def test_permisos_y_validaciones_admin(admin_api):
    cliente, password = admin_api
    admin = cabecera(cliente, password)
    normal = cabecera(cliente, password, 2)
    for ruta in ["/api/admin/usuarios", "/api/admin/usuarios/2"]:
        assert cliente.get(ruta).status_code == 401
        assert cliente.get(ruta, headers=normal).status_code == 403
    assert cliente.patch("/api/admin/usuarios/1/estado", json={"estado": "BLOQUEADO"}, headers=normal).status_code == 403
    for cuerpo in [{}, {"estado": "ELIMINADO"}, {"estado": "ACTIVO", "nombre": "Cambio"}]:
        assert cliente.patch("/api/admin/usuarios/2/estado", json=cuerpo, headers=admin).status_code == 422
    for consulta in ["pagina=0", "limite=101", "limite=0"]:
        assert cliente.get("/api/admin/usuarios?" + consulta, headers=admin).status_code == 422
    assert cliente.get("/api/admin/usuarios/999", headers=admin).status_code == 404
    assert cliente.patch("/api/admin/usuarios/999/estado", json={"estado": "ACTIVO"}, headers=admin).status_code == 404
    # También se impide el uso de un token anterior de un administrador bloqueado.
    assert cliente.patch("/api/admin/usuarios/1/estado", json={"estado": "BLOQUEADO"}, headers=admin).status_code == 200
    assert cliente.get("/api/admin/usuarios", headers=admin).status_code == 403
