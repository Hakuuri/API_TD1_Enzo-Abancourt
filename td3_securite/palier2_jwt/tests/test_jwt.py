import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app import creer_jwt, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from datetime import datetime, timedelta


def test_creer_jwt_retourne_format_header_payload_signature():
    """Un JWT valide doit contenir exactement deux points (header.payload.signature)."""
    token = creer_jwt("alice")
    assert isinstance(token, str)
    assert token.count(".") == 2


def test_payload_contient_sub_correct():
    """Le claim 'sub' du JWT doit correspondre au nom d'utilisateur."""
    token = creer_jwt("alice")
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "alice"


def test_payload_contient_exp():
    """Le JWT doit contenir un claim 'exp' (expiration)."""
    token = creer_jwt("bob")
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert "exp" in payload


def test_mauvaise_cle_leve_jwterror():
    """Decoder un JWT avec une mauvaise cle secrete doit lever JWTError."""
    token = creer_jwt("alice")
    with pytest.raises(JWTError):
        jwt.decode(token, "mauvaise-cle-secrete", algorithms=[ALGORITHM])


def test_token_expire_est_rejete():
    """Un JWT dont l'expiration est dans le passe doit etre refuse."""
    payload = {
        "sub": "alice",
        "exp": datetime.utcnow() - timedelta(minutes=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    with pytest.raises(JWTError):
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def test_jwt_differents_pour_utilisateurs_differents():
    """Deux JWT generes pour des utilisateurs differents doivent etre distincts."""
    token_alice = creer_jwt("alice")
    token_bob = creer_jwt("bob")
    assert token_alice != token_bob


def test_sub_correct_pour_bob():
    """Le claim 'sub' doit etre correct pour un utilisateur different."""
    token = creer_jwt("bob")
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "bob"
