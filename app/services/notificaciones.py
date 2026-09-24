 feature/SCRUM-14-Notificaciones
"""Operaciones reutilizables para crear notificaciones."""


 Main
from sqlalchemy.orm import Session

from app.models import Notificacion


 feature/SCRUM-14-Notificaciones
def registrar_notificacion(
    db: Session,
    *,
    id_usuario: int,
    tipo: str,
    mensaje: str,
    id_planta: int | None = None,
    id_solicitud: int | None = None,
) -> Notificacion:
    """Agrega una notificaci�n a la transacci�n activa, sin hacer commit.

    El llamador conserva el control de commit/rollback para que la notificaci�n
    se confirme junto con la solicitud, aceptaci�n o moderaci�n relacionada.
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

def notificar_solicitud(db: Session, *, id_usuario: int, id_planta: int,
                       id_solicitud: int, nombre_planta: str) -> None:
    """La ruta confirma solicitud y notificación juntas; este servicio no hace commit."""
    db.add(Notificacion(
        tipo="SOLICITUD_ADOPCION",
        mensaje=f"Recibiste una solicitud de adopción para {nombre_planta}.",
        id_usuario=id_usuario,
        id_planta=id_planta,
        id_solicitud=id_solicitud,
    ))
 Main
