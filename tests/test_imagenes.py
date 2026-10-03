from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
from fastapi import HTTPException
from PIL import Image

from app import imagenes


def imagen_png():
    salida = BytesIO()
    Image.new("RGB", (12, 12), "green").save(salida, format="PNG")
    return salida.getvalue()


def test_normaliza_foto_y_rechaza_archivo_falso():
    resultado = imagenes.preparar_imagen(SimpleNamespace(file=BytesIO(imagen_png())))
    assert Image.open(BytesIO(resultado)).format == "JPEG"
    with pytest.raises(HTTPException) as error:
        imagenes.preparar_imagen(SimpleNamespace(file=BytesIO(b"esto no es una foto")))
    assert error.value.status_code == 422


def test_limite_tamano():
    with pytest.raises(HTTPException) as error:
        imagenes.preparar_imagen(SimpleNamespace(file=BytesIO(b"x" * (imagenes.MAX_BYTES + 1))))
    assert error.value.status_code == 413


def test_error_proveedor_no_expone_credenciales(monkeypatch):
    monkeypatch.setattr(imagenes, "_enviar", Mock(side_effect=httpx.ConnectError("secreto")))
    with pytest.raises(HTTPException) as error:
        imagenes.subir_imagen(imagen_png())
    assert error.value.status_code == 502
    assert "secreto" not in error.value.detail


def test_configuracion_incompleta(monkeypatch):
    monkeypatch.delenv("CLOUDINARY_API_SECRET", raising=False)
    with pytest.raises(HTTPException) as error:
        imagenes.subir_imagen(imagen_png())
    assert error.value.status_code == 503
