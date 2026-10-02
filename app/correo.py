"""Entrega códigos de recuperación mediante APIs HTTPS de correo."""

import os

import httpx


def correo_configurado() -> bool:
    return bool(
        (os.getenv("MAILJET_API_KEY") and os.getenv("MAILJET_SECRET_KEY")
         and os.getenv("MAILJET_SENDER_EMAIL"))
        or (os.getenv("BREVO_API_KEY") and os.getenv("BREVO_SENDER_EMAIL"))
    )


def enviar_codigo_recuperacion(destinatario: str, codigo: str) -> None:
    """Lanza una excepción si el proveedor no acepta el mensaje."""
    contenido = (
        f"Tu código de recuperación es: {codigo}\n\n"
        "Caduca en 15 minutos. Si no lo solicitaste, ignora este mensaje."
    )
    if (os.getenv("MAILJET_API_KEY") and os.getenv("MAILJET_SECRET_KEY")
            and os.getenv("MAILJET_SENDER_EMAIL")):
        respuesta = httpx.post(
            "https://api.mailjet.com/v3.1/send",
            auth=(os.environ["MAILJET_API_KEY"], os.environ["MAILJET_SECRET_KEY"]),
            json={"Messages": [{
                "From": {"Email": os.environ["MAILJET_SENDER_EMAIL"], "Name": "AdopPlant"},
                "To": [{"Email": destinatario}],
                "Subject": "Código para recuperar tu cuenta de AdopPlant",
                "TextPart": contenido,
            }]},
            timeout=10.0,
        )
        respuesta.raise_for_status()
        if respuesta.json().get("Messages", [{}])[0].get("Status") != "success":
            raise httpx.HTTPError("Mailjet no aceptó el mensaje")
        return

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
            "textContent": contenido,
        },
        timeout=10.0,
    )
    respuesta.raise_for_status()
