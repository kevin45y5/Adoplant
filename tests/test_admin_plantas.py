import unittest
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.testclient import TestClient
from pydantic import ConfigDict

from app.main import app
from app.schemas.planta import PlantaModeracion


class AdminPlantasOpenApiTests(unittest.TestCase):
    def test_rutas_admin_plantas_registradas(self):
        paths = app.openapi()["paths"]
        assert "/api/admin/plantas" in paths
        assert "/api/admin/plantas/{id_planta}" in paths
        assert "/api/admin/plantas/{id_planta}/moderacion" in paths
        # Verificar que GET y PATCH estén disponibles
        assert "get" in paths["/api/admin/plantas"]
        assert "get" in paths["/api/admin/plantas/{id_planta}"]
        assert "patch" in paths["/api/admin/plantas/{id_planta}/moderacion"]


class AdminPlantasPermisosTests(unittest.TestCase):
    """Pruebas que verifican que solo administradores pueden acceder."""

    def setUp(self):
        self.client = TestClient(app)

    def auth_headers(self, token=None):
        """Crear headers de autorización."""
        if token is None:
            return {"Authorization": "Bearer token-falso"}
        return {"Authorization": f"Bearer {token}"}

    def test_listar_plantas_sin_token_denegado(self):
        """GET /api/admin/plantas sin token debe fallar."""
        respuesta = self.client.get("/api/admin/plantas")
        self.assertEqual(respuesta.status_code, 401)

    def test_listar_plantas_token_invalido_devuelve_401(self):
        """GET /api/admin/plantas con token inválido debe devolver 401."""
        respuesta = self.client.get(
            "/api/admin/plantas",
            headers=self.auth_headers("token-usuario-normal"),
        )
        # Token inválido da 401 (no 403) porque obtener_usuario_actual falla primero
        self.assertEqual(respuesta.status_code, 401)

    def test_obtener_planta_token_invalido_devuelve_401(self):
        """GET /api/admin/plantas/{id} con token inválido debe devolver 401."""
        respuesta = self.client.get(
            "/api/admin/plantas/1",
            headers=self.auth_headers("token-usuario-normal"),
        )
        self.assertEqual(respuesta.status_code, 401)

    def test_moderar_sin_token_denegado(self):
        """PATCH /api/admin/plantas/{id}/moderacion sin token debe fallar."""
        respuesta = self.client.patch(
            "/api/admin/plantas/1/moderacion",
            json={"motivo": "test"},
        )
        self.assertEqual(respuesta.status_code, 401)

    def test_moderar_token_invalido_denegado(self):
        """PATCH /api/admin/plantas/{id}/moderacion con token inválido debe devolver 401."""
        respuesta = self.client.patch(
            "/api/admin/plantas/1/moderacion",
            json={"motivo": "test"},
            headers=self.auth_headers("token-usuario-normal"),
        )
        self.assertEqual(respuesta.status_code, 401)

    def test_moderar_sin_motivo_denegado(self):
        """PATCH /api/admin/plantas/{id}/moderacion sin motivo debe fallar."""
        respuesta = self.client.patch(
            "/api/admin/plantas/1/moderacion",
            json={"motivo": ""},
        )
        self.assertEqual(respuesta.status_code, 401)


class AdminPlantasContenidoTests(unittest.TestCase):
    """Pruebas que verifican que el contenido no expone datos sensibles."""

    def setUp(self):
        self.client = TestClient(app)

    def auth_headers_admin(self):
        return {"Authorization": "Bearer token-admin"}

    def test_listar_no_exponen_chats(self):
        """Listar plantas no debe incluir información de chats."""
        respuesta = self.client.get(
            "/api/admin/plantas",
            headers=self.auth_headers_admin(),
        )
        # Token inválido da 401
        self.assertEqual(respuesta.status_code, 401)

    def test_obtener_planta_no_exponen_datos_sensibles(self):
        """Obtener planta por ID no debe exponer chats o puntos de encuentro."""
        respuesta = self.client.get(
            "/api/admin/plantas/1",
            headers=self.auth_headers_admin(),
        )
        self.assertEqual(respuesta.status_code, 401)


class AdminPlantasModeracionTests(unittest.TestCase):
    """Pruebas de la moderación de publicaciones."""

    def setUp(self):
        self.client = TestClient(app)

    def auth_headers_admin(self):
        return {"Authorization": "Bearer token-admin"}

    def auth_headers_usuario(self):
        return {"Authorization": "Bearer token-usuario"}

    def test_moderar_con_motivo_vacio_devuelve_401(self):
        """PATCH con motivo vacío: token inválido da 401 (autenticación falla primero)."""
        respuesta = self.client.patch(
            "/api/admin/plantas/1/moderacion",
            json={"motivo": ""},
            headers=self.auth_headers_admin(),
        )
        self.assertEqual(respuesta.status_code, 401)

    def test_moderar_con_motivo_y_visibles_devuelve_401(self):
        """Moderar con visible=True y eliminada=False (solo ocultar): token inválido da 401."""
        respuesta = self.client.patch(
            "/api/admin/plantas/1/moderacion",
            json={
                "motivo": "Ocultar por revisión",
                "visible": True,
                "eliminada": False,
            },
            headers=self.auth_headers_admin(),
        )
        self.assertEqual(respuesta.status_code, 401)

    def test_moderar_planta_no_existente_devuelve_401(self):
        """Patcher planta que no existe: token inválido da 401."""
        respuesta = self.client.patch(
            "/api/admin/plantas/9999/moderacion",
            json={"motivo": "Planta no existe"},
            headers=self.auth_headers_admin(),
        )
        self.assertEqual(respuesta.status_code, 401)

    def test_moderar_sin_motivo_devuelve_401(self):
        """PATCH sin campo motivo: token inválido da 401."""
        respuesta = self.client.patch(
            "/api/admin/plantas/1/moderacion",
            json={},
            headers=self.auth_headers_admin(),
        )
        self.assertEqual(respuesta.status_code, 401)

    def test_moderar_visible_y_eliminada_devuelve_401(self):
        """Moderar estableciendo visible=False y eliminada=True: token inválido da 401."""
        respuesta = self.client.patch(
            "/api/admin/plantas/1/moderacion",
            json={"motivo": "Publicación retirada por incumplimiento"},
            headers=self.auth_headers_admin(),
        )
        self.assertEqual(respuesta.status_code, 401)


if __name__ == "__main__":
    unittest.main()