#!/usr/bin/env python3
"""
Palier 2 - Authentification par JWT

Pourquoi passer aux JWT ?
Le palier 1 stocke tous les tokens actifs en memoire (tokens_actifs).
Avec plusieurs instances serveur, chaque instance a sa propre memoire :
un token valide sur instance A est inconnu de l'instance B.

Un JWT (JSON Web Token) resout ce probleme : il porte lui-meme les informations
(utilisateur, expiration) et sa signature cryptographique garantit qu'il n'a
pas ete modifie. Le serveur n'a plus besoin de stocker les tokens.

Structure d'un JWT : header.payload.signature
  - header    : algorithme de signature (HS256) et type (JWT)
  - payload   : claims sub (utilisateur) et exp (expiration timestamp Unix)
  - signature : HMAC-SHA256(header+payload, SECRET_KEY)
"""
from flask import Flask, jsonify, request, abort
from jose import jwt, JWTError
from datetime import datetime, timedelta

app = Flask(__name__)
SECRET_KEY = "a-changer-en-production"
ALGORITHM = "HS256"
DUREE_TOKEN_MINUTES = 30

utilisateurs_db = {
    "alice": "motdepasse123",
    "bob": "secret456",
}


def creer_jwt(username):
    """Encode un JWT avec les claims sub (utilisateur) et exp (expiration)."""
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(minutes=DUREE_TOKEN_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verifier_jwt():
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


@app.route("/auth/login", methods=["POST"])
def login():
    """Authentifie un utilisateur et retourne un access_token JWT."""
    data = request.get_json()
    if not data:
        abort(400, description="Corps JSON requis")
    username = data.get("username")
    password = data.get("password")
    if username not in utilisateurs_db or utilisateurs_db[username] != password:
        abort(401, description="Identifiants invalides")
    return jsonify({
        "access_token": creer_jwt(username),
        "token_type": "bearer"
    }), 200


@app.route("/profil", methods=["GET"])
def profil():
    """Route protegee : retourne le nom de l'utilisateur connecte."""
    username = verifier_jwt()
    return jsonify({"utilisateur": username}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5002)
