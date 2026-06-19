import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import generer_token, tokens_actifs
from datetime import datetime, timedelta


def test_generer_token_cree_une_entree():
    """Le token genere doit etre present dans tokens_actifs."""
    token = generer_token("alice")
    assert token in tokens_actifs


def test_token_associe_au_bon_utilisateur():
    """Le token doit etre associe au bon nom d'utilisateur."""
    token = generer_token("alice")
    assert tokens_actifs[token]["user"] == "alice"


def test_token_a_une_expiration_future():
    """La date d'expiration du token doit etre dans le futur."""
    token = generer_token("alice")
    assert tokens_actifs[token]["expire_le"] > datetime.utcnow()


def test_deux_tokens_sont_differents():
    """Deux appels successifs a generer_token produisent des tokens distincts."""
    token1 = generer_token("alice")
    token2 = generer_token("alice")
    assert token1 != token2


def test_token_est_une_chaine_hexadecimale():
    """Le token doit etre une chaine hexadecimale de 64 caracteres."""
    token = generer_token("alice")
    assert isinstance(token, str)
    assert len(token) == 64
    assert all(c in "0123456789abcdef" for c in token)


def test_token_expiration_dans_30_minutes():
    """La duree de vie du token doit etre d'environ 30 minutes."""
    avant = datetime.utcnow() + timedelta(minutes=29)
    token = generer_token("alice")
    apres = datetime.utcnow() + timedelta(minutes=31)
    assert avant < tokens_actifs[token]["expire_le"] < apres
