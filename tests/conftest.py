"""Configuración aislada para ejecutar las pruebas sin credenciales locales."""

import os


# La integración es optativa y utiliza la configuración explícita del entorno/.env.
# Las pruebas unitarias usan dobles o SQLite y no deben cargar secretos reales.
if not any(os.getenv(flag) == "1" for flag in ("SCRUM2_TEST_DB", "SCRUM6_TEST_DB", "SCRUM120_TEST_DB")):
    os.environ.update({
        "DB_USER": "adopplant_test",
        "DB_PASSWORD": "solo-pruebas",
        "DB_HOST": "127.0.0.1",
        "DB_PORT": "1",
        "DB_NAME": "adopplant_test",
        "JWT_SECRET_KEY": "clave-exclusiva-para-pruebas-" * 4,
        "JWT_ACCESS_TOKEN_MINUTES": "30",
    })
