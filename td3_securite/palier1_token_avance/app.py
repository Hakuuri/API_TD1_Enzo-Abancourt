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
