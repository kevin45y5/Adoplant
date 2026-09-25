import sys
sys.path.insert(0, '.')
from fastapi.testclient import TestClient
from app.main import app

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkwMjk2MjUxLCJleHAiOjE3OTAyOTgwNTF9.XnoPBILk_MxRb2cKUHGv_LEVsamGnKjh4sUp86R52GU"
headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

c = TestClient(app)

# Check plant 1
r = c.get("/api/plantas/1", headers=headers)
print("Plant 1:", r.status_code, r.text[:200])
print()

# Try delete
r = c.delete("/api/plantas/1", headers=headers)
print("DELETE:", r.status_code, r.text[:500])