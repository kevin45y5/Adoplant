"""Añade las peticiones públicas de SCRUM-2 a la colección grupal."""

import json
from pathlib import Path

RUTA = Path(__file__).resolve().parents[1] / "postman" / "AdopPlant_API_grupal_integrada.postman_collection.json"
coleccion = json.loads(RUTA.read_text(encoding="utf-8"))
carpeta = next((parte for parte in coleccion["item"] if parte["name"] == "SCRUM-2 — Recuperación de contraseña"), None)
if carpeta is None:
    carpeta = {"name": "SCRUM-2 — Recuperación de contraseña", "item": []}
    coleccion["item"].insert(2, carpeta)


def peticion(nombre, ruta, cuerpo, descripcion):
    return {
        "name": nombre,
        "request": {
            "method": "POST",
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "body": {"mode": "raw", "raw": json.dumps(cuerpo, ensure_ascii=False, indent=2),
                     "options": {"raw": {"language": "json"}}},
            "url": {"raw": "{{baseUrl}}/api/auth/" + ruta,
                    "host": ["{{baseUrl}}"], "path": ["api", "auth", ruta]},
            "description": descripcion,
        },
        "response": [],
    }


carpeta["item"] = [
    peticion("Solicitar código", "recuperacion",
             {"correo": "correo-registrado@example.com"},
             "SCRUM-2, subtarea 1. Responde 202 de forma genérica. Requiere Brevo configurado en la API. El código llega solo al correo registrado; no se publica en esta colección."),
    peticion("Restablecer contraseña", "restablecer-contrasena",
             {"correo": "correo-registrado@example.com", "codigo": "00000000",
              "nueva_contrasena": "NuevaClave123", "confirmar_contrasena": "NuevaClave123"},
             "SCRUM-2, subtareas 2 y 3. Sustituir correo y código por los de una cuenta de prueba. El código dura 15 minutos y solo se puede usar una vez. Éxito: 200. Inválido, vencido o reutilizado: 400. Contraseña inválida: 422. No guardar ejemplos con códigos reales."),
]
RUTA.write_text(json.dumps(coleccion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
