import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.deps import es_administrador, obtener_usuario_actual
from app.database import get_db
from app.main import app
from app.schemas import (
    ReporteCrear,
    ReporteEstadoActualizar,
    ReporteRespuesta,
)


def _resultado(unico=None, varios=None):
    respuesta = MagicMock()
    respuesta.scalar_one_or_none.return_value = unico
    respuesta.scalars.return_value = respuesta
    respuesta.all.return_value = varios if varios is not None else []
    return respuesta


def _usuario_falso(id_usuario=2, estado="ACTIVO"):
    return SimpleNamespace(id_usuario=id_usuario, estado=estado)


def _reporte_falso(**cambios):
    datos = {
        "id_reporte": 10,
        "motivo": "Contenido inapropiado",
        "estado": "EN_REVISION",
        "fecha_creacion": datetime(2026, 9, 20, tzinfo=timezone.utc),
        "id_reportante": 2,
        "id_reportado": 3,
        "id_administrador": None,
    }
    datos.update(cambios)
    return SimpleNamespace(**datos)


class ReporteRutasTests(unittest.TestCase):
    def test_rutas_reportes_registradas(self):
        paths = app.openapi()["paths"]
        assert "/api/reportes" in paths
        assert "post" in paths["/api/reportes"]
        assert "/api/admin/reportes" in paths
        assert "get" in paths["/api/admin/reportes"]
        assert "/api/admin/reportes/{id_reporte}" in paths
        detalle = paths["/api/admin/reportes/{id_reporte}"]
        assert "get" in detalle
        assert "patch" in detalle


class ReporteEsquemasTests(unittest.TestCase):
    def test_crear_rechaza_motivo_vacio_y_ids_invalidos(self):
        for motivo in ["", "   ", None]:
            with self.subTest(motivo=motivo), self.assertRaises(ValidationError):
                ReporteCrear(id_reportado=3, motivo=motivo)
        for id_reportado in [0, -1]:
            with self.subTest(id_reportado=id_reportado), self.assertRaises(ValidationError):
                ReporteCrear(id_reportado=id_reportado, motivo="Spam")

    def test_crear_limpia_motivo(self):
        datos = ReporteCrear(id_reportado=3, motivo="  Spam  ")
        self.assertEqual(datos.motivo, "Spam")

    def test_estado_se_normaliza_y_vacio_se_rechaza(self):
        datos = ReporteEstadoActualizar(estado="  resuelto ")
        self.assertEqual(datos.estado, "RESUELTO")
        for estado in ["", "   ", None]:
            with self.subTest(estado=estado), self.assertRaises(ValidationError):
                ReporteEstadoActualizar(estado=estado)

    def test_respuesta_no_expone_secretos(self):
        campos = set(ReporteRespuesta.model_fields)
        self.assertNotIn("contrasena", campos)
        self.assertNotIn("hash", campos)
        self.assertIn("id_administrador", campos)


class ReportePermisosTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_rutas_protegidas_sin_token(self):
        self.assertEqual(
            self.client.post(
                "/api/reportes", json={"id_reportado": 3, "motivo": "Spam"}
            ).status_code,
            401,
        )
        self.assertEqual(self.client.get("/api/admin/reportes").status_code, 401)
        self.assertEqual(self.client.get("/api/admin/reportes/1").status_code, 401)
        self.assertEqual(
            self.client.patch(
                "/api/admin/reportes/1", json={"estado": "RESUELTO"}
            ).status_code,
            401,
        )

    def test_rutas_protegidas_token_invalido(self):
        headers = {"Authorization": "Bearer token-invalido"}
        self.assertEqual(
            self.client.post(
                "/api/reportes",
                json={"id_reportado": 3, "motivo": "Spam"},
                headers=headers,
            ).status_code,
            401,
        )
        self.assertEqual(
            self.client.get("/api/admin/reportes", headers=headers).status_code, 401
        )
        self.assertEqual(
            self.client.get("/api/admin/reportes/1", headers=headers).status_code, 401
        )
        self.assertEqual(
            self.client.patch(
                "/api/admin/reportes/1",
                json={"estado": "RESUELTO"},
                headers=headers,
            ).status_code,
            401,
        )


class ReporteCrearTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.db = MagicMock()
        app.dependency_overrides[get_db] = lambda: self.db
        app.dependency_overrides[obtener_usuario_actual] = lambda: _usuario_falso(2)
        self.addCleanup(app.dependency_overrides.clear)

    def test_crear_reporte_valido(self):
        self.db.execute.return_value = _resultado(unico=_usuario_falso(3))

        def _completar(obj):
            obj.id_reporte = 10
            obj.fecha_creacion = datetime(2026, 9, 20, tzinfo=timezone.utc)

        self.db.refresh.side_effect = _completar
        respuesta = self.client.post(
            "/api/reportes", json={"id_reportado": 3, "motivo": "  Spam  "}
        )
        self.assertEqual(respuesta.status_code, 201)
        cuerpo = respuesta.json()
        self.assertEqual(cuerpo["estado"], "EN_REVISION")
        self.assertEqual(cuerpo["id_reportante"], 2)
        self.assertEqual(cuerpo["id_reportado"], 3)
        self.assertEqual(cuerpo["motivo"], "Spam")
        self.assertIsNone(cuerpo["id_administrador"])

    def test_rechaza_autorreporte(self):
        respuesta = self.client.post(
            "/api/reportes", json={"id_reportado": 2, "motivo": "Spam"}
        )
        self.assertEqual(respuesta.status_code, 400)

    def test_rechaza_reportado_inexistente(self):
        self.db.execute.return_value = _resultado(unico=None)
        respuesta = self.client.post(
            "/api/reportes", json={"id_reportado": 99, "motivo": "Spam"}
        )
        self.assertEqual(respuesta.status_code, 404)

    def test_rechaza_motivo_vacio_con_422(self):
        respuesta = self.client.post(
            "/api/reportes", json={"id_reportado": 3, "motivo": "   "}
        )
        self.assertEqual(respuesta.status_code, 422)


class ReporteAdminTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.db = MagicMock()
        app.dependency_overrides[get_db] = lambda: self.db
        app.dependency_overrides[es_administrador] = lambda: _usuario_falso(1)
        self.addCleanup(app.dependency_overrides.clear)

    def test_buscar_reportes(self):
        self.db.execute.return_value = _resultado(
            varios=[_reporte_falso(), _reporte_falso(id_reporte=11)]
        )
        respuesta = self.client.get("/api/admin/reportes")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.json()), 2)

    def test_buscar_rechaza_estado_invalido(self):
        respuesta = self.client.get("/api/admin/reportes", params={"estado": "CERRADO"})
        self.assertEqual(respuesta.status_code, 400)

    def test_detalle_inexistente(self):
        self.db.execute.return_value = _resultado(unico=None)
        respuesta = self.client.get("/api/admin/reportes/99")
        self.assertEqual(respuesta.status_code, 404)

    def test_detalle_existente(self):
        self.db.execute.return_value = _resultado(unico=_reporte_falso())
        respuesta = self.client.get("/api/admin/reportes/10")
        cuerpo = respuesta.json()
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(cuerpo["id_reporte"], 10)
        self.assertEqual(cuerpo["id_reportado"], 3)

    def test_actualizar_estado_resuelve_y_asocia_admin(self):
        reporte = _reporte_falso()
        admin = SimpleNamespace(id_administrador=7, id_usuario=1)
        self.db.execute.side_effect = [
            _resultado(unico=reporte),
            _resultado(unico=admin),
        ]
        respuesta = self.client.patch(
            "/api/admin/reportes/10", json={"estado": "resuelto"}
        )
        self.assertEqual(respuesta.status_code, 200)
        cuerpo = respuesta.json()
        self.assertEqual(cuerpo["estado"], "RESUELTO")
        self.assertEqual(cuerpo["id_administrador"], 7)

    def test_actualizar_rechaza_estado_invalido(self):
        respuesta = self.client.patch(
            "/api/admin/reportes/10", json={"estado": "CERRADO"}
        )
        self.assertEqual(respuesta.status_code, 400)

    def test_actualizar_reporte_inexistente(self):
        self.db.execute.return_value = _resultado(unico=None)
        respuesta = self.client.patch(
            "/api/admin/reportes/99", json={"estado": "RESUELTO"}
        )
        self.assertEqual(respuesta.status_code, 404)


class DependenciasAuthTests(unittest.TestCase):
    def test_sin_token_y_token_invalido_devuelven_401(self):
        from fastapi import HTTPException

        with self.assertRaises(HTTPException) as contexto:
            obtener_usuario_actual(credenciales=None, db=MagicMock())
        self.assertEqual(contexto.exception.status_code, 401)

        credenciales = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="token-invalido"
        )
        with self.assertRaises(HTTPException) as contexto:
            obtener_usuario_actual(credenciales=credenciales, db=MagicMock())
        self.assertEqual(contexto.exception.status_code, 401)

    def test_cuenta_bloqueada_devuelve_403(self):
        from fastapi import HTTPException

        from app.security import crear_token_acceso

        db = MagicMock()
        db.execute.return_value = _resultado(unico=_usuario_falso(5, estado="BLOQUEADO"))
        credenciales = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=crear_token_acceso(5)
        )
        with self.assertRaises(HTTPException) as contexto:
            obtener_usuario_actual(credenciales=credenciales, db=db)
        self.assertEqual(contexto.exception.status_code, 403)

    def test_admin_requiere_relacion_administrador(self):
        from fastapi import HTTPException

        usuario = _usuario_falso(9)
        db = MagicMock()
        db.execute.return_value = _resultado(unico=None)
        with self.assertRaises(HTTPException) as contexto:
            es_administrador(usuario=usuario, db=db)
        self.assertEqual(contexto.exception.status_code, 403)

        db.execute.return_value = _resultado(
            unico=SimpleNamespace(id_administrador=4, id_usuario=9)
        )
        self.assertEqual(es_administrador(usuario=usuario, db=db), usuario)


if __name__ == "__main__":
    unittest.main()
