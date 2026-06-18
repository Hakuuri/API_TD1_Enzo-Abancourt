#!/usr/bin/env python3
"""API REST - Carnet de contacts (Flask)"""
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

API_TOKEN = "mon_token_secret_123"

contacts_db = [
    {"id": 1, "nom": "Aïcha Diallo", "email": "aicha@exemple.fr",
     "telephone": "0601020304", "favori": True},
]

next_id = 2


def verifier_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        abort(401)
    token = auth_header[7:]
    if token != API_TOKEN:
        abort(403)


def valider_contact(data, required_fields=None):
    if required_fields is None:
        required_fields = ["nom", "email"]

    for field in required_fields:
        if field not in data or not data[field]:
            abort(400)

    if "@" not in data.get("email", ""):
        abort(400)


@app.route("/contacts", methods=["GET"])
def list_contacts():
    verifier_token()
    favori = request.args.get("favori")
    result = contacts_db

    if favori is not None:
        favori_bool = favori.lower() == "true"
        result = [c for c in contacts_db if c["favori"] == favori_bool]

    return jsonify(result), 200


@app.route("/contacts/<int:contact_id>", methods=["GET"])
def get_contact(contact_id):
    verifier_token()
    contact = next((c for c in contacts_db if c["id"] == contact_id), None)
    if not contact:
        abort(404)
    return jsonify(contact), 200


@app.route("/contacts", methods=["POST"])
def create_contact():
    global next_id
    verifier_token()
    data = request.get_json() or {}

    valider_contact(data)

    new_contact = {
        "id": next_id,
        "nom": data["nom"],
        "email": data["email"],
        "telephone": data.get("telephone"),
        "favori": data.get("favori", False)
    }

    contacts_db.append(new_contact)
    next_id += 1
    return jsonify(new_contact), 201


@app.route("/contacts/<int:contact_id>", methods=["PUT"])
def update_contact(contact_id):
    verifier_token()
    contact = next((c for c in contacts_db if c["id"] == contact_id), None)
    if not contact:
        abort(404)

    data = request.get_json() or {}
    valider_contact(data, required_fields=[])

    if "nom" in data:
        contact["nom"] = data["nom"]
    if "email" in data:
        if "@" not in data["email"]:
            abort(400)
        contact["email"] = data["email"]
    if "telephone" in data:
        contact["telephone"] = data["telephone"]
    if "favori" in data:
        contact["favori"] = data["favori"]

    return jsonify(contact), 200


@app.route("/contacts/<int:contact_id>", methods=["DELETE"])
def delete_contact(contact_id):
    verifier_token()
    global contacts_db
    contact = next((c for c in contacts_db if c["id"] == contact_id), None)
    if not contact:
        abort(404)

    contacts_db = [c for c in contacts_db if c["id"] != contact_id]
    return "", 204


if __name__ == "__main__":
    app.run(debug=True, port=5000)
