#!/usr/bin/env python3
"""API REST - Carnet de contacts (FastAPI)"""
from fastapi import FastAPI, HTTPException, Header, Query, status
from pydantic import BaseModel, EmailStr
from typing import Optional, List

app = FastAPI(title="API Contacts")

API_TOKEN = "mon_token_secret_123"


class Contact(BaseModel):
    id: int
    nom: str
    email: EmailStr
    telephone: Optional[str] = None
    favori: bool = False


class ContactInput(BaseModel):
    nom: str
    email: EmailStr
    telephone: Optional[str] = None
    favori: bool = False


contacts_db: List[dict] = [
    {"id": 1, "nom": "Aïcha Diallo", "email": "aicha@exemple.fr",
     "telephone": "0601020304", "favori": True},
]

next_id = 2


def verifier_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    token = authorization[7:]
    if token != API_TOKEN:
        raise HTTPException(status_code=403, detail="Token invalide")


@app.get("/contacts", response_model=List[Contact])
async def list_contacts(authorization: str = Header(...), favori: Optional[bool] = Query(None)):
    verifier_token(authorization)
    result = contacts_db

    if favori is not None:
        result = [c for c in contacts_db if c["favori"] == favori]

    return result


@app.get("/contacts/{contact_id}", response_model=Contact)
async def get_contact(contact_id: int, authorization: str = Header(...)):
    verifier_token(authorization)
    contact = next((c for c in contacts_db if c["id"] == contact_id), None)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact non trouvé")
    return contact


@app.post("/contacts", response_model=Contact, status_code=status.HTTP_201_CREATED)
async def create_contact(contact: ContactInput, authorization: str = Header(...)):
    global next_id
    verifier_token(authorization)

    new_contact = {
        "id": next_id,
        "nom": contact.nom,
        "email": contact.email,
        "telephone": contact.telephone,
        "favori": contact.favori
    }

    contacts_db.append(new_contact)
    next_id += 1
    return new_contact


@app.put("/contacts/{contact_id}", response_model=Contact)
async def update_contact(contact_id: int, contact: ContactInput, authorization: str = Header(...)):
    verifier_token(authorization)
    existing = next((c for c in contacts_db if c["id"] == contact_id), None)
    if not existing:
        raise HTTPException(status_code=404, detail="Contact non trouvé")

    existing["nom"] = contact.nom
    existing["email"] = contact.email
    existing["telephone"] = contact.telephone
    existing["favori"] = contact.favori

    return existing


@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, authorization: str = Header(...)):
    global contacts_db
    verifier_token(authorization)
    existing = next((c for c in contacts_db if c["id"] == contact_id), None)
    if not existing:
        raise HTTPException(status_code=404, detail="Contact non trouvé")

    contacts_db = [c for c in contacts_db if c["id"] != contact_id]
    return None
