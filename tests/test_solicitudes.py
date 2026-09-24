import pytest
from pydantic import ValidationError

from app.schemas import SolicitudCrear


@pytest.mark.parametrize("mensaje", ["", "   ", "a" * 501])
def test_mensaje_invalido(mensaje):
    with pytest.raises(ValidationError):
        SolicitudCrear(id_planta=1, mensaje=mensaje)


def test_limite_y_limpieza():
    assert SolicitudCrear(id_planta=1, mensaje="a" * 500).mensaje == "a" * 500
    assert SolicitudCrear(id_planta=1, mensaje="  Quiero cuidarla  ").mensaje == "Quiero cuidarla"


@pytest.mark.parametrize("datos", [
    {"id_planta": 0}, {"id_planta": True}, {"id_planta": 2147483648},
    {"id_adoptante": 10}, {"estado": "ACEPTADA"},
])
def test_rechaza_identificadores_y_campos_ajenos(datos):
    with pytest.raises(ValidationError):
        SolicitudCrear(**({"id_planta": 1, "mensaje": "La cuidaré"} | datos))
