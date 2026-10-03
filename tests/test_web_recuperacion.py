from fastapi.testclient import TestClient
from app.main import app


def test_paginas_y_recursos_de_recuperacion():
    with TestClient(app) as client:
        for path in ('/views/index.html', '/views/register.html', '/views/recuperar.html', '/views/recuperar.js', '/views/recuperar.css', '/views/inicio.html', '/views/inicio.js'):
            assert client.get(path).status_code == 200
        assert '/views/recuperar.html' in client.get('/views/index.html').text
        assert client.get('/').json()['mensaje'] == 'La API de AdopPlant está funcionando'
