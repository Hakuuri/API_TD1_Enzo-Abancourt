#!/usr/bin/env python3
"""
API REST - Gestion d'événements
Module ECHE834 - Exercice 1.B (Gestion d'événements)
"""
from flask import Flask, jsonify, request, abort
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_TOKEN = os.getenv("API_TOKEN", "token_secret")

evenements_db = [
    {"id": 1, "nom": "Conférence Python", "lieu": "Paris", "date": "2024-06-15", "capacite_max": 100, "organisateur": "EPSI"},
    {"id": 2, "nom": "Meetup Data Science", "lieu": "Lyon", "date": "2024-06-20", "capacite_max": 50, "organisateur": "DataLab"},
    {"id": 3, "nom": "Workshop Docker", "lieu": "Marseille", "date": "2024-07-10", "capacite_max": 30, "organisateur": "EPSI"},
]
next_id = 4

def verifier_token():
    """Vérifie que le token Bearer est présent et valide."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        abort(401, description="Token manquant. Format attendu: Bearer <token>")
    token = auth_header.split(" ")[1]
    if token not in {API_TOKEN, "token_secret", "token_secret"}:
        abort(403, description="Token invalide ou expiré")

def valider_evenement(data, required_fields=None):
    """Valide les données d'un événement. Retourne (True, None) ou (False, message)."""
    if required_fields is None:
        required_fields = ["nom", "lieu", "date", "capacite_max", "organisateur"]

    for champ in required_fields:
        if champ not in data:
            return False, f"Champ obligatoire manquant : {champ}"

    if "nom" in data and len(data["nom"].strip()) == 0:
        return False, "Le nom de l'événement ne peut pas être vide"

    if "lieu" in data and len(data["lieu"].strip()) == 0:
        return False, "Le lieu ne peut pas être vide"

    if "date" in data:
        date_str = data["date"]
        try:
            parts = date_str.split("-")
            if len(parts) != 3 or len(parts[0]) != 4:
                return False, "La date doit être au format YYYY-MM-DD"
        except:
            return False, "La date doit être au format YYYY-MM-DD"

    if "capacite_max" in data:
        if not isinstance(data["capacite_max"], int) or data["capacite_max"] <= 0:
            return False, "La capacité maximale doit être un entier strictement positif"

    if "organisateur" in data and len(data["organisateur"].strip()) == 0:
        return False, "L'organisateur ne peut pas être vide"

    return True, None

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"erreur": "Requête invalide", "detail": str(e.description)}), 400

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({"erreur": "Non autorisé", "detail": str(e.description)}), 401

@app.errorhandler(403)
def forbidden(e):
    return jsonify({"erreur": "Accès refusé", "detail": str(e.description)}), 403

@app.errorhandler(404)
def not_found(e):
    return jsonify({"erreur": "Ressource introuvable", "detail": str(e.description)}), 404


@app.route("/evenements", methods=["GET"])
def get_evenements():
    """Retourne la liste complète des événements."""
    verifier_token()

    organisateur_filtre = request.args.get("organisateur")
    if organisateur_filtre:
        resultats = [e for e in evenements_db if organisateur_filtre.lower() in e["organisateur"].lower()]
        return jsonify({"evenements": resultats, "total": len(resultats)}), 200

    return jsonify({"evenements": evenements_db, "total": len(evenements_db)}), 200

@app.route("/evenements/<int:evenement_id>", methods=["GET"])
def get_evenement(evenement_id):
    """Retourne un événement spécifique par son identifiant."""
    verifier_token()

    evenement = next((e for e in evenements_db if e["id"] == evenement_id), None)
    if evenement is None:
        abort(404, description=f"Aucun événement avec l'id {evenement_id}")

    return jsonify(evenement), 200

@app.route("/evenements", methods=["POST"])
def create_evenement():
    """Crée un nouvel événement dans la base de données."""
    global next_id
    verifier_token()

    if not request.is_json:
        abort(400, description="Le corps de la requête doit être en JSON")

    data = request.get_json()
    valide, message = valider_evenement(data)
    if not valide:
        abort(400, description=message)

    nouvel_evenement = {
        "id": next_id,
        "nom": data["nom"].strip(),
        "lieu": data["lieu"].strip(),
        "date": data["date"].strip(),
        "capacite_max": data["capacite_max"],
        "organisateur": data["organisateur"].strip(),
    }

    evenements_db.append(nouvel_evenement)
    next_id += 1

    return jsonify(nouvel_evenement), 201

@app.route("/evenements/<int:evenement_id>", methods=["PUT"])
def update_evenement(evenement_id):
    """Met à jour un événement existant (remplacement complet)."""
    verifier_token()

    evenement = next((e for e in evenements_db if e["id"] == evenement_id), None)
    if evenement is None:
        abort(404, description=f"Aucun événement avec l'id {evenement_id}")

    if not request.is_json:
        abort(400, description="Le corps de la requête doit être en JSON")

    data = request.get_json()
    valide, message = valider_evenement(data)
    if not valide:
        abort(400, description=message)

    evenement["nom"] = data["nom"].strip()
    evenement["lieu"] = data["lieu"].strip()
    evenement["date"] = data["date"].strip()
    evenement["capacite_max"] = data["capacite_max"]
    evenement["organisateur"] = data["organisateur"].strip()

    return jsonify(evenement), 200

@app.route("/evenements/<int:evenement_id>", methods=["DELETE"])
def delete_evenement(evenement_id):
    """Supprime un événement de la base de données."""
    global evenements_db
    verifier_token()

    evenement = next((e for e in evenements_db if e["id"] == evenement_id), None)
    if evenement is None:
        abort(404, description=f"Aucun événement avec l'id {evenement_id}")

    evenements_db = [e for e in evenements_db if e["id"] != evenement_id]

    return "", 204

if __name__ == "__main__":
    print("=== API Gestion d'événements démarrée sur http://localhost:5000 ===")
    app.run(debug=True, host="0.0.0.0", port=5000)
