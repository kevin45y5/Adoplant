from unittest.mock import Mock

import httpx
import pytest

from app import correo


def test_mailjet_envia_por_https_sin_exponer_claves(monkeypatch):
    monkeypatch.setenv("MAILJET_API_KEY", "publica-de-prueba")
    monkeypatch.setenv("MAILJET_SECRET_KEY", "secreta-de-prueba")
    monkeypatch.setenv("MAILJET_SENDER_EMAIL", "remitente@example.com")
    respuesta = Mock()
    respuesta.json.return_value = {"Messages": [{"Status": "success"}]}
    enviar = Mock(return_value=respuesta)
    monkeypatch.setattr(correo.httpx, "post", enviar)

    assert correo.correo_configurado()
    correo.enviar_codigo_recuperacion("destino@example.com", "12345678")

    argumentos, opciones = enviar.call_args
    assert argumentos[0] == "https://api.mailjet.com/v3.1/send"
    assert opciones["auth"] == ("publica-de-prueba", "secreta-de-prueba")
    mensaje = opciones["json"]["Messages"][0]
    assert mensaje["To"] == [{"Email": "destino@example.com"}]
    assert "12345678" in mensaje["TextPart"]
    respuesta.raise_for_status.assert_called_once()


def test_mailjet_rechazado_se_trata_como_fallo(monkeypatch):
    monkeypatch.setenv("MAILJET_API_KEY", "publica-de-prueba")
    monkeypatch.setenv("MAILJET_SECRET_KEY", "secreta-de-prueba")
    monkeypatch.setenv("MAILJET_SENDER_EMAIL", "remitente@example.com")
    respuesta = Mock()
    respuesta.json.return_value = {"Messages": [{"Status": "error"}]}
    monkeypatch.setattr(correo.httpx, "post", Mock(return_value=respuesta))
    with pytest.raises(httpx.HTTPError):
        correo.enviar_codigo_recuperacion("destino@example.com", "12345678")
