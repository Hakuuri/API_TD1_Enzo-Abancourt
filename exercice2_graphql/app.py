"""
Application FastAPI + GraphQL (Strawberry)
Module ECHE834 - Exercice 2.B (Gestion d'événements)
"""
from fastapi import FastAPI, Depends, HTTPException, Header
from strawberry.fastapi import GraphQLRouter
from exercice2_graphql.schema import schema
import os
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN", "token_secret")

# Configuration FastAPI
app = FastAPI(title="API GraphQL - Gestion d'événements", version="1.0.0")

# Dépendance : Vérification du token Bearer
def verifier_token(authorization: str = Header(...)):
    """Dépendance FastAPI pour la vérification du token."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Format: Bearer <token>")
    token = authorization.split(" ")[1]
    if token != API_TOKEN:
        raise HTTPException(status_code=403, detail="Token invalide")

# Routeur GraphQL — accessible via /graphql
graphql_router = GraphQLRouter(
    schema,
    dependencies=[Depends(verifier_token)]
)
app.include_router(graphql_router, prefix="/graphql")

# Endpoint de bienvenue
@app.get("/")
async def root():
    return {
        "message": "API GraphQL Gestion d'événements opérationnelle",
        "docs": "/graphql",
        "version": "1.0.0"
    }

# Point d'entrée de l'application
if __name__ == "__main__":
    import uvicorn
    print("=== API GraphQL Gestion d'événements démarrée sur http://localhost:8000 ===")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
