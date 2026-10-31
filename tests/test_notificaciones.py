"""SCRUM-112: mocks, más una comprobación de flush con SQLite en memoria."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models import Notificacion
from app.services.notificaciones import notificar_decision, notificar_solicitud


@pytest.fixture
def db():
    return Mock(spec=Session)


def solicitud(db):
    notificar_solicitud(db, id_usuario=10, id_planta=20,
                       id_solicitud=30, nombre_planta="Orquídea")


def decision(db, estado):
    notificar_decision(
        db, solicitud=SimpleNamespace(id_solicitud=30, id_adoptante=11),
        planta=SimpleNamespace(id_planta=20, nombre="Orquídea", id_usuario=10),
        estado=estado,
    )


def test_c112_01_notificacion_de_solicitud(db):
    solicitud(db)
    db.add.assert_called_once()
    aviso = db.add.call_args.args[0]
    assert isinstance(aviso, Notificacion)
    assert aviso.tipo == "SOLICITUD_ADOPCION"
    assert aviso.mensaje == "Recibiste una solicitud de adopción para Orquídea."
    assert (aviso.id_usuario, aviso.id_planta, aviso.id_solicitud) == (10, 20, 30)


def test_c112_02_no_confirma_transaccion(db):
    solicitud(db)
    db.commit.assert_not_called()
    db.rollback.assert_not_called()


def test_c112_03_aceptada(db):
    decision(db, "ACEPTADA")
    aviso = db.add.call_args.args[0]
    assert aviso.tipo == "SOLICITUD_ACEPTADA"
    assert aviso.mensaje == "Tu solicitud para adoptar Orquídea fue aceptada."
    db.commit.assert_not_called()


def test_c112_04_rechazada(db):
    decision(db, "RECHAZADA")
    aviso = db.add.call_args.args[0]
    assert aviso.tipo == "SOLICITUD_RECHAZADA"
    assert aviso.mensaje == "Tu solicitud para adoptar Orquídea fue rechazada."
    db.commit.assert_not_called()


def test_c112_05_estado_distinto_de_aceptada(db):
    decision(db, "PENDIENTE")
    aviso = db.add.call_args.args[0]
    assert aviso.tipo == "SOLICITUD_RECHAZADA"
    assert aviso.mensaje == "Tu solicitud para adoptar Orquídea fue rechazada."


def test_c112_06_destinatario_es_adoptante(db):
    decision(db, "ACEPTADA")
    aviso = db.add.call_args.args[0]
    assert (aviso.id_usuario, aviso.id_planta, aviso.id_solicitud) == (11, 20, 30)


def test_c112_07_flush_conserva_identificadores():
    # Comprobación de componente complementaria: un Mock no demuestra que flush
    # persista el objeto. SQLite es efímera, sin usar PostgreSQL ni datos reales.
    engine = create_engine("sqlite://", execution_options={
        "schema_translate_map": {"public": None},
    })
    try:
        Notificacion.__table__.create(engine)
        with Session(engine) as db:
            solicitud(db)
            db.flush()
            assert db.in_transaction()
            db.expunge_all()
            aviso = db.scalars(select(Notificacion)).one()
            assert (aviso.id_usuario, aviso.id_planta, aviso.id_solicitud) == (10, 20, 30)
            db.rollback()
            assert db.scalars(select(Notificacion)).all() == []
    finally:
        engine.dispose()


def test_c112_08_notificaciones_independientes(db):
    solicitud(db)
    decision(db, "ACEPTADA")
    assert db.add.call_count == 2
    primera, segunda = [llamada.args[0] for llamada in db.add.call_args_list]
    assert primera is not segunda
    assert primera.tipo == "SOLICITUD_ADOPCION"
    assert segunda.tipo == "SOLICITUD_ACEPTADA"
    assert primera.id_usuario == 10
    assert segunda.id_usuario == 11
    db.commit.assert_not_called()
