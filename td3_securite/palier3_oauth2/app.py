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
