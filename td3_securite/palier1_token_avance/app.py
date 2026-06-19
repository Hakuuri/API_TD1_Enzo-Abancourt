#!/usr/bin/env python3
"""
Palier 1 - Token avec expiration et revocation

Probleme resolu par ce palier :
- Au TD1/TD2, un seul token statique pour tous les utilisateurs, sans expiration
  ni revocation. En production, cela signifie qu'un token vole reste valide
  indefiniment et qu'on ne peut pas identifier qui est connecte.

Ce palier introduit :
- Un token aleatoire unique par session utilisateur
- Une date d'expiration associee (30 minutes)
- Un endpoint de revocation (/auth/logout) pour invalider avant expiration
"""
from flask import Flask, jsonify, request, abort
import secrets
from datetime import datetime, timedelta

app = Flask(__name__)

# Base d'utilisateurs (en production : table en base de donnees)
utilisateurs_db = {
    "alice": "motdepasse123",
    "bob": "secret456",
}

# Tokens actifs : { token: {"user": ..., "expire_le": ...} }
tokens_actifs = {}
DUREE_TOKEN_MINUTES = 30


def generer_token(username):
    """Genere un token aleatoire securise et l'enregistre avec son expiration."""
    token = secrets.token_hex(32)
    tokens_actifs[token] = {
        "user": username,
        "expire_le": datetime.utcnow() + timedelta(minutes=DUREE_TOKEN_MINUTES)
    }
    return token


def verifier_token():
    """Verifie le token Bearer : presence, existence, expiration."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        abort(401, description="Token manquant")
    token = auth_header.split(" ")[1]
    if token not in tokens_actifs:
        abort(403, description="Token invalide")
    info = tokens_actifs[token]
    if info["expire_le"] < datetime.utcnow():
        del tokens_actifs[token]
        abort(401, description="Token expire")
    return info["user"]


@app.route("/auth/login", methods=["POST"])
def login():
    """Authentifie un utilisateur et retourne un nouveau token."""
    data = request.get_json()
    if not data:
        abort(400, description="Corps JSON requis")
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        abort(400, description="username et password requis")
    if username not in utilisateurs_db or utilisateurs_db[username] != password:
        abort(401, description="Identifiants invalides")
    token = generer_token(username)
    return jsonify({"token": token, "expire_dans_minutes": DUREE_TOKEN_MINUTES}), 200


@app.route("/auth/logout", methods=["POST"])
def logout():
    """Revoque le token actuel avant son expiration naturelle."""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.split(" ")[1] if " " in auth_header else None
    if token and token in tokens_actifs:
        del tokens_actifs[token]
    return "", 204


@app.route("/profil", methods=["GET"])
def profil():
    """Route protegee : retourne le nom de l'utilisateur connecte."""
    username = verifier_token()
    return jsonify({"utilisateur": username}), 200


@app.errorhandler(400)
def bad_request(e):
    return jsonify({"erreur": str(e.description)}), 400


@app.errorhandler(401)
def non_autorise(e):
    return jsonify({"erreur": str(e.description)}), 401


@app.errorhandler(403)
def interdit(e):
    return jsonify({"erreur": str(e.description)}), 403


if __name__ == "__main__":
    app.run(debug=True, port=5001)
