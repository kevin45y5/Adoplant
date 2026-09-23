import secrets
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Planta, Fotografia
from app.schemas import FotografiaRespuesta

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "static" / "fotografias"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

router = APIRouter(prefix="/fotografias", tags=["Fotografías"])


def validar_archivo(file: UploadFile) -> str:
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extensión no permitida: {extension}. Permitidas: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de contenido no permitido: {file.content_type}",
        )

    file_content = file.file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El archivo excede el tamaño máximo de 5MB",
        )

    file.file.seek(0)

    return extension


@router.post("/", response_model=FotografiaRespuesta, status_code=status.HTTP_201_CREATED)
def subir_fotografia(
    foto: UploadFile = File(..., description="Archivo de imagen (jpg, jpeg, png, gif, webp)"),
    id_planta: int = Form(...),
    db: Session = Depends(get_db),
):
    extension = validar_archivo(foto)

    planta = db.execute(
        select(Planta).where(Planta.id_planta == id_planta)
    ).scalar_one_or_none()

    if planta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planta no encontrada",
        )

    nombre_seguro = f"{secrets.token_hex(16)}{extension}"
    ruta_destino = UPLOAD_DIR / nombre_seguro

    with open(ruta_destino, "wb") as buffer:
        buffer.write(foto.file.read())

    url = f"/fotografias/{nombre_seguro}"

    fotografia = Fotografia(
        url=url,
        id_planta=id_planta,
    )
    db.add(fotografia)
    db.commit()
    db.refresh(fotografia)

    return FotografiaRespuesta(
        id_foto=fotografia.id_foto,
        url=fotografia.url,
        fecha_carga=fotografia.fecha_carga,
        id_planta=fotografia.id_planta,
    )


@router.get("/{nombre_archivo}")
def servir_fotografia(nombre_archivo: str):
    ruta = UPLOAD_DIR / nombre_archivo
    if not ruta.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fotografía no encontrada",
        )
    return {"url": f"/fotografias/{nombre_archivo}"}
