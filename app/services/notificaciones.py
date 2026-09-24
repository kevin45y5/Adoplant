"""Operaciones reutilizables para crear notificaciones."""

from sqlalchemy.orm import Session

from app.models import Notificacion


def registrar_notificacion(
    db: Session,
    *,
    id_usuario: int,
    tipo: str,
    mensaje: str,
    id_planta: int | None = None,
    id_solicitud: int | None = None,
) -> Notificacion:
    """Agrega una notificación a la transacción activa, sin hacer commit.

    El llamador conserva el control de commit/rollback para que la notificación
    se confirme junto con la solicitud, aceptación o moderación relacionada.
    """
    notificacion = Notificacion(
        id_usuario=id_usuario,
        tipo=tipo,
        mensaje=mensaje,
        id_planta=id_planta,
        id_solicitud=id_solicitud,
    )
    db.add(notificacion)
    db.flush()
    return notificacion