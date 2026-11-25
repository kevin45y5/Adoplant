from typing import Literal

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials

from app.dependencies import bearer

router = APIRouter(prefix="/admin/metricas", tags=["Métricas de administración"])

Metrica = Literal[
    "resumen", "evolucion", "plantas-por-categoria", "embudo", "usuarios", "reportes"
]


@router.get("/{metrica}")
async def consultar_metrica(
    metrica: Metrica,
    request: Request,
    meses: int | None = None,
    limite: int | None = None,
    credenciales: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> Response:
    if credenciales is None:
        raise HTTPException(401, "Inicia sesión para consultar las métricas", headers={
            "WWW-Authenticate": "Bearer",
        })

    # .NET comprueba la firma del JWT y el rol antes de consultar PostgreSQL.
    params = {}
    if metrica == "evolucion" and meses is not None:
        params["meses"] = meses
    if metrica in ("usuarios", "reportes") and limite is not None:
        params["limite"] = limite

    try:
        upstream = await request.app.state.analytics.get(
            f"api/metricas/{metrica}",
            params=params,
            headers={"Authorization": f"Bearer {credenciales.credentials}"},
        )
    except httpx.RequestError:
        raise HTTPException(503, "El servicio de métricas no está disponible. Intenta nuevamente.") from None

    if upstream.status_code == 401:
        raise HTTPException(401, "Tu sesión venció. Vuelve a iniciar sesión.", headers={
            "WWW-Authenticate": "Bearer",
        })
    if upstream.status_code == 403:
        raise HTTPException(403, "Se requieren permisos de administrador")
    if upstream.status_code != 200:
        raise HTTPException(502, "El servicio de métricas no pudo completar la consulta.")

    return Response(
        content=upstream.content,
        media_type="application/json",
        headers={"Cache-Control": "no-store"},
    )
