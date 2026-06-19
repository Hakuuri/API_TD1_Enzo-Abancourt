#!/usr/bin/env python3
"""
Palier 3 - OAuth2 simplifie (Authorization Code Flow + JWT)

Contexte : une start-up developpe une marketplace de livres d'occasion.
Des applications partenaires (comparateur de prix, app mobile) doivent
acceder a l'API au nom d'un utilisateur, sans jamais connaitre son mot de passe.

Flux OAuth2 Authorization Code implemente :
  1. POST /oauth/authorize : utilisateur + client_id -> code d'autorisation (60s, usage unique)
  2. POST /oauth/token    : code + client_id + client_secret -> access_token (JWT 15min) + refresh_token (7j)
  3. POST /oauth/refresh  : refresh_token -> nouvel access_token
  4. GET  /profil         : endpoint protege par access_token

Clients autorises :
  - app_comparateur / secret_comparateur
  - app_mobile      / secret_mobile
"""
from flask import Flask, jsonify, request, abort
from jose import jwt, JWTError
import secrets
from datetime import datetime, timedelta

app = Flask(__name__)
SECRET_KEY = "a-changer-en-production"
ALGORITHM = "HS256"
DUREE_ACCESS_TOKEN_MINUTES = 15
DUREE_REFRESH_TOKEN_JOURS = 7
DUREE_CODE_AUTORISATION_SECONDES = 60

utilisateurs_db = {
    "alice": "motdepasse123",
    "bob": "secret456",
}

clients_autorises = {
    "app_comparateur": "secret_comparateur",
    "app_mobile": "secret_mobile",
}

codes_autorisation = {}
refresh_tokens = {}


def creer_access_token(username):
    """Encode un JWT access_token avec sub et exp (15 minutes)."""
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(minutes=DUREE_ACCESS_TOKEN_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verifier_access_token():
    """Decode et valide le JWT Bearer de la requete. Retourne le username."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        abort(401, description="Token manquant")
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except JWTError:
        abort(401, description="Token invalide ou expire")


@app.route("/oauth/authorize", methods=["POST"])
def authorize():
    """Genere un code d'autorisation a usage unique valable 60 secondes."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    client_id = data.get("client_id")

    if username not in utilisateurs_db or utilisateurs_db[username] != password:
        abort(401, description="Identifiants utilisateur invalides")

    if client_id not in clients_autorises:
        abort(401, description="client_id invalide")

    code = secrets.token_hex(16)
    codes_autorisation[code] = {
        "username": username,
        "client_id": client_id,
        "expire_le": datetime.utcnow() + timedelta(seconds=DUREE_CODE_AUTORISATION_SECONDES),
        "utilise": False
    }
    return jsonify({"code": code}), 200


@app.route("/oauth/token", methods=["POST"])
def token():
    """Echange un code d'autorisation contre access_token et refresh_token."""
    data = request.get_json()
    code = data.get("code")
    client_id = data.get("client_id")
    client_secret = data.get("client_secret")

    if client_id not in clients_autorises or clients_autorises[client_id] != client_secret:
        abort(401, description="client_id ou client_secret invalide")

    if code not in codes_autorisation:
        abort(400, description="Code d'autorisation invalide")

    info_code = codes_autorisation[code]

    if info_code["utilise"]:
        abort(400, description="Code d'autorisation deja utilise")

    if info_code["expire_le"] < datetime.utcnow():
        del codes_autorisation[code]
        abort(400, description="Code d'autorisation expire")

    if info_code["client_id"] != client_id:
        abort(401, description="client_id ne correspond pas au code emis")

    codes_autorisation[code]["utilise"] = True
    username = info_code["username"]
    access_token = creer_access_token(username)

    refresh_token = secrets.token_hex(32)
    refresh_tokens[refresh_token] = {
        "username": username,
        "expire_le": datetime.utcnow() + timedelta(days=DUREE_REFRESH_TOKEN_JOURS)
    }

    return jsonify({
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "expires_in": DUREE_ACCESS_TOKEN_MINUTES * 60
    }), 200
