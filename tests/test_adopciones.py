from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from app.routes.adopciones import aplicar_confirmacion


@pytest.mark.parametrize('orden', [(1, 2), (2, 1)])
def test_doble_confirmacion_independiente_e_idempotente(orden):
    adopcion = SimpleNamespace(id_donante=1, id_adoptante=2, fecha_entrega=None,
                               fecha_recepcion=None, estado='EN_PROCESO')
    planta = SimpleNamespace(estado='SOLICITADA')
    ahora = datetime.now(timezone.utc)
    assert aplicar_confirmacion(adopcion, planta, orden[0], ahora)
    assert adopcion.estado == 'EN_PROCESO'
    assert planta.estado == 'SOLICITADA'
    assert (adopcion.fecha_entrega is not None) == (orden[0] == 1)
    assert not aplicar_confirmacion(adopcion, planta, orden[0], ahora)
    assert aplicar_confirmacion(adopcion, planta, orden[1], ahora)
    assert adopcion.estado == 'COMPLETADA'
    assert planta.estado == 'ADOPTADA'
    assert not aplicar_confirmacion(adopcion, planta, orden[1], ahora)


def test_tercero_no_puede_confirmar():
    adopcion = SimpleNamespace(id_donante=1, id_adoptante=2, fecha_entrega=None,
                               fecha_recepcion=None, estado='EN_PROCESO')
    planta = SimpleNamespace(estado='SOLICITADA')
    with pytest.raises(HTTPException) as error:
        aplicar_confirmacion(adopcion, planta, 3, datetime.now(timezone.utc))
    assert error.value.status_code == 404
    assert adopcion.fecha_entrega is None and adopcion.fecha_recepcion is None
