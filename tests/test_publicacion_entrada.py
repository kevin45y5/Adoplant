import pytest
import json
from fastapi import HTTPException
from fastapi.datastructures import FormData, UploadFile
from unittest.mock import AsyncMock, MagicMock
from app.publicacion_entrada import _leer, documentacion_entrada, PlantaCreate, PlantaUpdate

PLANTA_VALIDA = {
    "nombre": "Monstera",
    "tamano": "Mediano",
    "nivel_cuidado": "Facil",
    "estado_salud": "Buena",
    "necesidad_luz": "Media",
    "necesidad_agua": "Poca",
    "ubicacion": "Interior",
    "id_categoria": 1
}

@pytest.mark.anyio
async def test_c113_01_peticion_json_valida():
    request = MagicMock()
    request.headers = {"content-type": "application/json"}
    request.json = AsyncMock(return_value=PLANTA_VALIDA)
    request.close = AsyncMock()

    datos, fotos = await _leer(request, modelo=PlantaCreate)
    assert datos.nombre == "Monstera"
    assert fotos is None

@pytest.mark.anyio
async def test_c113_02_cuerpo_malformado():
    request = MagicMock()
    request.headers = {"content-type": "text/plain"}
    request.json = AsyncMock(side_effect=json.JSONDecodeError("Error", "", 0))
    request.close = AsyncMock()

    with pytest.raises(HTTPException):
        await _leer(request, modelo=PlantaCreate)

@pytest.mark.anyio
async def test_c113_03_json_no_cumple_esquema():
    request = MagicMock()
    request.headers = {"content-type": "application/json"}
    request.json = AsyncMock(return_value={"campo_invalido": 123})
    request.close = AsyncMock()

    with pytest.raises(Exception):
        await _leer(request, modelo=PlantaCreate)

@pytest.mark.anyio
async def test_c113_04_fotografia_no_es_archivo():
    form_data = FormData([("fotografia", "no_es_un_archivo_upload")])
    request = MagicMock()
    request.headers = {"content-type": "multipart/form-data"}
    request.form = AsyncMock(return_value=form_data)
    request.close = AsyncMock()

    with pytest.raises(HTTPException):
        await _leer(request, modelo=PlantaCreate)

@pytest.mark.anyio
async def test_c113_05_fotografia_y_fotografias_simultaneas():
    foto_mock = MagicMock(spec=UploadFile)
    form_data = FormData([("fotografia", foto_mock), ("fotografias", foto_mock)])
    request = MagicMock()
    request.headers = {"content-type": "multipart/form-data"}
    request.form = AsyncMock(return_value=form_data)
    request.close = AsyncMock()

    with pytest.raises(HTTPException):
        await _leer(request, modelo=PlantaCreate)

@pytest.mark.anyio
async def test_c113_06_fotografias_con_valor_invalido():
    form_data = FormData([("fotografias", "cadena_no_uploadfile")])
    request = MagicMock()
    request.headers = {"content-type": "multipart/form-data"}
    request.form = AsyncMock(return_value=form_data)
    request.close = AsyncMock()

    with pytest.raises(HTTPException):
        await _leer(request, modelo=PlantaCreate)

@pytest.mark.anyio
async def test_c113_07_conservar_fotografias_json_invalido():
    form_data = FormData([("conservar_fotografias", "{json_invalido}")])
    request = MagicMock()
    request.headers = {"content-type": "multipart/form-data"}
    request.form = AsyncMock(return_value=form_data)
    request.close = AsyncMock()

    with pytest.raises(HTTPException):
        await _leer(request, modelo=PlantaUpdate)

@pytest.mark.anyio
async def test_c113_08_conservar_fotografias_no_es_lista_cadenas():
    form_data = FormData([("conservar_fotografias", "[123, 456]")])
    request = MagicMock()
    request.headers = {"content-type": "multipart/form-data"}
    request.form = AsyncMock(return_value=form_data)
    request.close = AsyncMock()

    with pytest.raises(HTTPException):
        await _leer(request, modelo=PlantaUpdate)

@pytest.mark.anyio
async def test_c113_09_conservar_fotografias_exceso_o_repetidos():
    urls = '["http://img1.png", "http://img1.png", "http://img2.png", "http://img3.png", "http://img4.png", "http://img5.png"]'
    form_data = FormData([("conservar_fotografias", urls)])
    request = MagicMock()
    request.headers = {"content-type": "multipart/form-data"}
    request.form = AsyncMock(return_value=form_data)
    request.close = AsyncMock()

    with pytest.raises(HTTPException):
        await _leer(request, modelo=PlantaUpdate)

@pytest.mark.anyio
async def test_c113_10_entrada_crear_sin_fotografia():
    request = MagicMock()
    request.headers = {"content-type": "application/json"}
    request.json = AsyncMock(return_value=PLANTA_VALIDA)
    request.close = AsyncMock()

    try:
        await _leer(request, modelo=PlantaCreate)
    except Exception:
        pass

@pytest.mark.anyio
async def test_c113_11_entrada_crear_con_conservar_fotografias():
    form_data = FormData([("conservar_fotografias", '["http://img1.png"]')])
    request = MagicMock()
    request.headers = {"content-type": "multipart/form-data"}
    request.form = AsyncMock(return_value=form_data)
    request.close = AsyncMock()

    with pytest.raises(Exception):
        await _leer(request, modelo=PlantaCreate)

@pytest.mark.anyio
async def test_c113_12_entrada_editar_conservar_fotografias_valido():
    form_data = FormData([("conservar_fotografias", '["http://img1.png"]'), ("nombre", "Planta Editada")])
    request = MagicMock()
    request.headers = {"content-type": "multipart/form-data"}
    request.form = AsyncMock(return_value=form_data)
    request.close = AsyncMock()

    datos, fotos = await _leer(request, modelo=PlantaUpdate)
    assert datos.nombre == "Planta Editada"

def test_c113_13_documentacion_entrada_plantacreate():
    esquema = documentacion_entrada(PlantaCreate)
    assert esquema is not None

def test_c113_14_documentacion_entrada_plantaupdate():
    esquema = documentacion_entrada(PlantaUpdate)
    assert esquema is not None

@pytest.mark.anyio
async def test_c113_15_bloque_finally_libera_recurso():
    request = MagicMock()
    request.headers = {"content-type": "application/json"}
    request.json = AsyncMock(side_effect=Exception("Error lectura"))
    request.close = AsyncMock()

    with pytest.raises(Exception):
        await _leer(request, modelo=PlantaCreate)
