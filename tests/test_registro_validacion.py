import unittest

from pydantic import ValidationError

from app.schemas import UsuarioRegistro, UsuarioRespuesta


class RegistroValidacionTests(unittest.TestCase):
    def datos(self, **cambios):
        return {
            "nombre": "Ana",
            "apellido": "Lopez",
            "correo": "ana@example.com",
            "telefono": "70000000",
            "contrasena": "Planta123",
            "confirmar_contrasena": "Planta123",
            **cambios,
        }

    def test_registro_valido_y_sin_secretos_en_serializacion(self):
        usuario = UsuarioRegistro(**self.datos())
        self.assertEqual(usuario.nombre, "Ana")
        self.assertNotIn("contrasena", usuario.model_dump())
        self.assertNotIn("confirmar_contrasena", usuario.model_dump())
        self.assertNotIn("contrasena", UsuarioRespuesta.model_fields)

    def test_rechaza_contrasenas_que_no_cumplen_hu1(self):
        for clave in ["Abc1234", "abcdefgh", "12345678"]:
            with self.subTest(clave_tipo=len(clave)), self.assertRaises(ValidationError):
                UsuarioRegistro(**self.datos(contrasena=clave, confirmar_contrasena=clave))

    def test_confirmacion_obligatoria_y_coincidente(self):
        datos = self.datos()
        del datos["confirmar_contrasena"]
        with self.assertRaises(ValidationError):
            UsuarioRegistro(**datos)
        with self.assertRaises(ValidationError):
            UsuarioRegistro(**self.datos(confirmar_contrasena="Otra1234"))

    def test_telefono_obligatorio(self):
        for valor in [None, "", "   "]:
            with self.subTest(valor=valor), self.assertRaises(ValidationError):
                UsuarioRegistro(**self.datos(telefono=valor))
        datos = self.datos()
        del datos["telefono"]
        with self.assertRaises(ValidationError):
            UsuarioRegistro(**datos)

    def test_limpia_datos_pero_conserva_contrasena_exacta(self):
        clave = " Planta123 "
        usuario = UsuarioRegistro(**self.datos(nombre=" Ana ", telefono=" 70000000 ",
                                              contrasena=clave, confirmar_contrasena=clave))
        self.assertEqual(usuario.nombre, "Ana")
        self.assertEqual(usuario.telefono, "70000000")
        self.assertEqual(usuario.contrasena, clave)
        with self.assertRaises(ValidationError):
            UsuarioRegistro(**self.datos(contrasena=clave, confirmar_contrasena=clave.strip()))

    def test_rechaza_correo_invalido_y_nombre_vacio(self):
        for cambios in [{"correo": "invalido"}, {"nombre": "  "}, {"apellido": "  "}]:
            with self.assertRaises(ValidationError):
                UsuarioRegistro(**self.datos(**cambios))


if __name__ == "__main__":
    unittest.main()
