import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.app import app


def test_home_endpoint():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "Bookstore Management System API is running" in data["message"]

def test_health_endpoint():
    client = app.test_client()
    response = client.get("/health")

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "bookstore-api"

def test_version_endpoint():
    client = app.test_client()
    response = client.get("/version")

    assert response.status_code == 200

    data = response.get_json()
    assert data["application"] == "Bookstore Management System"
    assert data["version"] == "1.0"