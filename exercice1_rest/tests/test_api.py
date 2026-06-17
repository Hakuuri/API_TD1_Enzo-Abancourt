import pytest
import sys, os
sys.modules.pop("app", None)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import app, evenements_db, next_id

TOKEN = "token_secret"
HEADERS_OK = {"Authorization": f"Bearer {TOKEN}"}
HEADERS_BAD = {"Authorization": "Bearer mauvais_token"}

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

class TestGetEvenements:
    def test_get_tous_les_evenements(self, client):
        r = client.get("/evenements", headers=HEADERS_OK)
        assert r.status_code == 200
        data = r.get_json()
        assert "evenements" in data
        assert data["total"] >= 3

    def test_get_evenement_par_id(self, client):
        r = client.get("/evenements/1", headers=HEADERS_OK)
        assert r.status_code == 200
        assert r.get_json()["nom"] == "Conférence Python"

    def test_get_evenement_inexistant(self, client):
        r = client.get("/evenements/999", headers=HEADERS_OK)
        assert r.status_code == 404

    def test_get_sans_token(self, client):
        r = client.get("/evenements")
        assert r.status_code == 401

    def test_get_mauvais_token(self, client):
        r = client.get("/evenements", headers=HEADERS_BAD)
        assert r.status_code == 403

    def test_get_filtre_organisateur(self, client):
        r = client.get("/evenements?organisateur=EPSI", headers=HEADERS_OK)
        assert r.status_code == 200
        data = r.get_json()
        assert all(e["organisateur"] == "EPSI" for e in data["evenements"])

class TestCreateEvenement:
    def test_creer_evenement_valide(self, client):
        payload = {
            "nom": "Webinaire Cloud",
            "lieu": "Bordeaux",
            "date": "2024-08-15",
            "capacite_max": 200,
            "organisateur": "Acme Corp"
        }
        r = client.post("/evenements", json=payload, headers=HEADERS_OK)
        assert r.status_code == 201
        evenement = r.get_json()
        assert evenement["nom"] == "Webinaire Cloud"
        assert "id" in evenement

    def test_creer_evenement_champ_manquant(self, client):
        payload = {
            "nom": "Événement incomplet",
            "lieu": "Paris",
            "date": "2024-08-20",
            "capacite_max": 50
        }
        r = client.post("/evenements", json=payload, headers=HEADERS_OK)
        assert r.status_code == 400

    def test_creer_evenement_capacite_invalide(self, client):
        payload = {
            "nom": "Test",
            "lieu": "Paris",
            "date": "2024-08-20",
            "capacite_max": -5,
            "organisateur": "Test Org"
        }
        r = client.post("/evenements", json=payload, headers=HEADERS_OK)
        assert r.status_code == 400

    def test_creer_evenement_date_invalide(self, client):
        payload = {
            "nom": "Test",
            "lieu": "Paris",
            "date": "15/08/2024",
            "capacite_max": 50,
            "organisateur": "Test Org"
        }
        r = client.post("/evenements", json=payload, headers=HEADERS_OK)
        assert r.status_code == 400

    def test_creer_evenement_nom_vide(self, client):
        payload = {
            "nom": "",
            "lieu": "Paris",
            "date": "2024-08-20",
            "capacite_max": 50,
            "organisateur": "Test Org"
        }
        r = client.post("/evenements", json=payload, headers=HEADERS_OK)
        assert r.status_code == 400

class TestUpdateEvenement:
    def test_modif_evenement(self, client):
        payload = {
            "nom": "Conférence Python Avancée",
            "lieu": "Paris",
            "date": "2024-06-15",
            "capacite_max": 150,
            "organisateur": "EPSI"
        }
        r = client.put("/evenements/1", json=payload, headers=HEADERS_OK)
        assert r.status_code == 200
        assert r.get_json()["nom"] == "Conférence Python Avancée"

    def test_modif_evenement_inexistant(self, client):
        payload = {
            "nom": "Test",
            "lieu": "Paris",
            "date": "2024-08-20",
            "capacite_max": 50,
            "organisateur": "Test Org"
        }
        r = client.put("/evenements/999", json=payload, headers=HEADERS_OK)
        assert r.status_code == 404

class TestDeleteEvenement:
    def test_supprimer_evenement(self, client):
        r = client.delete("/evenements/1", headers=HEADERS_OK)
        assert r.status_code == 204

    def test_supprimer_evenement_inexistant(self, client):
        r = client.delete("/evenements/999", headers=HEADERS_OK)
        assert r.status_code == 404

class TestAuthentification:
    def test_post_sans_token(self, client):
        payload = {
            "nom": "Test",
            "lieu": "Paris",
            "date": "2024-08-20",
            "capacite_max": 50,
            "organisateur": "Test Org"
        }
        r = client.post("/evenements", json=payload)
        assert r.status_code == 401

    def test_put_avec_mauvais_token(self, client):
        payload = {
            "nom": "Test",
            "lieu": "Paris",
            "date": "2024-08-20",
            "capacite_max": 50,
            "organisateur": "Test Org"
        }
        r = client.put("/evenements/1", json=payload, headers=HEADERS_BAD)
        assert r.status_code == 403

    def test_delete_sans_token(self, client):
        r = client.delete("/evenements/1")
        assert r.status_code == 401
