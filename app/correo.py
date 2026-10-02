"""Entrega códigos de recuperación mediante la API HTTPS de Brevo."""

import os

import httpx


def correo_configurado() -> bool:
    return bool(os.getenv("BREVO_API_KEY") and os.getenv("BREVO_SENDER_EMAIL"))


def enviar_codigo_recuperacion(destinatario: str, codigo: str) -> None:
    """Lanza una excepción si Brevo no acepta el mensaje."""
    remitente = os.environ["BREVO_SENDER_EMAIL"]
    respuesta = httpx.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "api-key": os.environ["BREVO_API_KEY"],
            "accept": "application/json",
        },
        json={
            "sender": {"name": "AdopPlant", "email": remitente},
            "to": [{"email": destinatario}],
            "subject": "Código para recuperar tu cuenta de AdopPlant",
            "textContent": (
                f"Tu código de recuperación es: {codigo}\n\n"
                "Caduca en 15 minutos. Si no lo solicitaste, ignora este mensaje."
            ),
        },
        timeout=10.0,
    )
    respuesta.raise_for_status()
