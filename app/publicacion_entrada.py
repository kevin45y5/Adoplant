import json
from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.datastructures import UploadFile

from app.dependencies import obtener_usuario_actual
from app.schemas import PlantaCreate, PlantaUpdate

MAX_FOTOS = 5


@dataclass
class SeleccionFotos:
    archivos: list
    conservar: list[str] | None = None


async def _leer(request, modelo):
    foto = None
    if request.headers.get("content-type", "").startswith("multipart/form-data"):
        formulario = await request.form(max_files=MAX_FOTOS, max_fields=16)
        datos = dict(formulario)
        foto = datos.pop("fotografia", None)
        if foto is not None and not isinstance(foto, UploadFile):
            raise HTTPException(422, "fotografia debe ser un archivo")
        if "fotografias" in datos or "conservar_fotografias" in datos:
            if foto is not None:
                raise HTTPException(422, "Usa fotografia o fotografias, no ambos")
            archivos = formulario.getlist("fotografias")
            datos.pop("fotografias", None)
            if any(not isinstance(f, UploadFile) for f in archivos):
                raise HTTPException(422, "fotografias debe contener archivos")
            conservar = None
            if "conservar_fotografias" in datos:
                try:
                    conservar = json.loads(datos.pop("conservar_fotografias"))
                except (ValueError, TypeError):
                    raise HTTPException(422, "conservar_fotografias debe ser una lista JSON") from None
                if not isinstance(conservar, list) or any(not isinstance(u, str) for u in conservar):
                    raise HTTPException(422, "conservar_fotografias debe ser una lista de URLs existentes")
                if len(conservar) > MAX_FOTOS or len(set(conservar)) != len(conservar):
                    raise HTTPException(422, "La selección de fotografías no es válida")
            foto = SeleccionFotos(archivos, conservar)
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
        if foto is None or (isinstance(foto, SeleccionFotos) and not foto.archivos):
            raise HTTPException(422, "Adjunta una fotografía para publicar la planta")
        if isinstance(foto, SeleccionFotos) and foto.conservar:
            raise HTTPException(422, "Una publicación nueva no tiene fotografías previas")
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
    esquema["properties"]["fotografias"] = {"type": "array", "items": {"type": "string", "format": "binary"}, "maxItems": MAX_FOTOS, "description": "Alternativa múltiple a fotografia. Entre una y cinco fotos por publicación."}
    if foto_obligatoria:
        esquema["anyOf"] = [{"required": ["fotografia"]}, {"required": ["fotografias"]}]
    else:
        esquema["properties"]["conservar_fotografias"] = {"type": "string", "description": "Lista JSON de URLs actuales que se conservarán. Omitir conserva todas; [] las reemplaza por los nuevos archivos."}
    contenido = {"multipart/form-data": {"schema": esquema}}
    if not foto_obligatoria:
        contenido["application/json"] = {"schema": modelo.model_json_schema()}
    return {"requestBody": {"required": True, "content": contenido}}
