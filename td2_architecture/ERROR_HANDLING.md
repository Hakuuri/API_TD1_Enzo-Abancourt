# Gestion des Erreurs - API Médiathèque

## Configuration des Codes de Statut HTTP

Tous les cas d'erreur et de succès sont gérés avec les codes HTTP appropriés:

| Cas | Code HTTP | Message d'erreur | Exemple |
|-----|-----------|-----------------|---------|
| Réservation créée avec succès | **201 Created** | N/A | POST /salles/1/reservations |
| Champ date, heure_debut ou usager manquant | **400 Bad Request** | "Champs manquants" | POST avec données incomplètes |
| Token absent ou invalide | **401/403** | "Unauthorized"/"Forbidden" | Sans Authorization header |
| Salle inexistante référencée | **404 Not Found** | "Salle non trouvée" | GET /salles/999 |
| Créneau qui chevauche une réservation existante | **409 Conflict** | "Conflit: La salle X est déjà réservée sur ce créneau" | POST avec horaires conflictuels |
| Suppression d'une réservation réussie | **204 No Content** | N/A | DELETE /reservations/1 |

## Implémentation dans FastAPI

### Structure de Réponse d'Erreur

FastAPI retourne automatiquement une réponse structurée:

```json
{
  "detail": "Description de l'erreur"
}
```

Pour les erreurs de validation Pydantic (400):

```json
{
  "detail": [
    {
      "loc": ["body", "usager"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Exceptions Levées dans le Code

```python
# 404 Not Found - Salle inexistante
raise HTTPException(
    status_code=404,
    detail="Salle non trouvée"
)

# 409 Conflict - Chevauchement de créneau
raise HTTPException(
    status_code=409,
    detail="Conflit: La salle 1 est déjà réservée sur ce créneau (14:00-15:30)"
)

# 400 Bad Request - Champs manquants
raise HTTPException(
    status_code=400,
    detail="Champs manquants"
)

# 401 Unauthorized - Token absent
raise HTTPException(
    status_code=401,
    detail="Invalid token format"
)

# 403 Forbidden - Token invalide
raise HTTPException(
    status_code=403,
    detail="Token invalide"
)
```

## Cas de Test Validés

### Réservation créée avec succès (201)
```bash
curl -X POST http://localhost:8000/salles/1/reservations \
  -H "Authorization: Bearer token_mediatheque_123" \
  -H "Content-Type: application/json" \
  -d '{
    "usager": "Mme Martin",
    "date": "2026-06-21",
    "heure_debut": "10:00",
    "heure_fin": "11:30"
  }'

Response: 201 Created
{
  "id": 2,
  "salle_id": 1,
  "usager": "Mme Martin",
  "date": "2026-06-21",
  "heure_debut": "10:00",
  "heure_fin": "11:30"
}
```

### Champ manquant (400)
```bash
curl -X POST http://localhost:8000/salles/1/reservations \
  -H "Authorization: Bearer token_mediatheque_123" \
  -H "Content-Type: application/json" \
  -d '{
    "usager": "Test"
  }'

Response: 422 Unprocessable Entity (Pydantic validation)
```

### Salle inexistante (404)
```bash
curl -X POST http://localhost:8000/salles/999/reservations \
  -H "Authorization: Bearer token_mediatheque_123" \
  -H "Content-Type: application/json" \
  -d '{...}'

Response: 404 Not Found
{"detail": "Salle non trouvée"}
```

### Créneau en conflit (409)
```bash
curl -X POST http://localhost:8000/salles/1/reservations \
  -H "Authorization: Bearer token_mediatheque_123" \
  -H "Content-Type: application/json" \
  -d '{
    "usager": "M. Test",
    "date": "2026-06-20",
    "heure_debut": "14:15",
    "heure_fin": "15:00"
  }'

Response: 409 Conflict
{"detail": "Conflit: La salle 1 est déjà réservée sur ce créneau (14:00-15:30)"}
```

### Token invalide (403)
```bash
curl -X GET http://localhost:8000/salles \
  -H "Authorization: Bearer invalid_token"

Response: 403 Forbidden
{"detail": "Token invalide"}
```

### Suppression réussie (204)
```bash
curl -X DELETE http://localhost:8000/reservations/1 \
  -H "Authorization: Bearer token_mediatheque_123"

Response: 204 No Content (aucun corps de réponse)
```

## Points Clés de Sécurité

1. **Authentification obligatoire**: Tous les endpoints vérifient le token Bearer
2. **Validation côté serveur**: Les champs sont validés même si validés côté client
3. **Messages d'erreur explicites**: Le client peut comprendre et réagir correctement
4. **Codes HTTP sémantiques**: Chaque situation a son code approprié
