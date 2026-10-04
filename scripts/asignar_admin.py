"""Ejecutar en el servidor: python -m scripts.asignar_admin

Asigna el rol al usuario existente indicado expresamente por el propietario.
No crea cuentas, no altera contraseñas y no habilita autoasignación por correo.
"""
from sqlalchemy import select, func
from app.database import SessionLocal
from app.models import Usuario, Administrador

CORREO_ADMIN = "revertlewandosky@gmail.com"


def asignar(db):
    usuarios = db.scalars(select(Usuario).where(
        func.lower(Usuario.correo) == CORREO_ADMIN).with_for_update()).all()
    if len(usuarios) != 1:
        raise ValueError("Debe existir exactamente una cuenta registrada con " + CORREO_ADMIN)
    usuario = usuarios[0]
    if usuario.estado != "ACTIVO":
        raise ValueError("La cuenta debe estar activa antes de asignar el rol")
    existente = db.scalar(select(Administrador).where(Administrador.id_usuario == usuario.id_usuario))
    if existente is None:
        db.add(Administrador(id_usuario=usuario.id_usuario))
    db.commit()
    return usuario.id_usuario


if __name__ == "__main__":
    with SessionLocal() as db:
        try:
            identificador = asignar(db)
        except ValueError as error:
            db.rollback()
            raise SystemExit(str(error)) from None
        print(f"Rol administrador confirmado: {CORREO_ADMIN} (usuario {identificador}).")
