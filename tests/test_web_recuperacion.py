from fastapi.testclient import TestClient
from app.main import app


def test_paginas_y_recursos_de_recuperacion():
    with TestClient(app) as client:
        for path in ('/views/index.html', '/views/register.html', '/views/recuperar.html', '/views/recuperar.js', '/views/recuperar.css', '/views/inicio.html', '/views/inicio.js'):
            assert client.get(path).status_code == 200
        assert '/views/recuperar.html' in client.get('/views/index.html').text
        assert client.get('/').json()['mensaje'] == 'La API de AdopPlant está funcionando'


def test_configuracion_render_y_carga_antes_de_formularios():
    with TestClient(app) as client:
        assert 'https://adopplant-api.onrender.com/api' in client.get('/views/config.js').text
        for page, script in [('index', 'main'), ('register', 'main'), ('inicio', 'inicio'), ('recuperar', 'recuperar')]:
            html = client.get(f'/views/{page}.html').text
            assert html.index('/views/config.js') < html.index(f'/views/{script}.js')


def test_cors_local_permite_json_y_token_sin_abrir_cualquier_origen():
    with TestClient(app) as client:
        for origin in ['http://127.0.0.1:8000', 'http://localhost:5500']:
            response = client.options('/api/auth/recuperacion', headers={
                'Origin': origin, 'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'content-type,authorization',
            })
            assert response.status_code == 200
            assert response.headers['access-control-allow-origin'] == origin
            assert 'access-control-allow-credentials' not in response.headers
            error = client.get('/api/usuarios/me', headers={'Origin': origin})
            assert error.status_code == 401
            assert error.headers['access-control-allow-origin'] == origin
        for origin in ['https://otro.example', 'http://localhost.ejemplo.com:8000', 'null']:
            response = client.options('/api/auth/recuperacion', headers={
                'Origin': origin, 'Access-Control-Request-Method': 'POST',
            })
            assert response.status_code == 400
            assert 'access-control-allow-origin' not in response.headers
