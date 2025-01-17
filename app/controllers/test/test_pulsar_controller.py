import pytest
from app.main import create_app
from fastapi.testclient import TestClient
from app.internal.config import AppConfig
from http import HTTPStatus

def test_health(client):
    response = client.get("/api/pulsar/health")
    assert response.status_code == HTTPStatus.OK

def test_pulsar(client):
    # Create pulsar
    response = client.post(
        "/api/pulsar", 
        json={
            "url": "http://localhost:8080",
            "api_key": "1234567890",
            "users": ["test@test.com"]
        },
        headers={"Authorization": "Bearer 1234567890"},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {"id": 1}

    # Get pulsar
    response = client.get(
        "/api/pulsar/1",
        headers={"Authorization": "Bearer 1234567890"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": 1,
        "url": "http://localhost:8080",
        "api_key": "1234567890",
        "users": ["test@test.com"]
    }

    # Search pulsar
    response = client.get(
        "/api/pulsar?user=test@test.com",
        headers={"Authorization": "Bearer 1234567890"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [{
        "id": 1,
        "url": "http://localhost:8080",
        "api_key": "1234567890",
        "users": ["test@test.com"]
    }]

    # Delete pulsar
    response = client.delete(
        "/api/pulsar/1", 
        headers={"Authorization": "Bearer 1234567890"},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

@pytest.fixture
def client():
    config = AppConfig()
    app = create_app(config)
    client = TestClient(app)
    return client

