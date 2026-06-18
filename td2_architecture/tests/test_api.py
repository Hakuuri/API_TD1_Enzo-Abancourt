"""
Tests de l'API Médiathèque - Réservations de Salles
Utilise pytest et httpx pour tester les endpoints FastAPI
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Importer l'app depuis le fichier parent
sys.path.insert(0, str(Path(__file__).parent.parent))
from td2_architecture.app import app

client = TestClient(app)
API_TOKEN = "token_mediatheque_123"


@pytest.fixture
def auth_header():
    """Fixture fournissant l'en-tête d'authentification."""
    return {"Authorization": f"Bearer {API_TOKEN}"}


class TestListSalles:
    """Tests pour le listing des salles."""

    def test_list_salles_200_non_empty(self, auth_header):
        """Lister les salles renvoie un statut 200 et une liste non vide."""
        response = client.get("/salles", headers=auth_header)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) > 0
        assert response.json()[0].get("nom")
        assert response.json()[0].get("capacite")

    def test_list_salles_requires_auth(self):
        """Lister les salles sans token renvoie 401."""
        response = client.get("/salles")
        assert response.status_code == 401


class TestCreateReservation:
    """Tests pour la création de réservations."""

    def test_create_valid_reservation_201(self, auth_header):
        """Créer une réservation valide renvoie 201."""
        response = client.post(
            "/salles/2/reservations",
            headers=auth_header,
            json={
                "usager": "Mme Dupuis",
                "date": "2026-06-25",
                "heure_debut": "10:00",
                "heure_fin": "11:00"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["salle_id"] == 2
        assert data["usager"] == "Mme Dupuis"
        assert data["heure_debut"] == "10:00"

    def test_create_reservation_nonexistent_salle_404(self, auth_header):
        """Créer une réservation sur une salle inexistante renvoie 404."""
        response = client.post(
            "/salles/999/reservations",
            headers=auth_header,
            json={
                "usager": "M. Test",
                "date": "2026-06-25",
                "heure_debut": "10:00",
                "heure_fin": "11:00"
            }
        )
        assert response.status_code == 404
        assert "non trouvée" in response.json()["detail"].lower()

    def test_create_reservation_overlap_409(self, auth_header):
        """Créer une réservation sur un créneau déjà pris renvoie 409."""
        # La salle 1 a déjà une réservation le 2026-06-20 de 14:00 à 15:30
        response = client.post(
            "/salles/1/reservations",
            headers=auth_header,
            json={
                "usager": "M. Martin",
                "date": "2026-06-20",
                "heure_debut": "14:15",  # Chevauche 14:00-15:30
                "heure_fin": "15:00"
            }
        )
        assert response.status_code == 409
        assert "Conflit" in response.json()["detail"]

    def test_create_reservation_no_overlap_same_day_201(self, auth_header):
        """Créer une réservation avant/après une existante le même jour réussit."""
        # Créer une réservation qui ne chevauche pas
        response = client.post(
            "/salles/1/reservations",
            headers=auth_header,
            json={
                "usager": "Mme Laurent",
                "date": "2026-06-20",
                "heure_debut": "16:00",  # Après 14:00-15:30
                "heure_fin": "17:00"
            }
        )
        assert response.status_code == 201

    def test_create_reservation_different_date_no_conflict_201(self, auth_header):
        """Créer une réservation même horaire mais autre date réussit."""
        response = client.post(
            "/salles/1/reservations",
            headers=auth_header,
            json={
                "usager": "Mme Petit",
                "date": "2026-06-21",  # Autre date
                "heure_debut": "14:00",  # Même horaire, mais autre date
                "heure_fin": "15:30"
            }
        )
        assert response.status_code == 201

    def test_create_reservation_missing_field_400(self, auth_header):
        """Créer une réservation sans champs obligatoires renvoie 400/422."""
        response = client.post(
            "/salles/1/reservations",
            headers=auth_header,
            json={
                "usager": "Test"
                # Manquent: date, heure_debut, heure_fin
            }
        )
        assert response.status_code == 422  # Validation Pydantic


class TestDeleteReservation:
    """Tests pour la suppression de réservations."""

    def test_delete_existing_reservation_204(self, auth_header):
        """Annuler une réservation existante renvoie 204."""
        # Créer d'abord une réservation
        create_response = client.post(
            "/salles/2/reservations",
            headers=auth_header,
            json={
                "usager": "M. Durand",
                "date": "2026-06-22",
                "heure_debut": "09:00",
                "heure_fin": "10:00"
            }
        )
        reservation_id = create_response.json()["id"]

        # Annuler cette réservation
        response = client.delete(
            f"/reservations/{reservation_id}",
            headers=auth_header
        )
        assert response.status_code == 204
        # Vérifier que la réservation est supprimée
        response = client.post(
            f"/salles/2/reservations",
            headers=auth_header,
            json={
                "usager": "Autre",
                "date": "2026-06-22",
                "heure_debut": "09:00",
                "heure_fin": "10:00"
            }
        )
        assert response.status_code == 201  # Peut créer maintenant

    def test_delete_nonexistent_reservation_404(self, auth_header):
        """Annuler une réservation inexistante renvoie 404."""
        response = client.delete(
            "/reservations/999",
            headers=auth_header
        )
        assert response.status_code == 404
        assert "non trouvée" in response.json()["detail"].lower()

    def test_delete_requires_auth(self):
        """Annuler sans token renvoie 401."""
        response = client.delete("/reservations/1")
        assert response.status_code == 401


class TestAuthentication:
    """Tests pour l'authentification."""

    def test_invalid_token_403(self):
        """Token invalide renvoie 403."""
        response = client.get(
            "/salles",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 403

    def test_missing_bearer_prefix_401(self):
        """Header sans "Bearer" renvoie 401."""
        response = client.get(
            "/salles",
            headers={"Authorization": f"{API_TOKEN}"}
        )
        assert response.status_code == 401

    def test_missing_auth_header_403(self):
        """Header Authorization manquant renvoie 403."""
        response = client.get("/salles")
        assert response.status_code in [401, 403]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
