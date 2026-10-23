"""Crea (de forma idempotente) los datos que necesitan las pruebas automatizadas.

    python -m scripts.seed_pruebas

Se ejecuta solo con el codigo y el entorno de la API:

* dentro de Docker:  docker compose exec api python -m scripts.seed_pruebas
* en el stack QA:    servicio one-shot `seed` del docker-compose.yml

Crea las cuentas documentadas en el README (administrador, donante y
adoptante), cuatro categorias activas y tres plantas publicadas por el
donante. Si los datos ya existen no los duplica ni cambia contrasenas.
"""

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Administrador, Categoria, Planta, Usuario
from app.security import crear_hash

CUENTAS = (
    {
        "nombre": "Administrador",
        "apellido": "Panel",
        "correo": "admin.panel@adopplant.com",
        "telefono": "70000001",
        "contrasena": "Admin2026panel",
        "administrador": True,
    },
    {
        "nombre": "Donante",
        "apellido": "Pruebas",
        "correo": "donante.pruebas@adopplant.com",
        "telefono": "70000002",
        "contrasena": "Donante2026!",
        "administrador": False,
    },
    {
        "nombre": "Adoptante",
        "apellido": "Pruebas",
        "correo": "adoptante.pruebas@adopplant.com",
        "telefono": "70000003",
        "contrasena": "Adoptante2026!",
        "administrador": False,
    },
)

CATEGORIAS = ("Interior", "Exterior", "Suculentas", "Ornamentales")

PLANTAS = (
    {
        "nombre": "Monstera de pruebas",
        "tamano": "Mediana",
        "nivel_cuidado": "Medio",
        "estado_salud": "Saludable",
        "necesidad_luz": "Indirecta",
        "necesidad_agua": "Moderada",
        "descripcion": "Planta creada por el seed para las pruebas de carga.",
        "ubicacion": "San Salvador",
    },
    {
        "nombre": "Suculenta de pruebas",
        "tamano": "Pequena",
        "nivel_cuidado": "Bajo",
        "estado_salud": "Saludable",
        "necesidad_luz": "Directa",
        "necesidad_agua": "Baja",
        "descripcion": "Planta creada por el seed para el catalogo.",
        "ubicacion": "Santa Tecla",
    },
    {
        "nombre": "Helecho de pruebas",
        "tamano": "Mediana",
        "nivel_cuidado": "Alto",
        "estado_salud": "Saludable",
        "necesidad_luz": "Sombra",
        "necesidad_agua": "Alta",
        "descripcion": "Planta creada por el seed para el detalle.",
        "ubicacion": "Antiguo Cuscatlan",
    },
)


def _obtener_o_crear_usuario(db, datos) -> Usuario:
    usuario = db.scalar(
        select(Usuario).where(Usuario.correo == datos["correo"])
    )

    if usuario is None:
        usuario = Usuario(
            nombre=datos["nombre"],
            apellido=datos["apellido"],
            correo=datos["correo"],
            telefono=datos["telefono"],
            contrasena=crear_hash(datos["contrasena"]),
            estado="ACTIVO",
        )
        db.add(usuario)
        db.flush()

    if datos["administrador"]:
        existe = db.scalar(
            select(Administrador).where(
                Administrador.id_usuario == usuario.id_usuario
            )
        )
        if existe is None:
            db.add(Administrador(id_usuario=usuario.id_usuario))

    return usuario


def _obtener_o_crear_categoria(db, nombre: str) -> Categoria:
    categoria = db.scalar(
        select(Categoria).where(Categoria.nombre == nombre)
    )

    if categoria is None:
        categoria = Categoria(nombre=nombre, estado="ACTIVA")
        db.add(categoria)
        db.flush()

    return categoria


def sembrar() -> None:
    with SessionLocal() as db:
        usuarios = [_obtener_o_crear_usuario(db, datos) for datos in CUENTAS]
        donante = usuarios[1]
        categorias = [_obtener_o_crear_categoria(db, nombre) for nombre in CATEGORIAS]

        for indice, datos in enumerate(PLANTAS):
            existe = db.scalar(
                select(Planta).where(
                    Planta.nombre == datos["nombre"],
                    Planta.id_usuario == donante.id_usuario,
                )
            )
            if existe is not None:
                continue

            categoria = categorias[indice % len(categorias)]
            db.add(
                Planta(
                    nombre=datos["nombre"],
                    tamano=datos["tamano"],
                    nivel_cuidado=datos["nivel_cuidado"],
                    estado_salud=datos["estado_salud"],
                    necesidad_luz=datos["necesidad_luz"],
                    necesidad_agua=datos["necesidad_agua"],
                    descripcion=datos["descripcion"],
                    ubicacion=datos["ubicacion"],
                    estado="DISPONIBLE",
                    visible=True,
                    eliminada=False,
                    id_usuario=donante.id_usuario,
                    id_categoria=categoria.id_categoria,
                )
            )

        db.commit()

    print("Datos de prueba listos.")
    print("  Administrador: admin.panel@adopplant.com / Admin2026panel")
    print("  Donante:       donante.pruebas@adopplant.com / Donante2026!")
    print("  Adoptante:     adoptante.pruebas@adopplant.com / Adoptante2026!")


if __name__ == "__main__":
    sembrar()
