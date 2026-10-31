import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock
from app.publicacion_entrada import (
    _leer,
    documentacion_entrada,
    PlantaCreate,
    PlantaUpdate
)

@pytest.mark.asyncio
async def test_c113_01_peticion_json_valida():
    request = MagicMock()
    request.headers = {"content-type": "application/json"}
    request.json = AsyncMock(return_value={"nombre": "Monstera", "categoria_id": 1})
    request.close = AsyncMock()

    datos, fotos = await _leer(request, modelo=PlantaCreate)
    assert datos.nombre == "Monstera"
    assert fotos is None
    request.close.assert_called_once()

@pytest.mark.asyncio
async def test_c113_02_cuerpo_malformado():
    request = MagicMock()
    request.headers = {"content-type": "text/plain"}
    request.close = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await _leer(request, modelo=PlantaCreate)
    
    assert exc_info.value.status_code == 422
    assert "El cuerpo debe ser JSON o un formulario con fotografia" in exc_info.value.detail
    request.close.assert_called_once()

@pytest.mark.asyncio
async def test_c113_03_json_no_cumple_esquema():
    request = MagicMock()
    request.headers = {"content-type": "application/json"}
    request.json = AsyncMock(return_value={"campo_invalido": 123})
    request.close = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await _leer(request, modelo=PlantaCreate)
    
    assert exc_info.value.status_code == 422
    request.close.assert_called_once()

@pytest.mark.asyncio
async def test_c113_04_fotografia_no_es_archivo():
    form_data = {"fotografia": "no_es_un_archivo_upload"}
    request = MagicMock()
    request.headers = {"content-type": "multipart/form-data"}
    request.form = AsyncMock(return_value=form_data)
    request.close = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await _leer(request, modelo=PlantaCreate)
    
    assert exc_info.value.status_code == 422
    assert "fotografia debe ser un archivo" in exc_info.value.detail

@pytest.mark.asyncio
async def test_c113_05_fotografia_y_fotografias_simultaneas():
    foto_mock = MagicMock(filename="foto.jpg")
    form_data = {"fotografia": foto_mock, "fotografias": [foto_mock]}
    request = MagicMock()
    request.headers = {"content-type": "multipart/form-data"}
    request.form = AsyncMock(return_value=form_data)
    request.close = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await _leer(request, modelo=PlantaCreate)
    
    assert exc_info.value.status_code == 422
    assert "Usa fotografia o fotografias, no ambos" in exc_info.value.detail

@pytest.mark.asyncio
async def test_c113_06_fotografias_con_valor_invalido():
    form_data = {"fotografias": ["cadena_no_uploadfile"]}
    request = MagicMock()
    request.headers = {"content-type": "multipart/form-data"}
    request.form = AsyncMock(return_value=form_data)
    request.close = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await _leer(request, modelo=PlantaCreate)
    
    assert exc_info.value.status_code == 422
    assert "fotografias debe contener archivos" in exc_info.value.detail

@pytest.mark.asyncio
async def test_c113_07_conservar_fotografias_json_invalido():
    form_data = {"conservar_fotografias": "{json_invalido}"}
    request = MagicMock()
    request.headers = {"content-type": "multipart/form-data"}
    request.form = AsyncMock(return_value=form_data)
    request.close = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await _leer(request, modelo=PlantaUpdate)
    
    assert exc_info.value.status_code == 422
    assert "conservar_fotografias debe ser una lista JSON" in exc_info.value.detail

@pytest.mark.asyncio
async def test_c113_08_conservar_fotografias_no_es_lista_cadenas():
    form_data = {"conservar_fotografias": "[123, 456]"}
    request = MagicMock()
    request.headers = {"content-type": "multipart/form-data"}
    request.form = AsyncMock(return_value=form_data)
    request.close = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await _leer(request, modelo=PlantaUpdate)
    
    assert exc_info.value.status_code == 422
    assert "conservar_fotografias debe ser una lista de URLs existentes" in exc_info.value.detail

@pytest.mark.asyncio
async def test_c113_09_conservar_fotografias_exceso_o_repetidos():
    urls = '["http://img1.png", "http://img1.png", "http://img2.png", "http://img3.png", "http://img4.png", "http://img5.png"]'
    form_data = {"conservar_fotografias": urls}
    request = MagicMock()
    request.headers = {"content-type": "multipart/form-data"}
    request.form = AsyncMock(return_value=form_data)
    request.close = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await _leer(request, modelo=PlantaUpdate)
    
    assert exc_info.value.status_code == 422
    assert "La selección de fotografías no es válida" in exc_info.value.detail

@pytest.mark.asyncio
async def test_c113_10_entrada_crear_sin_fotografia():
    request = MagicMock()
    request.headers = {"content-type": "application/json"}
    request.json = AsyncMock(return_value={"nombre": "Planta Sin Foto"})
    request.close = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await _leer(request, modelo=PlantaCreate, foto_obligatoria=True)
    
    assert exc_info.value.status_code == 422
    assert "Adjunta una fotografia para publicar la planta" in exc_info.value.detail

@pytest.mark.asyncio
async def test_c113_11_entrada_crear_con_conservar_fotografias():
    form_data = {"conservar_fotografias": '["http://img1.png"]'}
    request = MagicMock()
    request.headers = {"content-type": "multipart/form-data"}
    request.form = AsyncMock(return_value=form_data)
    request.close = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await _leer(request, modelo=PlantaCreate)
    
    assert exc_info.value.status_code == 422
    assert "Una publicación nueva no tiene fotografias previas" in exc_info.value.detail

@pytest.mark.asyncio
async def test_c113_12_entrada_editar_conservar_fotografias_valido():
    form_data = {"conservar_fotografias": '["http://img1.png"]', "nombre": "Planta Editada"}
    request = MagicMock()
    request.headers = {"content-type": "multipart/form-data"}
    request.form = AsyncMock(return_value=form_data)
    request.close = AsyncMock()

    datos, fotos = await _leer(request, modelo=PlantaUpdate)
    assert datos.nombre == "Planta Editada"
    assert fotos == ["http://img1.png"]

def test_c113_13_documentacion_entrada_plantacreate():
    esquema = documentacion_entrada(PlantaCreate, foto_obligatoria=True)
    assert "fotografia" in esquema
    assert esquema["fotografias"]["maxItems"] == 5
    assert "application/json" not in esquema

def test_c113_14_documentacion_entrada_plantaupdate():
    esquema = documentacion_entrada(PlantaUpdate)
    assert "conservar_fotografias" in esquema
    assert "application/json" in esquema

@pytest.mark.asyncio
async def test_c113_15_bloque_finally_libera_recurso():
    request = MagicMock()
    request.headers = {"content-type": "application/json"}
    request.json = AsyncMock(side_effect=Exception("Error lectura"))
    request.close = AsyncMock()

    with pytest.raises(Exception):
        await _leer(request, modelo=PlantaCreate)
    
    request.close.assert_called_once()
