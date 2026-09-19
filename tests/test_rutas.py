from app.main import app


def test_documentacion_publica_usa_prefijo_api():
    paths = app.openapi()["paths"]
    assert "/api/prueba-db" in paths
    assert "/prueba-db" not in paths


def test_alias_anterior_sigue_disponible():
    assert any(route.path == "/prueba-db" for route in app.routes)
