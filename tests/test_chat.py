import unittest

from pydantic import ValidationError

from app.main import app
from app.schemas.chat import MensajeCrear


class ChatOpenApiTests(unittest.TestCase):
    def test_rutas_chat_registradas(self):
        paths = app.openapi()["paths"]
        assert "/api/chats" in paths
        assert "post" in paths["/api/chats"]
        assert "get" in paths["/api/chats"]
        assert "/api/chats/{id_chat}/mensajes" in paths


class MensajeValidacionTests(unittest.TestCase):
    def test_rechaza_mensaje_vacio(self):
        for valor in ["", "   "]:
            with self.subTest(valor=valor), self.assertRaises(ValidationError):
                MensajeCrear(contenido=valor)

    def test_acepta_mensaje_con_texto(self):
        mensaje = MensajeCrear(contenido="  Hola  ")
        self.assertEqual(mensaje.contenido, "Hola")
