"""
API REST - Gestion des réservations de salles (Médiathèque)

ÉTAPE 1 — MODÉLISATION DES RESSOURCES

1. Quelles sont les ressources principales de ce système ? Combien y en a-t-il ?

   RÉPONSE: Deux ressources principales:
   - Salles (rooms)
   - Réservations (reservations)

   Les salles représentent les espaces physiques disponibles.
   Les réservations représentent les occupations de ces salles sur des créneaux.

2. Une réservation est-elle une ressource indépendante, ou une sous-ressource d'une salle ? Justifiez.

   RÉPONSE: Une réservation est une SUB-RESSOURCE d'une salle.

   JUSTIFICATION:
   - Une réservation n'existe que dans le contexte d'une salle
   - Son cycle de vie dépend de l'existence de la salle
   - Les patterns REST courants pour ce cas: POST /salles/{id}/reservations
   - Cependant, pour la suppression, on peut aussi autoriser DELETE /reservations/{id}
     car l'ID est suffisant pour identifier la réservation de manière unique
   - Compromis: structure hiérarchique pour création, identifiant global pour suppression

3. Quelles URLs utiliseriez-vous pour:

   a) Lister toutes les salles ?
      → GET /salles
      → Retourne: Liste de toutes les salles avec capacité et équipement

   b) Lister les réservations d'une salle précise ?
      → GET /salles/{id}/reservations
      → Retourne: Liste des réservations de la salle spécifiée
      → Paramètres optionnels: ?date=2026-06-20 pour filtrer par date

   c) Créer une réservation ?
      → POST /salles/{id}/reservations
      → Body: { usager, date, heure_debut, heure_fin }
      → Retourne: 201 Created avec la réservation créée (id inclus)

   d) Lister UNE réservation spécifique (bonus) ?
      → GET /reservations/{id}
      → Alternative: GET /salles/{id}/reservations/{res_id}
      → Préférer la première pour éviter imbrication > 2 niveaux

4. Quelle méthode HTTP et quel code de statut pour annuler une réservation ?

   RÉPONSE:
   - Méthode HTTP: DELETE
   - Code de statut: 204 No Content
   - URL: DELETE /reservations/{id}

   JUSTIFICATION:
   - DELETE est la méthode standard pour la suppression
   - 204 No Content car aucune ressource n'est retournée après suppression
   - Utiliser /reservations/{id} plutôt que /salles/{id}/reservations/{id}
     pour éviter l'imbrication excessive (règle max 2 niveaux)

RÉSUMÉ DE L'ARCHITECTURE

Ressources et endpoints:

GET /salles                              → Lister toutes les salles
GET /salles/{id}                         → Détail d'une salle
GET /salles/{id}/reservations            → Lister les réservations d'une salle
POST /salles/{id}/reservations           → Créer une réservation
DELETE /reservations/{id}                → Annuler une réservation

Codes de statut utilisés:
- 200 OK: Lecture réussie
- 201 Created: Réservation créée
- 204 No Content: Suppression réussie
- 400 Bad Request: Champs manquants ou mal formés
- 401/403: Authentification/autorisation
- 404 Not Found: Salle ou réservation inexistante
- 409 Conflict: Chevauchement de créneau

Validations côté serveur:
- Une salle doit exister avant de pouvoir créer une réservation sur celle-ci
- Les horaires doivent être valides (heure_fin > heure_debut)
- Aucun chevauchement de créneau sur la même salle et même date
"""

# Base de données (données brutes)
salles_db = [
    {"id": 1, "nom": "Salle Voltaire", "capacite": 12,
     "equipement": ["vidéoprojecteur", "tableau blanc"]},
    {"id": 2, "nom": "Salle Curie", "capacite": 6,
     "equipement": ["écran TV"]},
]

reservations_db = [
    {"id": 1, "salle_id": 1, "usager": "M. Dupont",
     "date": "2026-06-20", "heure_debut": "14:00", "heure_fin": "15:30"},
]
