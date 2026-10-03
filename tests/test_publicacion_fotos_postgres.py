"""Transacciones locales que se revierten, sin enviar imágenes a Cloudinary."""
import os
from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from sqlalchemy import select, func

from app.models import Planta, Fotografia
from tests.test_integracion_grupal_postgres import grupo, headers
from tests.test_imagenes import imagen_png

pytestmark = pytest.mark.skipif(os.getenv("SCRUM6_TEST_DB") != "1", reason="Requiere PostgreSQL local")


def datos_publicacion(db, datos):
    planta = db.get(Planta, datos["plantas"]["disponible"])
    return dict(nombre="Publicación con foto", tamano="Pequeña", nivel_cuidado="Bajo", estado_salud="Sana", necesidad_luz="Indirecta", necesidad_agua="Semanal", ubicacion="Prueba", id_categoria=planta.id_categoria)


def test_publicar_editar_y_validar_fotos(grupo, monkeypatch):
    c, db, datos, _ = grupo
    auth = headers(datos, "donante")
    body = datos_publicacion(db, datos)
    subir = Mock(return_value=("https://example.com/foto.jpg", "prueba"))
    monkeypatch.setattr("app.routes.plantas.subir_imagen", subir)
    assert c.post("/api/plantas", json=body, headers=auth).status_code == 422
    foto = {"fotografia": ("foto.png", imagen_png(), "application/octet-stream")}
    invalida = {"fotografia": ("foto.png", b"invalido", "image/png")}
    assert c.post("/api/plantas", data=body, files=invalida, headers=auth).status_code == 422
    subir.assert_not_called()
    respuesta = c.post("/api/plantas", data=body, files=foto, headers=auth)
    assert respuesta.status_code == 201, respuesta.text
    planta = respuesta.json()
    assert planta["fotografia_url"] == "https://example.com/foto.jpg"
    assert planta["categoria"]["id_categoria"] == body["id_categoria"]
    assert planta["visible"] and not planta["eliminada"]
    ruta = f'/api/plantas/{planta["id_planta"]}'
    assert c.patch(ruta, json={"nombre": "Actualizada"}, headers=auth).status_code == 200
    subir.return_value = ("https://example.com/nueva.jpg", "otra")
    respuesta = c.patch(ruta, data={"nombre": "Foto nueva"}, files=foto, headers=auth)
    assert respuesta.status_code == 200, respuesta.text
    assert respuesta.json()["fotografia_url"].endswith("nueva.jpg")
    assert c.patch(ruta, json={"id_categoria": None}, headers=auth).status_code == 422
    foto_id = db.scalar(select(Fotografia.id_fotografia).where(Fotografia.id_planta == planta["id_planta"]))
    assert c.delete(f"/api/fotografias/{foto_id}", headers=auth).status_code == 409
    assert c.patch(ruta, data={"nombre": "Ajena"}, files=foto, headers=headers(datos, "adoptante")).status_code == 403
    assert c.patch(ruta, json={"id_usuario": 999}, headers=auth).status_code == 422
    categorias = c.get("/api/categorias").json()
    assert categorias and all(x["estado"] == "ACTIVA" for x in categorias)


def test_fallo_cloudinary_no_crea_planta(grupo, monkeypatch):
    c, db, datos, _ = grupo
    antes = db.scalar(select(func.count()).select_from(Planta))
    monkeypatch.setattr("app.routes.plantas.subir_imagen", Mock(side_effect=HTTPException(502, "Fallo simulado")))
    r = c.post("/api/plantas", headers=headers(datos, "donante"), data=datos_publicacion(db, datos), files={"fotografia": ("foto.png", imagen_png())})
    assert r.status_code == 502
    assert db.scalar(select(func.count()).select_from(Planta)) == antes


def test_fallo_db_limpia_imagen(grupo, monkeypatch):
    c, db, datos, _ = grupo
    body = datos_publicacion(db, datos)
    monkeypatch.setattr("app.routes.plantas.subir_imagen", Mock(return_value=("https://example.com/foto.jpg", "limpiar")))
    limpiar = Mock()
    monkeypatch.setattr("app.routes.plantas.eliminar_imagen", limpiar)
    monkeypatch.setattr(db, "commit", Mock(side_effect=RuntimeError("Fallo simulado")))
    r = c.post("/api/plantas", headers=headers(datos, "donante"), data=body, files={"fotografia": ("foto.png", imagen_png())})
    assert r.status_code == 500
    limpiar.assert_called_once_with("limpiar")
    assert db.scalar(select(Planta).where(Planta.nombre == body["nombre"])) is None


def test_consulta_privada_filtros_y_paginas(grupo):
    c, db, datos, _ = grupo
    auth = headers(datos, "donante")
    retirada = datos["plantas"]["eliminada"]
    ruta = f"/api/plantas/mias/{retirada}"
    r = c.get(ruta, headers=auth)
    assert r.status_code == 200 and r.json()["eliminada"] is True
    assert c.get(ruta, headers=headers(datos, "otro")).status_code == 404
    assert c.get(ruta).status_code == 401
    r = c.get("/api/plantas/mias", headers=auth, params={"retirada": "true"})
    assert [p["id_planta"] for p in r.json()] == [retirada]
    r = c.get("/api/plantas/mias", headers=auth, params={"estado": "SOLICITADA"})
    assert [p["id_planta"] for p in r.json()] == [datos["plantas"]["solicitada"]]
    nombre = db.get(Planta, retirada).nombre
    r = c.get("/api/plantas/mias", headers=auth, params={"busqueda": nombre})
    assert [p["id_planta"] for p in r.json()] == [retirada]
    ids = []
    for pagina in range(1, 4):
        r = c.get("/api/plantas/mias", headers=auth, params={"pagina": pagina, "limite": 2})
        assert r.status_code == 200
        ids.extend(p["id_planta"] for p in r.json())
    assert ids == sorted(datos["plantas"].values(), reverse=True)


@pytest.mark.parametrize("caso", ["solicitada", "adoptada", "oculta", "eliminada"])
def test_estados_impiden_editar_y_retirar(grupo, caso):
    c, db, datos, _ = grupo
    ruta = f'/api/plantas/{datos["plantas"][caso]}'
    auth = headers(datos, "donante")
    assert c.patch(ruta, headers=auth, json={"nombre": "No cambiar"}).status_code == 403
    assert c.delete(ruta, headers=auth).status_code == 403
