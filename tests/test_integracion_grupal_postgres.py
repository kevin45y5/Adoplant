"""SCRUM6_TEST_DB=1: verifica módulos juntos y revierte todos los datos creados."""
import os
from io import BytesIO
from PIL import Image

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import inspect, select, text
from sqlalchemy.orm import Session

from app.database import engine, get_db
from app.main import app
from app.models import Administrador, Base, Notificacion
from app.security import crear_token_acceso
from scripts.preparar_postman import crear_datos

pytestmark = pytest.mark.skipif(os.getenv("SCRUM6_TEST_DB") != "1", reason="Requiere PostgreSQL local")


@pytest.fixture
def grupo():
    with engine.connect() as connection:
        outer = connection.begin()
        with Session(bind=connection, join_transaction_mode="create_savepoint") as db:
            datos = crear_datos(db)
            admin = Administrador(id_usuario=datos["usuarios"]["otro"]["id"])
            db.add(admin)
            db.commit()
            anteriores = app.dependency_overrides.copy()
            app.dependency_overrides[get_db] = lambda: db
            try:
                with TestClient(app) as client:
                    yield client, db, datos, admin
            finally:
                app.dependency_overrides = anteriores
        outer.rollback()


def headers(datos, rol):
    return {"Authorization": "Bearer " + crear_token_acceso(datos["usuarios"][rol]["id"])}


def test_modelos_no_requieren_columnas_nuevas():
    inspector = inspect(engine)
    for table in Base.metadata.sorted_tables:
        existing = {c["name"] for c in inspector.get_columns(table.name, schema="public")}
        assert set(table.columns.keys()) <= existing, table.name


def test_flujo_plantas_solicitudes_notificaciones_y_reportes(grupo, monkeypatch):
    c, db, datos, admin = grupo
    donante, adoptante, administrador = [headers(datos, r) for r in ("donante", "adoptante", "otro")]
    categoria = db.scalar(text("SELECT id_categoria FROM public.planta WHERE id_planta=:id"), {"id": datos["plantas"]["disponible"]})
    body = dict(nombre="Planta integración", tamano="Pequeña", nivel_cuidado="Bajo", estado_salud="Sana", necesidad_luz="Indirecta", necesidad_agua="Moderada", ubicacion="Prueba", id_categoria=categoria)
    imagen = BytesIO()
    Image.new("RGB", (10, 10)).save(imagen, format="PNG")
    monkeypatch.setattr("app.routes.plantas.subir_imagen", lambda contenido: ("https://example.com/principal.jpg", "prueba"))
    r = c.post("/api/plantas/", headers=donante, data=body, files={"fotografia": ("planta.png", imagen.getvalue(), "image/png")})
    assert r.status_code == 201, r.text
    planta = r.json()["id_planta"]
    assert r.json()["estado_planta"] == "DISPONIBLE"
    assert c.get("/api/plantas?estado=INVALIDO").status_code == 422
    assert c.get("/api/plantas").status_code == 200
    assert c.get("/api/plantas/mias", headers=donante).status_code == 200
    assert c.get(f"/api/plantas/{planta}", headers=adoptante).status_code == 200
    assert c.patch(f"/api/plantas/{planta}", headers=adoptante, json={"nombre": "No autorizado"}).status_code == 403
    assert c.patch(f"/api/plantas/{planta}", headers=donante, json={"nombre": "Planta actualizada"}).status_code == 200
    r = c.post("/api/fotografias", headers=donante, json={"id_planta": planta, "url": "https://example.com/prueba.jpg"})
    assert r.status_code == 201, r.text
    foto = r.json()["id_fotografia"]
    assert c.get(f"/api/fotografias?id_planta={planta}").status_code == 200
    assert c.delete(f"/api/fotografias/{foto}", headers=adoptante).status_code == 403
    assert c.delete(f"/api/fotografias/{foto}", headers=donante).status_code == 204
    r = c.post("/api/solicitudes", headers=adoptante, json={"id_planta": planta, "mensaje": "Quiero adoptarla"})
    assert r.status_code == 201, r.text
    solicitud = r.json()["id_solicitud"]
    aviso = db.scalar(select(Notificacion).where(Notificacion.id_solicitud == solicitud))
    assert c.get("/api/notificaciones", headers=donante).status_code == 200
    assert c.get(f"/api/notificaciones/{aviso.id_notificacion}", headers=adoptante).status_code == 404
    r = c.patch(f"/api/notificaciones/{aviso.id_notificacion}", headers=donante)
    assert r.status_code == 200 and r.json()["leida"] is True, r.text
    r = c.post("/api/reportes", headers=adoptante, json={"id_reportado": datos["usuarios"]["donante"]["id"], "motivo": "Reporte de integración"})
    assert r.status_code == 201, r.text
    reporte = r.json()["id_reporte"]
    assert c.get("/api/admin/reportes", headers=adoptante).status_code == 403
    assert c.get("/api/admin/reportes", headers=administrador).status_code == 200
    assert c.get(f"/api/admin/reportes/{reporte}", headers=administrador).status_code == 200
    r = c.patch(f"/api/admin/reportes/{reporte}", headers=administrador, json={"estado": "RESUELTO"})
    assert r.status_code == 200 and r.json()["id_administrador"] == admin.id_administrador, r.text
    assert c.delete(f"/api/plantas/{planta}", headers=donante).status_code == 200
    r = c.get(f"/api/solicitudes/{solicitud}", headers=adoptante)
    assert r.json()["estado"] == "RECHAZADA", r.text
    assert c.get(f"/api/plantas/{planta}", headers=adoptante).status_code == 404


def test_chat_y_moderacion_con_ids_administrativos_distintos(grupo):
    c, db, datos, admin = grupo
    donante, adoptante, administrador = [headers(datos, r) for r in ("donante", "adoptante", "otro")]
    planta = datos["plantas"]["disponible"]
    assert c.post("/api/chats", headers=donante, json={"id_planta": planta}).status_code == 403
    solicitud = c.post("/api/solicitudes", headers=adoptante, json={"id_planta": planta, "mensaje": "Prueba chat"}).json()["id_solicitud"]
    # Fixture transaccional: aún no se integró el módulo que acepta solicitudes.
    db.execute(text("UPDATE public.solicitud_adopcion SET estado='ACEPTADA' WHERE id_solicitud=:id"), {"id": solicitud})
    db.execute(text("INSERT INTO public.adopcion (id_solicitud,id_planta,id_donante,id_adoptante) VALUES (:s,:p,:d,:a)"), {"s": solicitud, "p": planta, "d": datos["usuarios"]["donante"]["id"], "a": datos["usuarios"]["adoptante"]["id"]})
    db.commit()
    r = c.post("/api/chats", headers=donante, json={"id_planta": planta})
    assert r.status_code == 201, r.text
    chat = r.json()["id_chat"]
    assert c.post("/api/chats", headers=administrador, json={"id_planta": planta}).status_code == 403
    assert c.get("/api/chats", headers=adoptante).status_code == 200
    r = c.post(f"/api/chats/{chat}/mensajes", headers=adoptante, json={"contenido": "Hola"})
    assert r.status_code == 201, r.text
    assert c.get(f"/api/chats/{chat}/mensajes", headers=donante).status_code == 200
    assert c.get(f"/api/chats/{chat}/mensajes", headers=administrador).status_code == 403
    assert c.get("/api/admin/plantas", headers=administrador).status_code == 200
    assert c.get(f"/api/admin/plantas/{planta}", headers=administrador).status_code == 200
    r = c.patch(f"/api/admin/plantas/{planta}/moderacion", headers=administrador, json={"motivo": "Prueba", "visible": True, "eliminada": True})
    assert r.status_code == 200, r.text
    assert r.json()["visible"] is False
    assert r.json()["id_administrador_moderador"] == admin.id_administrador
