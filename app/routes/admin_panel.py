from fastapi import APIRouter, Depends
from app.dependencies import obtener_administrador_actual
from app.models import Usuario

router = APIRouter(prefix="/admin", tags=["Administración"])


@router.get("/me")
def perfil_admin(usuario: Usuario = Depends(obtener_administrador_actual)):
    return {"id_usuario": usuario.id_usuario, "nombre": usuario.nombre,
            "correo": usuario.correo, "administrador": True}
