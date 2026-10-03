from typing import List, Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, text, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Categoria, Fotografia, Planta, Usuario
from app.schemas import CatalogoResponse, CategoriaRespuesta, PlantaCreate, PlantaRespuesta, PlantaUpdate
from app.dependencies import obtener_usuario_actual
from app.imagenes import preparar_imagen, subir_imagen, eliminar_imagen
from app.publicacion_entrada import entrada_crear, entrada_editar, documentacion_entrada, SeleccionFotos, MAX_FOTOS

router = APIRouter(prefix="/plantas", tags=["Plantas"])


def _planta_a_respuesta(db: Session, planta: Planta, usuario: Usuario | None = None) -> PlantaRespuesta:
    datos = PlantaRespuesta.model_validate(planta).model_dump()
    fotos = db.scalars(select(Fotografia).where(Fotografia.id_planta == planta.id_planta).order_by(Fotografia.id_fotografia)).all()
    url = fotos[0].url if fotos else None
    datos["fotografias"] = [foto.url for foto in fotos]
    puede = planta.estado_planta == "DISPONIBLE" and not planta.eliminada and (usuario is None or planta.id_usuario != usuario.id_usuario)
    datos["fotografia_url"] = url
    datos["puede_solicitar"] = puede
    categoria = db.get(Categoria, planta.id_categoria)
    datos["categoria"] = CategoriaRespuesta.model_validate(categoria) if categoria else None
    return PlantaRespuesta(**datos)


@router.get("", response_model=CatalogoResponse)
def catalogo(
    db: Session = Depends(get_db),
    busqueda: Optional[str] = Query(None, max_length=100),
    estado: Optional[Literal["DISPONIBLE", "SOLICITADA", "ADOPTADA"]] = Query(None),
    tamano: Optional[str] = Query(None, min_length=1, max_length=50),
    nivel_cuidado: Optional[str] = Query(None, min_length=1, max_length=50),
    categoria: Optional[str] = Query(None, min_length=1, max_length=100),
    ubicacion: Optional[str] = Query(None, min_length=1, max_length=150),
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
):
    condiciones = (Planta.eliminada == False, Planta.visible == True, Planta.estado_planta == "DISPONIBLE")
    consulta = select(Planta).where(*condiciones)
    if busqueda and busqueda.strip():
        consulta = consulta.where(Planta.nombre.icontains(busqueda.strip(), autoescape=True))
    if estado:
        consulta = consulta.where(Planta.estado_planta == estado)
    for valor, columna in [(tamano, Planta.tamano), (nivel_cuidado, Planta.nivel_cuidado), (ubicacion, Planta.ubicacion)]:
        if valor is not None:
            if not valor.strip():
                raise HTTPException(422, "El filtro no puede estar vacío")
            consulta = consulta.where(func.lower(func.trim(columna)) == valor.strip().lower())
    if categoria is not None:
        if not categoria.strip():
            raise HTTPException(422, "La categoría no puede estar vacía")
        consulta = consulta.join(Categoria, Planta.id_categoria == Categoria.id_categoria).where(func.lower(func.trim(Categoria.nombre)) == categoria.strip().lower())
    offset = (pagina - 1) * limite
    total = db.scalar(select(func.count()).select_from(consulta.subquery()))
    plantas = db.scalars(consulta.order_by(Planta.fecha_publicacion.desc(), Planta.id_planta.desc()).offset(offset).limit(limite)).all()
    filtros = {}
    for nombre, columna in [("tamano", Planta.tamano), ("nivel_cuidado", Planta.nivel_cuidado), ("ubicacion", Planta.ubicacion)]:
        filtros[nombre] = sorted({v.strip() for v in db.scalars(select(columna).where(*condiciones).distinct()) if v and v.strip()})
    filtros["categoria"] = sorted(set(db.scalars(select(Categoria.nombre).select_from(Categoria).join(Planta, Planta.id_categoria == Categoria.id_categoria).where(*condiciones).distinct())))
    return CatalogoResponse(total=total, pagina=pagina, limite=limite,
        plantas=[_planta_a_respuesta(db, p) for p in plantas],
        hay_mas=offset + len(plantas) < total, filtros=filtros)


@router.get("/mias", response_model=List[PlantaRespuesta])
def consultar_mias(
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
    busqueda: Optional[str] = Query(None, max_length=100),
    estado: Optional[Literal["DISPONIBLE", "SOLICITADA", "ADOPTADA"]] = Query(None),
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
    retirada: Optional[bool] = Query(None),
):
    consulta = select(Planta).where(Planta.id_usuario == usuario_actual.id_usuario)

    if busqueda:
        consulta = consulta.where(Planta.nombre.ilike(f"%{busqueda}%"))
    if estado:
        consulta = consulta.where(Planta.estado_planta == estado)

    if retirada is not None:
        consulta = consulta.where(Planta.eliminada == retirada)

    offset = (pagina - 1) * limite
    plantas = db.execute(
        consulta.order_by(Planta.id_planta.desc()).offset(offset).limit(limite)
    ).scalars().unique().all()

    return [_planta_a_respuesta(db, p, usuario_actual) for p in plantas]


@router.get("/mias/{id_planta}", response_model=PlantaRespuesta)
def consultar_publicacion_propia(
    id_planta: int,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    planta = db.scalar(select(Planta).where(
        Planta.id_planta == id_planta,
        Planta.id_usuario == usuario_actual.id_usuario,
    ))
    if planta is None:
        raise HTTPException(404, "Publicación propia no encontrada")
    return _planta_a_respuesta(db, planta, usuario_actual)


@router.get("/{id_planta}", response_model=PlantaRespuesta)
def consultar_planta(
    id_planta: int,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    planta = db.execute(
        select(Planta).where(Planta.id_planta == id_planta)
    ).scalar_one_or_none()

    if planta is None or not planta.visible or planta.eliminada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planta no encontrada",
        )

    return _planta_a_respuesta(db, planta, usuario_actual)


@router.patch("/{id_planta}", response_model=PlantaRespuesta, openapi_extra=documentacion_entrada(PlantaUpdate))
def modificar_planta(
    id_planta: int,
    entrada = Depends(entrada_editar),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    datos, archivo = entrada
    planta = db.execute(
        select(Planta).where(Planta.id_planta == id_planta).with_for_update()
    ).scalar_one_or_none()

    if planta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planta no encontrada",
        )

    if planta.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar esta publicación",
        )

    if planta.estado_planta != "DISPONIBLE" or not planta.visible or planta.eliminada:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo se pueden editar publicaciones DISPONIBLES, visibles y no eliminadas",
        )

    if datos.id_categoria is not None and datos.id_categoria != planta.id_categoria:
        categoria = db.execute(
            select(Categoria).where(
                Categoria.id_categoria == datos.id_categoria
            )
        ).scalar_one_or_none()
        if categoria is None or categoria.estado != "ACTIVA":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La categoría debe existir y estar ACTIVA",
            )

    datos_dict = datos.model_dump(exclude_unset=True)
    if "id_categoria" in datos_dict and datos_dict["id_categoria"] is None:
        raise HTTPException(422, "La categoría no puede estar vacía")
    fotos = list(db.scalars(select(Fotografia).where(Fotografia.id_planta == id_planta).order_by(Fotografia.id_fotografia)))
    archivos = archivo.archivos if isinstance(archivo, SeleccionFotos) else ([archivo] if archivo else [])
    conservar = archivo.conservar if isinstance(archivo, SeleccionFotos) else None
    if conservar is not None and not set(conservar) <= {f.url for f in fotos}:
        raise HTTPException(422, "Solo puedes conservar fotografías actuales de esta publicación")
    quitar = [f for f in fotos if conservar is not None and f.url not in conservar]
    # La carga singular antigua sigue reemplazando únicamente la primera foto.
    if archivo is not None and not isinstance(archivo, SeleccionFotos) and fotos:
        quitar = [fotos[0]]
    total = len(fotos) - len(quitar) + len(archivos)
    if not 1 <= total <= MAX_FOTOS:
        raise HTTPException(422, "La publicación debe conservar entre una y cinco fotografías")
    contenidos = [preparar_imagen(f) for f in archivos]
    assets = []
    try:
        for contenido in contenidos:
            url, asset = subir_imagen(contenido)
            assets.append(asset)
            if archivo is not None and not isinstance(archivo, SeleccionFotos) and fotos:
                fotos[0].url = url
                quitar = []
            else:
                db.add(Fotografia(id_planta=id_planta, url=url))
        for foto in quitar:
            db.delete(foto)
        for campo, valor in datos_dict.items():
            setattr(planta, campo, valor)
        db.commit()
    except Exception as error:
        db.rollback()
        for asset in assets:
            eliminar_imagen(asset)
        if isinstance(error, HTTPException):
            raise
        raise HTTPException(400, "Error al actualizar la publicación; no se guardaron cambios parciales") from None

    return _planta_a_respuesta(db, planta, usuario_actual)


@router.delete("/{id_planta}")
def retirar_planta(
    id_planta: int,
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    planta = db.execute(
        select(Planta).where(Planta.id_planta == id_planta).with_for_update()
    ).scalar_one_or_none()

    if planta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Planta no encontrada",
        )

    if planta.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para retirar esta publicación",
        )

    if planta.estado_planta != "DISPONIBLE" or not planta.visible or planta.eliminada:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo se pueden retirar publicaciones DISPONIBLES, visibles y no eliminadas",
        )

    adopcion_en_curso = db.execute(
        text("SELECT 1 FROM public.adopcion WHERE id_planta = :id AND estado IN ('EN_PROCESO', 'COMPLETADA') LIMIT 1"),
        {"id": id_planta},
    ).scalar_one_or_none()

    if adopcion_en_curso is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se puede retirar una planta con adopción en curso o completada",
        )

    try:
        db.execute(
            text("UPDATE public.solicitud_adopcion SET estado = 'RECHAZADA' WHERE id_planta = :id AND estado = 'PENDIENTE'"),
            {"id": id_planta},
        )

        planta.eliminada = True
        planta.visible = False

        db.commit()
        db.refresh(planta)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al retirar la publicación",
        )

    return _planta_a_respuesta(db, planta, usuario_actual)


@router.post("", response_model=PlantaRespuesta, status_code=status.HTTP_201_CREATED, openapi_extra=documentacion_entrada(PlantaCreate, True))
@router.post("/", response_model=PlantaRespuesta, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def crear_planta(
    entrada = Depends(entrada_crear),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(obtener_usuario_actual),
):
    datos, archivo = entrada
    categoria = db.execute(
        select(Categoria).where(Categoria.id_categoria == datos.id_categoria)
    ).scalar_one_or_none()

    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada",
        )

    if categoria.estado != "ACTIVA":
        raise HTTPException(status_code=400, detail="La categoría debe estar ACTIVA")

    planta = Planta(
        **datos.model_dump(),
        id_usuario=usuario_actual.id_usuario,
    )

    archivos = archivo.archivos if isinstance(archivo, SeleccionFotos) else [archivo]
    if not 1 <= len(archivos) <= MAX_FOTOS:
        raise HTTPException(422, "Adjunta entre una y cinco fotografías")
    contenidos = [preparar_imagen(f) for f in archivos]
    assets = []
    try:
        urls = []
        for contenido in contenidos:
            url, asset = subir_imagen(contenido)
            assets.append(asset)
            urls.append(url)
        db.add(planta)
        db.flush()
        for url in urls:
            db.add(Fotografia(id_planta=planta.id_planta, url=url))
        db.commit()
    except Exception as error:
        db.rollback()
        for asset in assets:
            eliminar_imagen(asset)
        if isinstance(error, HTTPException):
            raise
        raise HTTPException(500, "No se pudo guardar la publicación; no se guardaron datos incompletos") from None

    return _planta_a_respuesta(db, planta, usuario_actual)
