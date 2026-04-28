from hashlib import sha256

from fastapi.testclient import TestClient

from main import app
import app.routes as routes

client = TestClient(app)


def fake_hash_password(raw_password: str) -> str:
    return sha256(raw_password.encode("utf-8")).hexdigest()


def test_login_success(monkeypatch):
    def fake_fetch_one(sql, params=None):
        return {
            "id": 1,
            "email": "jean.dupont@example.com",
            "mdp_hash": fake_hash_password("secret123"),
            "actif": True,
        }

    monkeypatch.setattr(routes, "fetch_one", fake_fetch_one)

    response = client.post(
        "/login",
        json={"email": "jean.dupont@example.com", "password": "secret123"},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["user_id"] == 1


def test_login_failure_wrong_password(monkeypatch):
    def fake_fetch_one(sql, params=None):
        return {
            "id": 1,
            "email": "jean.dupont@example.com",
            "mdp_hash": fake_hash_password("secret123"),
            "actif": True,
        }

    monkeypatch.setattr(routes, "fetch_one", fake_fetch_one)

    response = client.post(
        "/login",
        json={"email": "jean.dupont@example.com", "password": "badpass"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Email ou mot de passe incorrect."
