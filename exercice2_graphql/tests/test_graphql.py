import pytest
from fastapi.testclient import TestClient
import sys, os
sys.modules.pop("app", None)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import app

TOKEN = "token_secret"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
URL = "/graphql"

@pytest.fixture
def client():
    return TestClient(app)

def gql(client, query, variables=None, headers=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    return client.post(URL, json=payload, headers=headers or HEADERS)

class TestQueries:
    def test_liste_evenements(self, client):
        q = "{ evenements { id nom lieu } }"
        r = gql(client, q)
        assert r.status_code == 200
        data = r.json()["data"]
        assert len(data["evenements"]) >= 3

    def test_evenement_par_id(self, client):
        q = "{ evenement(id: 1) { nom lieu } }"
        r = gql(client, q)
        assert r.status_code == 200
        assert r.json()["data"]["evenement"]["nom"] == "Conférence Python"

    def test_evenement_inexistant(self, client):
        q = "{ evenement(id: 999) { nom } }"
        r = gql(client, q)
        assert r.json()["data"]["evenement"] is None

    def test_filtre_organisateur(self, client):
        q = '{ evenements(organisateur: "EPSI") { nom organisateur } }'
        r = gql(client, q)
        assert r.status_code == 200
        data = r.json()["data"]
        assert all(e["organisateur"] == "EPSI" for e in data["evenements"])

    def test_query_sans_token(self, client):
        q = "{ evenements { id } }"
        r = client.post(URL, json={"query": q})
        assert r.status_code in [401, 403, 422]

    def test_query_mauvais_token(self, client):
        q = "{ evenements { id } }"
        headers_bad = {"Authorization": "Bearer mauvais_token"}
        r = client.post(URL, json={"query": q}, headers=headers_bad)
        assert r.status_code in [403, 422]

class TestMutations:
    def test_creer_evenement(self, client):
        mutation = """
        mutation {
            creerEvenement(evenementInput: {
                nom: "Événement Test"
                lieu: "Toulouse"
                date: "2024-09-15"
                capaciteMax: 75
                organisateur: "Test Org"
            }) {
                id
                nom
                capaciteMax
            }
        }
        """
        r = gql(client, mutation)
        assert r.status_code == 200
        data = r.json()["data"]["creerEvenement"]
        assert data["nom"] == "Événement Test"
        assert "id" in data

    def test_creer_evenement_nom_vide(self, client):
        mutation = """
        mutation {
            creerEvenement(evenementInput: {
                nom: ""
                lieu: "Toulouse"
                date: "2024-09-15"
                capaciteMax: 75
                organisateur: "Test Org"
            }) {
                id
                nom
            }
        }
        """
        r = gql(client, mutation)
        assert r.status_code == 200
        assert "errors" in r.json()

    def test_creer_evenement_capacite_invalide(self, client):
        mutation = """
        mutation {
            creerEvenement(evenementInput: {
                nom: "Test"
                lieu: "Toulouse"
                date: "2024-09-15"
                capaciteMax: -10
                organisateur: "Test Org"
            }) {
                id
            }
        }
        """
        r = gql(client, mutation)
        assert r.status_code == 200
        assert "errors" in r.json()

    def test_modif_evenement(self, client):
        mutation = """
        mutation {
            modifierEvenement(id: 1, evenementInput: {
                nom: "Conférence Python 2024"
                lieu: "Paris"
                date: "2024-06-15"
                capaciteMax: 150
                organisateur: "EPSI"
            }) {
                id
                nom
                capaciteMax
            }
        }
        """
        r = gql(client, mutation)
        assert r.status_code == 200
        data = r.json()["data"]["modifierEvenement"]
        assert data["nom"] == "Conférence Python 2024"
        assert data["capaciteMax"] == 150

    def test_modifier_evenement_inexistant(self, client):
        mutation = """
        mutation {
            modifierEvenement(id: 999, evenementInput: {
                nom: "Test"
                lieu: "Paris"
                date: "2024-06-15"
                capaciteMax: 50
                organisateur: "Test"
            }) {
                id
            }
        }
        """
        r = gql(client, mutation)
        assert r.json()["data"]["modifierEvenement"] is None

    def test_supprimer_evenement(self, client):
        mutation = """
        mutation {
            supprimerEvenement(id: 1) {
                success
                message
            }
        }
        """
        r = gql(client, mutation)
        assert r.status_code == 200
        data = r.json()["data"]["supprimerEvenement"]
        assert data["success"] is True

    def test_supprimer_evenement_inexistant(self, client):
        mutation = """
        mutation {
            supprimerEvenement(id: 999) {
                success
                message
            }
        }
        """
        r = gql(client, mutation)
        assert r.status_code == 200
        data = r.json()["data"]["supprimerEvenement"]
        assert data["success"] is False

class TestAuthentification:
    def test_sans_header_authorization(self, client):
        q = "{ evenements { id } }"
        r = client.post(URL, json={"query": q})
        assert r.status_code in [401, 403, 422]

    def test_token_format_invalide(self, client):
        q = "{ evenements { id } }"
        headers_bad = {"Authorization": "mon_token_secret"}
        r = client.post(URL, json={"query": q}, headers=headers_bad)
        assert r.status_code in [401, 403, 422]
