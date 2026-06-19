import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app import app, codes_autorisation, refresh_tokens


@pytest.fixture(autouse=True)
def nettoyer_etat():
    """Remet a zero les dictionnaires d'etat avant chaque test."""
    codes_autorisation.clear()
    refresh_tokens.clear()
    yield
    codes_autorisation.clear()
    refresh_tokens.clear()


@pytest.fixture
def client():
    """Cree un client de test Flask."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_authorize_retourne_code_pour_identifiants_valides(client):
    response = client.post(
        "/oauth/authorize",
        json={"username": "alice", "password": "motdepasse123", "client_id": "app_comparateur"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "code" in data
    assert len(data["code"]) == 32


def test_authorize_rejette_identifiants_invalides(client):
    response = client.post(
        "/oauth/authorize",
        json={"username": "alice", "password": "mauvais", "client_id": "app_comparateur"}
    )
    assert response.status_code == 401


def test_authorize_rejette_client_id_invalide(client):
    response = client.post(
        "/oauth/authorize",
        json={"username": "alice", "password": "motdepasse123", "client_id": "inconnu"}
    )
    assert response.status_code == 401


def test_token_exchange_valide(client):
    auth_resp = client.post(
        "/oauth/authorize",
        json={"username": "alice", "password": "motdepasse123", "client_id": "app_comparateur"}
    )
    code = json.loads(auth_resp.data)["code"]
    response = client.post(
        "/oauth/token",
        json={"code": code, "client_id": "app_comparateur", "client_secret": "secret_comparateur"}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "access_token" in data
    assert "refresh_token" in data


def test_token_rejette_client_secret_invalide(client):
    auth_resp = client.post(
        "/oauth/authorize",
        json={"username": "alice", "password": "motdepasse123", "client_id": "app_comparateur"}
    )
    code = json.loads(auth_resp.data)["code"]
    response = client.post(
        "/oauth/token",
        json={"code": code, "client_id": "app_comparateur", "client_secret": "mauvais_secret"}
    )
    assert response.status_code == 401


def test_code_autorisation_usage_unique(client):
    auth_resp = client.post(
        "/oauth/authorize",
        json={"username": "alice", "password": "motdepasse123", "client_id": "app_comparateur"}
    )
    code = json.loads(auth_resp.data)["code"]
    client.post(
        "/oauth/token",
        json={"code": code, "client_id": "app_comparateur", "client_secret": "secret_comparateur"}
    )
    response = client.post(
        "/oauth/token",
        json={"code": code, "client_id": "app_comparateur", "client_secret": "secret_comparateur"}
    )
    assert response.status_code == 400


def test_token_code_invalide(client):
    response = client.post(
        "/oauth/token",
        json={"code": "code_inexistant", "client_id": "app_comparateur", "client_secret": "secret_comparateur"}
    )
    assert response.status_code == 400


def test_refresh_token_genere_nouvel_access_token(client):
    auth_resp = client.post(
        "/oauth/authorize",
        json={"username": "alice", "password": "motdepasse123", "client_id": "app_comparateur"}
    )
    code = json.loads(auth_resp.data)["code"]
    token_resp = client.post(
        "/oauth/token",
        json={"code": code, "client_id": "app_comparateur", "client_secret": "secret_comparateur"}
    )
    refresh_token = json.loads(token_resp.data)["refresh_token"]
    response = client.post("/oauth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in json.loads(response.data)


def test_refresh_token_invalide(client):
    response = client.post("/oauth/refresh", json={"refresh_token": "token_invalide"})
    assert response.status_code == 401


def test_profil_protege_sans_token(client):
    response = client.get("/profil")
    assert response.status_code == 401


def test_profil_accessible_avec_access_token(client):
    auth_resp = client.post(
        "/oauth/authorize",
        json={"username": "alice", "password": "motdepasse123", "client_id": "app_comparateur"}
    )
    code = json.loads(auth_resp.data)["code"]
    token_resp = client.post(
        "/oauth/token",
        json={"code": code, "client_id": "app_comparateur", "client_secret": "secret_comparateur"}
    )
    access_token = json.loads(token_resp.data)["access_token"]
    response = client.get("/profil", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert json.loads(response.data)["utilisateur"] == "alice"
