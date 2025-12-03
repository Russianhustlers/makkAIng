from fastapi.testclient import TestClient

from backend.app.main import app


def test_ping_returns_status_ok():
    client = TestClient(app)
    response = client.get("/ping")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
