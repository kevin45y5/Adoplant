from sqlalchemy.orm import Session

from app.models import Notificacion


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
