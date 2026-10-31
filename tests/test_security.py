"""SCRUM-111: casos C-111-01 a C-111-10, sin credenciales reales."""
import json
from pathlib import Path
import runpy
import subprocess
import sys
from datetime import datetime, timezone

import jwt
import pytest

from app import security


CLAVE = "secreto-exclusivo-tests-security-" * 4


@pytest.fixture(autouse=True)
def configuracion(monkeypatch):
    monkeypatch.setattr(security, "JWT_SECRET_KEY", CLAVE)
    monkeypatch.setattr(security, "JWT_ACCESS_TOKEN_MINUTES", 30)


@pytest.fixture
def hash_valido():
    return security.crear_hash("Secreto#1")


def test_c111_01_hash_con_sal_y_sin_texto_claro(hash_valido):
    otro = security.crear_hash("Secreto#1")
    assert hash_valido != otro
    assert "Secreto#1" not in hash_valido
    assert "Secreto#1" not in otro


def test_c111_02_contrasena_correcta(hash_valido):
    assert security.verificar_contrasena("Secreto#1", hash_valido) is True


def test_c111_03_contrasena_incorrecta(hash_valido):
    assert security.verificar_contrasena("Secreto#2", hash_valido) is False


def test_c111_04_hash_corrupto_o_vacio(subtests):
    for valor in ("", "hash-corrupto", "$argon2id$v=19$m=65536,t=3,p=4$invalido"):
        with subtests.test(hash=valor):
            assert security.verificar_contrasena("Secreto#1", valor) is False


def decodificar(token):
    return jwt.decode(token, CLAVE, algorithms=["HS256"],
                      options={"require": ["sub", "iat", "exp"]})


def test_c111_05_claims_y_duracion():
    antes = int(datetime.now(timezone.utc).timestamp())
    token = security.crear_token_acceso(7)
    datos = decodificar(token)
    despues = int(datetime.now(timezone.utc).timestamp())
    assert datos["sub"] == "7"
    assert antes <= datos["iat"] <= despues
    # NumericDate expresa segundos; la configuración expresa minutos.
    assert datos["exp"] - datos["iat"] == 30 * 60
    assert datos["exp"] > despues
    assert jwt.get_unverified_header(token)["alg"] == "HS256"


def test_c111_06_tokens_consecutivos_y_usuarios_distintos():
    tokens = [security.crear_token_acceso(7) for _ in range(2)]
    for token in tokens:
        datos = decodificar(token)
        assert datos["sub"] == "7"
        assert datos["exp"] - datos["iat"] == 30 * 60
    otro = security.crear_token_acceso(8)
    assert otro not in tokens
    assert decodificar(otro)["sub"] == "8"


def test_c111_07_firma_correcta_e_incorrecta():
    token = security.crear_token_acceso(7)
    assert decodificar(token)["sub"] == "7"
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(token, "otra-clave-de-prueba-" * 5, algorithms=["HS256"])


def test_c111_08_decodificar_en_otro_proceso():
    token = security.crear_token_acceso(7)
    codigo = (
        "import json,sys,jwt; d=json.load(sys.stdin); "
        "print(json.dumps(jwt.decode(d['token'],d['key'],algorithms=['HS256'])))"
    )
    resultado = subprocess.run(
        [sys.executable, "-c", codigo],
        input=json.dumps({"token": token, "key": CLAVE}),
        capture_output=True, text=True, check=True, timeout=20,
    )
    assert json.loads(resultado.stdout) == decodificar(token)


def importar_con_configuracion(monkeypatch, clave, minutos):
    monkeypatch.setenv("JWT_SECRET_KEY", clave)
    monkeypatch.setenv("JWT_ACCESS_TOKEN_MINUTES", str(minutos))
    monkeypatch.setattr("dotenv.load_dotenv", lambda *args, **kwargs: False)
    return runpy.run_path(str(Path(security.__file__)))


def test_c111_09_rechazar_clave_corta(monkeypatch):
    with pytest.raises(ValueError, match="La clave JWT debe tener al menos 64 caracteres"):
        importar_con_configuracion(monkeypatch, "corta", 30)


def test_c111_10_rechazar_duracion_no_positiva(monkeypatch, subtests):
    for minutos in (0, -1):
        with subtests.test(minutos=minutos):
            with pytest.raises(ValueError, match="La duración del token debe ser mayor que cero"):
                importar_con_configuracion(monkeypatch, CLAVE, minutos)
