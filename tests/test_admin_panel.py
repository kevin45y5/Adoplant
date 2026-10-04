import pytest
from contextlib import contextmanager
from sqlalchemy import select, func
from test_admin_usuarios import admin_api, cabecera
from app.database import get_db
from app.main import app
from app.models import Administrador, Usuario
from scripts.asignar_admin import asignar, CORREO_ADMIN


def test_perfil_privado_y_bloqueo_propio(admin_api):
    client, password = admin_api
    assert client.get('/api/admin/me').status_code == 401
    assert client.get('/api/admin/me', headers=cabecera(client,password,2)).status_code == 403
    headers=cabecera(client,password)
    assert client.get('/api/admin/me', headers=headers).json()['administrador'] is True
    assert client.patch('/api/admin/usuarios/1/estado', headers=headers,
                        json={'estado':'BLOQUEADO'}).status_code == 409
    assert client.get('/api/admin/me', headers=headers).status_code == 200


def test_asignacion_exacta_idempotente_y_sin_crear_cuentas(admin_api):
    client, password=admin_api
    with contextmanager(app.dependency_overrides[get_db])() as db:
        with pytest.raises(ValueError):
            asignar(db)
        user=db.get(Usuario,2)
        original_password=user.contrasena
        user.correo=CORREO_ADMIN
        db.commit()
        assert asignar(db)==2
        assert asignar(db)==2
        assert db.scalar(select(func.count()).select_from(Administrador).where(Administrador.id_usuario==2))==1
        assert db.get(Usuario,2).contrasena==original_password
