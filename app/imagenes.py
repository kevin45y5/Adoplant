"""Almacenamiento de imágenes; las credenciales permanecen en el servidor."""
import hashlib
import logging
import os
import time
import uuid
from io import BytesIO

import httpx
from fastapi import HTTPException
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_BYTES = 8 * 1024 * 1024
MAX_PIXELS = 25_000_000
logger = logging.getLogger(__name__)


def preparar_imagen(archivo):
    contenido = archivo.file.read(MAX_BYTES + 1)
    if len(contenido) > MAX_BYTES:
        raise HTTPException(413, "La fotografía no debe superar 8 MB")
    try:
        with Image.open(BytesIO(contenido)) as original:
            if original.format not in {"JPEG", "PNG", "WEBP"}:
                raise ValueError()
            if original.width * original.height > MAX_PIXELS:
                raise ValueError()
            original.verify()
        with Image.open(BytesIO(contenido)) as original:
            imagen = ImageOps.exif_transpose(original).convert("RGB")
            imagen.thumbnail((2000, 2000))
            salida = BytesIO()
            imagen.save(salida, format="JPEG", quality=85)
            return salida.getvalue()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise HTTPException(422, "Adjunta una imagen válida JPG, PNG o WebP de hasta 25 megapíxeles") from None


def _config():
    valores = [os.getenv("CLOUDINARY_" + key, "").strip() for key in ("CLOUD_NAME", "API_KEY", "API_SECRET")]
    if not all(valores):
        raise HTTPException(503, "El almacenamiento de fotografías no está configurado")
    return valores


def _enviar(operacion, parametros, files=None):
    cloud, key, secret = _config()
    parametros = {**parametros, "timestamp": str(int(time.time()))}
    firma = "&".join(f"{k}={v}" for k, v in sorted(parametros.items())) + secret
    parametros.update(api_key=key, signature=hashlib.sha256(firma.encode()).hexdigest())
    with httpx.Client(timeout=30) as client:
        respuesta = client.post(f"https://api.cloudinary.com/v1_1/{cloud}/image/{operacion}", data=parametros, files=files)
        respuesta.raise_for_status()
        return respuesta.json()


def subir_imagen(contenido):
    public_id = "adopplant/" + uuid.uuid4().hex
    try:
        datos = _enviar("upload", {"public_id": public_id}, {"file": ("planta.jpg", contenido, "image/jpeg")})
        url = datos["secure_url"]
        if not isinstance(url, str) or not url.startswith("https://") or len(url) > 500:
            raise ValueError()
        return url, public_id
    except (httpx.HTTPError, KeyError, ValueError):
        eliminar_imagen(public_id)
        raise HTTPException(502, "No se pudo guardar la fotografía. Intenta nuevamente") from None


def eliminar_imagen(public_id):
    """Compensación si la transacción de publicación falla."""
    try:
        _enviar("destroy", {"public_id": public_id})
    except (httpx.HTTPError, ValueError, HTTPException):
        logger.warning("No se pudo limpiar una imagen de una publicación fallida: %s", public_id)
