import sys
sys.path.insert(0, '.')
from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)
r = c.get("/api/plantas", headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzkwMjY5NDA1LCJleHAiOjE3OTAyNzEyMDV9.XBeRl2H8fVIVElTUXHcIWfSFCoKtVv2p1DrXJkDIM9Q"})
print("Status:", r.status_code)
print("Text:", r.text[:500])