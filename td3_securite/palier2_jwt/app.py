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
