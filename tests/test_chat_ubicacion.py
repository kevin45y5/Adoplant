import json
from datetime import datetime, timezone
from types import SimpleNamespace

from app.routes.chats import _respuesta_mensaje
from app.services.chat_ubicacion import PREFIJO, leer_ubicacion


def test_ambos_participantes_reciben_mapa_y_no_el_texto_interno():
    posicion = dict(kind="live", session="entrega", lat=13.7, lng=-89.2,
                    at=1700000000000, until=1700000900000, label="Parque")
    mensaje = SimpleNamespace(id_mensaje=1, contenido=PREFIJO + json.dumps(posicion),
                              fecha_hora=datetime.now(timezone.utc), tipo="TEXTO",
                              id_chat=8, id_usuario=1, punto=None)
    for participante in (1, 2):
        respuesta = _respuesta_mensaje(mensaje, SimpleNamespace(id_usuario=participante))
        assert respuesta.ubicacion.lat == 13.7
        assert respuesta.ubicacion.lng == -89.2
        assert respuesta.tipo == "UBICACION"
        assert respuesta.punto.latitud == 13.7
        assert respuesta.punto.longitud == -89.2
        assert respuesta.punto.puede_editar is False
        assert PREFIJO not in respuesta.contenido
        assert "https://www.google.com/maps?q=13.7,-89.2" in respuesta.contenido
    mensaje.contenido = PREFIJO + json.dumps(dict(kind="stop", session="entrega"))
    respuesta = _respuesta_mensaje(mensaje, SimpleNamespace(id_usuario=2))
    assert respuesta.ubicacion.kind == "stop"
    assert "finalizada" in respuesta.contenido


def test_no_interpreta_texto_normal_ni_coordenadas_invalidas_como_mapa():
    assert leer_ubicacion("Hola") is None
    assert leer_ubicacion(PREFIJO + "{incorrecto") is None
    assert leer_ubicacion(PREFIJO + json.dumps(dict(kind="live", session="x", lat=99))) is None
