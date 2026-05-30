import pytest
from backend.main import app
from fastapi.testclient import TestClient


@pytest.fixture(name="client")
def fixture_client():
    """Provide a setup context manager wrapping application client network boundaries."""
    with TestClient(app) as tc:
        yield tc


def test_api_login_success(client):
    """Verify that seeded credentials successfully pass route authentication requirements."""
    response = client.post(
        "/api/login",
        data={"username": "client_demo", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "client_demo"
    assert data["role"] == "Client"
    assert "user_id" in data


def test_api_login_invalid_credentials(client):
    """Confirm that the auth endpoint drops invalid access request packets."""
    response = client.post(
        "/api/login",
        data={"username": "non_existent_user", "password": "wrong_password"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_mock_inference_endpoint(client, mocker):
    """Verify prediction image streaming routes run safely when the underlying model is mocked."""
    mocker.patch(
        "backend.main.predictor.predict",
        return_value=("Monstera Deliciosa", 0.9450),
    )

    file_payload = {"file": ("test_leaf.png", b"fake_image_bytes", "image/png")}
    data_payload = {"user_id": 1}

    response = client.post(
        "/api/predict", files=file_payload, data=data_payload
    )

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["predicted_species"] == "Monstera Deliciosa"
    assert json_response["confidence"] == 0.9450
    assert "log_id" in json_response