import pytest
from main import create_app
from fastapi.testclient import TestClient
from internal.config import AppConfig
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
        headers={"Authorization": "Bearer PULSAR_REGISTRY_KEY"}
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {"id": 1}

    # Get pulsar
    response = client.get(
        "/api/pulsar/1",
        headers={"Authorization": "Bearer PULSAR_REGISTRY_KEY"},
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
        headers={"Authorization": "Bearer PULSAR_REGISTRY_KEY"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [{
        "id": 1,
        "url": "http://localhost:8080",
        "api_key": "1234567890",
        "users": ["test@test.com"]
    }]

    # Update pulsar
    response = client.put(
        "/api/pulsar/1",
        json={
            "url": "http://localhost:9090",  # Changed URL
            "api_key": "0987654321",         # Changed API key
            "users": ["test@test.com", "new@test.com"]  # Added a user
        },
        headers={"Authorization": "Bearer PULSAR_REGISTRY_KEY"}
    )
    
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"id": 1}

    # Verify update
    response = client.get(
        "/api/pulsar/1",
        headers={"Authorization": "Bearer PULSAR_REGISTRY_KEY"}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "id": 1,
        "url": "http://localhost:9090",
        "api_key": "0987654321",
        "users": ["test@test.com", "new@test.com"]
    }

    # Delete pulsar
    response = client.delete(
        "/api/pulsar/1", 
        headers={"Authorization": "Bearer PULSAR_REGISTRY_KEY"}
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

@pytest.fixture
def client():
    config = AppConfig(test = True)
    app = create_app(config)
    client = TestClient(app)
    return client

