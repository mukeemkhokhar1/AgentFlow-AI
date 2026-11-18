from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_workflow():
    response = client.post("/api/workflows", json={
        "request": "Prepare a weekly project report"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "completed"
    assert len(data["agents"]) == 3
    assert data["review"]["passed"] is True

def test_reject_short_request():
    response = client.post("/api/workflows", json={"request": "no"})
    assert response.status_code == 422

def test_missing_workflow():
    response = client.get("/api/workflows/99999999")
    assert response.status_code == 404
