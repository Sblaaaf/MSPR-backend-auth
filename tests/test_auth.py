from hashlib import sha256

from fastapi.testclient import TestClient

from main import app
import app.routes as routes

client = TestClient(app)


def fake_hash_password(raw_password: str) -> str:
    return sha256(raw_password.encode("utf-8")).hexdigest()


def _active_user(password: str = "secret123") -> dict:
    return {
        "id": 1,
        "email": "jean.dupont@example.com",
        "nom": "Dupont",
        "prenom": "Jean",
        "mdp_hash": fake_hash_password(password),
        "actif": True,
        "abonnement": "freemium",
    }


# ---------------------------------------------------------------------------
# POST /login
# ---------------------------------------------------------------------------

def test_login_success(monkeypatch):
    monkeypatch.setattr(routes, "fetch_one", lambda *a, **kw: _active_user())

    resp = client.post("/login", json={"email": "jean.dupont@example.com", "password": "secret123"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["user_id"] == 1
    assert body["email"] == "jean.dupont@example.com"
    assert body["nom"] == "Dupont"
    assert body["prenom"] == "Jean"
    assert body["abonnement"] == "freemium"


def test_login_wrong_password(monkeypatch):
    monkeypatch.setattr(routes, "fetch_one", lambda *a, **kw: _active_user())

    resp = client.post("/login", json={"email": "jean.dupont@example.com", "password": "badpass"})

    assert resp.status_code == 401
    # message depends on Accept-Language header (EN default: "Email or password incorrect.")
    assert "incorrect" in resp.json()["detail"].lower()


def test_login_user_not_found(monkeypatch):
    monkeypatch.setattr(routes, "fetch_one", lambda *a, **kw: None)

    resp = client.post("/login", json={"email": "nobody@example.com", "password": "secret123"})

    assert resp.status_code == 401


def test_login_inactive_user(monkeypatch):
    user = {**_active_user(), "actif": False}
    monkeypatch.setattr(routes, "fetch_one", lambda *a, **kw: user)

    resp = client.post("/login", json={"email": "jean.dupont@example.com", "password": "secret123"})

    assert resp.status_code == 403


def test_login_invalid_email_format():
    resp = client.post("/login", json={"email": "not-an-email", "password": "secret123"})
    assert resp.status_code == 422


def test_login_password_too_short():
    resp = client.post("/login", json={"email": "jean.dupont@example.com", "password": "abc"})
    assert resp.status_code == 422


def test_login_missing_fields():
    resp = client.post("/login", json={"email": "jean.dupont@example.com"})
    assert resp.status_code == 422


def test_login_returns_correct_abonnement(monkeypatch):
    user = {**_active_user(), "abonnement": "premium"}
    monkeypatch.setattr(routes, "fetch_one", lambda *a, **kw: user)

    resp = client.post("/login", json={"email": "jean.dupont@example.com", "password": "secret123"})

    assert resp.status_code == 200
    assert resp.json()["abonnement"] == "premium"


# ---------------------------------------------------------------------------
# POST /admin-login
# ---------------------------------------------------------------------------

def test_admin_login_success(monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "adminpass")

    resp = client.post("/admin-login", json={"username": "admin", "password": "adminpass"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["role"] == "admin"


def test_admin_login_wrong_password(monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "adminpass")

    resp = client.post("/admin-login", json={"username": "admin", "password": "wrongpass"})

    assert resp.status_code == 401
    assert "invalides" in resp.json()["detail"].lower()


def test_admin_login_wrong_username(monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "adminpass")

    resp = client.post("/admin-login", json={"username": "hacker", "password": "adminpass"})

    assert resp.status_code == 401


def test_admin_login_missing_fields():
    resp = client.post("/admin-login", json={"username": "admin"})
    assert resp.status_code == 422


def test_admin_login_default_credentials():
    # Default env values: admin/admin
    resp = client.post("/admin-login", json={"username": "admin", "password": "admin"})
    assert resp.status_code == 200
    assert resp.json()["success"] is True
