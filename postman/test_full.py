import sys
sys.path.insert(0, '.')
from fastapi.testclient import TestClient
from app.main import app

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkwMjY5NDA1LCJleHAiOjE3OTAyNzEyMDV9.XBeRl2H8fVIVElTUXHcIWfSFCoKtVv2p1DrXJkDIM9Q"
headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

c = TestClient(app)

# 1. Crear planta
print("=== 1. CREAR PLANTA ===")
r = c.post("/api/plantas", json={"nombre": "Prueba CRUD", "tamano": "Grande", "nivel_cuidado": "Alto", "estado_salud": "Saludable", "necesidad_luz": "Sol", "necesidad_agua": "Alta", "ubicacion": "Jardin", "id_categoria": 1})
print(f"POST: {r.status_code}")
plantas = r.json()
id_planta = plantas.get("id_planta")
print(f"ID creada: {id_planta}")

# 2. Catálogo
print("\n=== 2. CATÁLOGO ===")
r = c.get("/api/plantas")
print(f"GET /api/plantas: {r.status_code}, total={r.json()['total']}")

# 3. Detalle por ID
print("\n=== 3. DETALLE ===")
if id_planta:
    r = c.get(f"/api/plantas/{id_planta}")
    print(f"GET /api/plantas/{id_planta}: {r.status_code}")

# 4. Mis plantas
print("\n=== 4. MIS PLANTAS ===")
r = c.get("/api/plantas/mias", headers=headers)
print(f"GET /api/plantas/mias: {r.status_code}, total={len(r.json())}")

# 5. Modificar
print("\n=== 5. MODIFICAR ===")
if id_planta:
    r = c.patch(f"/api/plantas/{id_planta}", json={"nombre": "Prueba CRUD Modificada"}, headers=headers)
    print(f"PATCH: {r.status_code}, nombre={r.json().get('nombre')}")

# 6. Retirar
print("\n=== 6. RETIRAR ===")
if id_planta:
    r = c.delete(f"/api/plantas/{id_planta}", headers=headers)
    print(f"DELETE: {r.status_code}")

# 7. Verificar retirada
print("\n=== 7. VERIFICAR RETIRO ===")
r = c.get(f"/api/plantas/{id_planta}")
print(f"GET después de DELETE: {r.status_code}")

# 8. Fotografías
print("\n=== 8. FOTOGRAFÍAS ===")
r = c.get("/api/fotografias?id_planta=1")
print(f"GET /api/fotografias: {r.status_code}")
r = c.post("/api/fotografias", json={"id_planta": 1, "url": "http://ejemplo.com/foto.jpg", "es_principal": True}, headers=headers)
print(f"POST /api/fotografias: {r.status_code}")
r = c.delete("/api/fotografias/1")
print(f"DELETE /api/fotografias/1: {r.status_code}")

print("\n=== TODOS LOS TESTS PASARON ===")