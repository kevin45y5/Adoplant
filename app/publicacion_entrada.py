import json

from fastapi import Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.datastructures import UploadFile

from app.dependencies import obtener_usuario_actual
from app.schemas import PlantaCreate, PlantaUpdate


async def _leer(request, modelo):
    foto = None
    if request.headers.get("content-type", "").startswith("multipart/form-data"):
        formulario = await request.form(max_files=1, max_fields=15)
        datos = dict(formulario)
        foto = datos.pop("fotografia", None)
        if foto is not None and not isinstance(foto, UploadFile):
            raise HTTPException(422, "fotografia debe ser un archivo")
    else:
        try:
            datos = await request.json()
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise HTTPException(422, "El cuerpo debe ser JSON o un formulario con fotografía") from None
    try:
        datos = modelo.model_validate(datos)
    except ValidationError as error:
        raise RequestValidationError([
            {"loc": ("body", *e["loc"]), "msg": e["msg"], "type": e["type"]}
            for e in error.errors()
        ]) from None
    return datos, foto


async def entrada_crear(request: Request, usuario=Depends(obtener_usuario_actual)):
    try:
        datos, foto = await _leer(request, PlantaCreate)
        if foto is None:
            raise HTTPException(422, "Adjunta una fotografía para publicar la planta")
        yield datos, foto
    finally:
        await request.close()


async def entrada_editar(request: Request, usuario=Depends(obtener_usuario_actual)):
    try:
        yield await _leer(request, PlantaUpdate)
    finally:
        await request.close()


def documentacion_entrada(modelo, foto_obligatoria=False):
    esquema = modelo.model_json_schema()
    esquema["properties"]["fotografia"] = {"type": "string", "format": "binary"}
    if foto_obligatoria:
        esquema.setdefault("required", []).append("fotografia")
    contenido = {"multipart/form-data": {"schema": esquema}}
    if not foto_obligatoria:
        contenido["application/json"] = {"schema": modelo.model_json_schema()}
    return {"requestBody": {"required": True, "content": contenido}}
