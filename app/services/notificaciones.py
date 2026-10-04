from sqlalchemy.orm import Session

from app.models import Notificacion, Planta, SolicitudAdopcion


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


def notificar_decision(db: Session, *, solicitud: SolicitudAdopcion,
                       planta: Planta, estado: str) -> None:
    """Informa al adoptante que el donante respondió su solicitud."""
    aceptada = estado == "ACEPTADA"
    db.add(Notificacion(
        tipo="SOLICITUD_ACEPTADA" if aceptada else "SOLICITUD_RECHAZADA",
        mensaje=(
            f"Tu solicitud para adoptar {planta.nombre} fue aceptada."
            if aceptada else
            f"Tu solicitud para adoptar {planta.nombre} fue rechazada."
        ),
        id_usuario=solicitud.id_adoptante,
        id_planta=planta.id_planta,
        id_solicitud=solicitud.id_solicitud,
    ))
