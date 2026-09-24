"""Ejecutar desde la raíz: python -m scripts.preparar_postman."""
import json
from pathlib import Path
import secrets
from uuid import uuid4

from sqlalchemy import text

from app.database import SessionLocal
from app.models import Usuario
from app.security import crear_hash


def crear_datos(db):
    """Agrega exclusivamente datos nuevos identificados como pruebas SCRUM-6."""
    etiqueta = uuid4().hex[:12]
    clave = secrets.token_urlsafe(20) + "A1"
    usuarios = {}
    for rol in ("donante", "adoptante", "otro", "bloqueado"):
        usuario = Usuario(nombre="Prueba SCRUM-6", apellido=rol,
                          correo=f"scrum6.{rol}.{etiqueta}@example.com",
                          telefono=uuid4().hex[:20], contrasena=crear_hash(clave),
                          estado="BLOQUEADO" if rol == "bloqueado" else "ACTIVO")
        db.add(usuario)
        db.flush()
        usuarios[rol] = {"id": usuario.id_usuario, "correo": usuario.correo}
    categoria = db.execute(text(
        "INSERT INTO public.categoria (nombre) VALUES (:nombre) RETURNING id_categoria"
    ), {"nombre": f"Prueba SCRUM-6 {etiqueta}"}).scalar_one()
    plantas = {}
    for caso, estado, visible, eliminada in (
        ("disponible", "DISPONIBLE", True, False),
        ("solicitada", "SOLICITADA", True, False),
        ("adoptada", "ADOPTADA", True, False),
        ("oculta", "DISPONIBLE", False, False),
        ("eliminada", "DISPONIBLE", False, True),
    ):
        plantas[caso] = db.execute(text("""
            INSERT INTO public.planta
            (nombre, tamano, nivel_cuidado, estado_salud, necesidad_luz,
             necesidad_agua, ubicacion, id_usuario, id_categoria, estado, visible, eliminada)
            VALUES (:nombre, 'Pequeña', 'Bajo', 'Saludable', 'Indirecta', 'Moderada',
                    'Datos de prueba', :dueno, :categoria,
                    CAST(:estado AS public.estado_planta), :visible, :eliminada)
            RETURNING id_planta
        """), {"nombre": f"Prueba SCRUM-6 {caso} {etiqueta}",
               "dueno": usuarios["donante"]["id"], "categoria": categoria,
               "estado": estado, "visible": visible, "eliminada": eliminada}).scalar_one()
    return {"usuarios": usuarios, "plantas": plantas, "clave": clave}


def main():
    salida = Path("postman/SCRUM-6.local.postman_environment.json")
    if salida.exists():
        raise SystemExit("Ya existe el entorno local de Postman. Reutilízalo; no se crearon datos.")
    with SessionLocal() as db:
        datos = crear_datos(db)
        valores = {"base_url": "http://127.0.0.1:8000", "password": datos["clave"],
                   "token": "", "solicitud_id": ""}
        valores.update({f"correo_{rol}": u["correo"] for rol, u in datos["usuarios"].items()})
        valores.update({f"planta_{caso}": str(i) for caso, i in datos["plantas"].items()})
        entorno = {"name": "AdopPlant SCRUM-6 local", "values": [
            {"key": k, "value": v, "enabled": True,
             "type": "secret" if k in ("password", "token") else "default"}
            for k, v in valores.items()], "_postman_variable_scope": "environment"}
        salida.parent.mkdir(exist_ok=True)
        salida.write_text(json.dumps(entorno, ensure_ascii=False, indent=2), encoding="utf-8")
        try:
            db.commit()
        except Exception:
            salida.unlink()
            raise
    print("Datos de prueba creados: 4 usuarios, 1 categoría y 5 plantas.")
    print(f"Importa el entorno local: {salida}")


if __name__ == "__main__":
    main()
