from pydantic import ValidationError

from app.schemas import UbicacionChat

PREFIJO = "[PlantHaven:ubicacion:1]"


def leer_ubicacion(contenido: str | None) -> UbicacionChat | None:
    if not contenido or not contenido.startswith(PREFIJO):
        return None
    try:
        return UbicacionChat.model_validate_json(contenido[len(PREFIJO):])
    except ValidationError:
        return None


def texto_ubicacion(ubicacion: UbicacionChat) -> str:
    if ubicacion.kind == "stop":
        return "Ubicación en tiempo real finalizada."
    titulo = "Ubicación en tiempo real" if ubicacion.kind == "live" else "Punto de encuentro"
    return f"{titulo}: {ubicacion.label}\nhttps://www.google.com/maps?q={ubicacion.lat},{ubicacion.lng}"
