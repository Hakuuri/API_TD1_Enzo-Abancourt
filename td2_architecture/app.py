#!/usr/bin/env python3
"""
API REST - Gestion des réservations de salles (Médiathèque)

Framework choisi: FastAPI
Justification: Validation stricte Pydantic nécessaire, documentation Swagger requise,
              gestion des codes 409 Conflict pour chevauchement de créneaux.
"""

from fastapi import FastAPI, HTTPException, status, Header
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

app = FastAPI(
    title="API Médiathèque - Réservations de Salles",
    description="Gestion des salles et réservations de la médiathèque municipale"
)

API_TOKEN = "token_mediatheque_123"


class Equipement(BaseModel):
    pass


class Salle(BaseModel):
    id: int
    nom: str
    capacite: int
    equipement: List[str]


class ReservationInput(BaseModel):
    usager: str
    date: str
    heure_debut: str
    heure_fin: str


class Reservation(BaseModel):
    id: int
    salle_id: int
    usager: str
    date: str
    heure_debut: str
    heure_fin: str


salles_db = [
    {"id": 1, "nom": "Salle Voltaire", "capacite": 12,
     "equipement": ["vidéoprojecteur", "tableau blanc"]},
    {"id": 2, "nom": "Salle Curie", "capacite": 6,
     "equipement": ["écran TV"]},
]

reservations_db = [
    {"id": 1, "salle_id": 1, "usager": "M. Dupont",
     "date": "2026-06-20", "heure_debut": "14:00", "heure_fin": "15:30"},
]

next_reservation_id = 2


def verifier_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    token = authorization[7:]
    if token != API_TOKEN:
        raise HTTPException(status_code=403, detail="Token invalide")


def heures_se_chevauchent(h1_debut: str, h1_fin: str, h2_debut: str, h2_fin: str) -> bool:
    """Vérifie si deux créneaux horaires se chevauchent."""
    def time_to_minutes(heure: str) -> int:
        parts = heure.split(":")
        return int(parts[0]) * 60 + int(parts[1])

    h1_debut_min = time_to_minutes(h1_debut)
    h1_fin_min = time_to_minutes(h1_fin)
    h2_debut_min = time_to_minutes(h2_debut)
    h2_fin_min = time_to_minutes(h2_fin)

    return not (h1_fin_min <= h2_debut_min or h2_fin_min <= h1_debut_min)


def verifier_chevauchement(salle_id: int, date: str, heure_debut: str, heure_fin: str):
    """Vérifie qu'aucune réservation existante ne chevauche ce créneau."""
    reservations_salle = [r for r in reservations_db if r["salle_id"] == salle_id and r["date"] == date]

    for res in reservations_salle:
        if heures_se_chevauchent(heure_debut, heure_fin, res["heure_debut"], res["heure_fin"]):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Conflit: La salle {salle_id} est déjà réservée sur ce créneau ({res['heure_debut']}-{res['heure_fin']})"
            )


@app.get("/salles", response_model=List[Salle], status_code=status.HTTP_200_OK)
async def list_salles(authorization: str = Header(...)):
    """Lister toutes les salles disponibles."""
    verifier_token(authorization)
    return salles_db


@app.get("/salles/{salle_id}", response_model=Salle, status_code=status.HTTP_200_OK)
async def get_salle(salle_id: int, authorization: str = Header(...)):
    """Récupérer les détails d'une salle."""
    verifier_token(authorization)
    salle = next((s for s in salles_db if s["id"] == salle_id), None)
    if not salle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salle non trouvée")
    return salle


@app.get("/salles/{salle_id}/reservations", response_model=List[Reservation], status_code=status.HTTP_200_OK)
async def list_reservations_salle(salle_id: int, authorization: str = Header(...)):
    """Lister toutes les réservations d'une salle."""
    verifier_token(authorization)

    salle = next((s for s in salles_db if s["id"] == salle_id), None)
    if not salle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salle non trouvée")

    return [r for r in reservations_db if r["salle_id"] == salle_id]


@app.post("/salles/{salle_id}/reservations", response_model=Reservation, status_code=status.HTTP_201_CREATED)
async def create_reservation(salle_id: int, reservation: ReservationInput, authorization: str = Header(...)):
    """Créer une réservation pour une salle."""
    global next_reservation_id
    verifier_token(authorization)

    # Vérifier que la salle existe
    salle = next((s for s in salles_db if s["id"] == salle_id), None)
    if not salle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salle non trouvée")

    # Vérifier les champs obligatoires
    if not reservation.usager or not reservation.date or not reservation.heure_debut or not reservation.heure_fin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Champs manquants")

    # Vérifier le chevauchement
    verifier_chevauchement(salle_id, reservation.date, reservation.heure_debut, reservation.heure_fin)

    # Créer la réservation
    new_reservation = {
        "id": next_reservation_id,
        "salle_id": salle_id,
        "usager": reservation.usager,
        "date": reservation.date,
        "heure_debut": reservation.heure_debut,
        "heure_fin": reservation.heure_fin
    }

    reservations_db.append(new_reservation)
    next_reservation_id += 1

    return new_reservation


@app.delete("/reservations/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reservation(reservation_id: int, authorization: str = Header(...)):
    """Annuler une réservation."""
    global reservations_db
    verifier_token(authorization)

    reservation = next((r for r in reservations_db if r["id"] == reservation_id), None)
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Réservation non trouvée")

    reservations_db = [r for r in reservations_db if r["id"] != reservation_id]
    return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
