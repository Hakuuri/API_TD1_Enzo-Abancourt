import strawberry
from typing import Optional, List


@strawberry.type
class Evenement:
    id: int
    nom: str
    lieu: str
    date: str
    capacite_max: int
    organisateur: str

@strawberry.input
class EvenementInput:
    nom: str
    lieu: str
    date: str
    capacite_max: int
    organisateur: str

@strawberry.type
class DeleteResult:
    success: bool
    message: str

evenements_db: List[dict] = [
    {"id": 1, "nom": "Conférence Python", "lieu": "Paris", "date": "2024-06-15", "capacite_max": 100, "organisateur": "EPSI"},
    {"id": 2, "nom": "Meetup Data Science", "lieu": "Lyon", "date": "2024-06-20", "capacite_max": 50, "organisateur": "DataLab"},
    {"id": 3, "nom": "Workshop Docker", "lieu": "Marseille", "date": "2024-07-10", "capacite_max": 30, "organisateur": "EPSI"},
]
_next_id = 4

def dict_to_evenement(d: dict) -> Evenement:
    return Evenement(
        id=d["id"],
        nom=d["nom"],
        lieu=d["lieu"],
        date=d["date"],
        capacite_max=d["capacite_max"],
        organisateur=d["organisateur"]
    )

@strawberry.type
class Query:
    @strawberry.field(description="Retourne tous les événements (filtre optionnel par organisateur)")
    def evenements(self, organisateur: Optional[str] = None) -> List[Evenement]:
        if organisateur:
            return [dict_to_evenement(e) for e in evenements_db
                    if organisateur.lower() in e["organisateur"].lower()]
        return [dict_to_evenement(e) for e in evenements_db]

    @strawberry.field(description="Retourne un événement par son identifiant")
    def evenement(self, id: int) -> Optional[Evenement]:
        evenement = next((e for e in evenements_db if e["id"] == id), None)
        return dict_to_evenement(evenement) if evenement else None

@strawberry.type
class Mutation:
    @strawberry.mutation(description="Crée un nouvel événement")
    def creer_evenement(self, evenement_input: EvenementInput) -> Evenement:
        global _next_id

        # Validation
        if not (1000 <= int(evenement_input.date.split("-")[0]) <= 2100):
            raise ValueError("L'année de la date doit être valide")
        if not evenement_input.nom.strip():
            raise ValueError("Le nom de l'événement ne peut pas être vide")
        if not evenement_input.lieu.strip():
            raise ValueError("Le lieu ne peut pas être vide")
        if not evenement_input.organisateur.strip():
            raise ValueError("L'organisateur ne peut pas être vide")
        if evenement_input.capacite_max <= 0:
            raise ValueError("La capacité maximale doit être strictement positive")

        try:
            parts = evenement_input.date.split("-")
            if len(parts) != 3 or len(parts[0]) != 4:
                raise ValueError("La date doit être au format YYYY-MM-DD")
        except:
            raise ValueError("La date doit être au format YYYY-MM-DD")

        nouveau = {
            "id": _next_id,
            "nom": evenement_input.nom.strip(),
            "lieu": evenement_input.lieu.strip(),
            "date": evenement_input.date.strip(),
            "capacite_max": evenement_input.capacite_max,
            "organisateur": evenement_input.organisateur.strip(),
        }
        evenements_db.append(nouveau)
        _next_id += 1
        return dict_to_evenement(nouveau)

    @strawberry.mutation(description="Modifie un événement existant")
    def modifier_evenement(self, id: int, evenement_input: EvenementInput) -> Optional[Evenement]:
        evenement = next((e for e in evenements_db if e["id"] == id), None)
        if evenement is None:
            return None

        # Validation
        if not evenement_input.nom.strip():
            raise ValueError("Le nom de l'événement ne peut pas être vide")
        if not evenement_input.lieu.strip():
            raise ValueError("Le lieu ne peut pas être vide")
        if not evenement_input.organisateur.strip():
            raise ValueError("L'organisateur ne peut pas être vide")
        if evenement_input.capacite_max <= 0:
            raise ValueError("La capacité maximale doit être strictement positive")

        try:
            parts = evenement_input.date.split("-")
            if len(parts) != 3 or len(parts[0]) != 4:
                raise ValueError("La date doit être au format YYYY-MM-DD")
        except:
            raise ValueError("La date doit être au format YYYY-MM-DD")

        evenement["nom"] = evenement_input.nom.strip()
        evenement["lieu"] = evenement_input.lieu.strip()
        evenement["date"] = evenement_input.date.strip()
        evenement["capacite_max"] = evenement_input.capacite_max
        evenement["organisateur"] = evenement_input.organisateur.strip()
        return dict_to_evenement(evenement)

    @strawberry.mutation(description="Supprime un événement")
    def supprimer_evenement(self, id: int) -> DeleteResult:
        global evenements_db
        avant = len(evenements_db)
        evenements_db = [e for e in evenements_db if e["id"] != id]
        if len(evenements_db) < avant:
            return DeleteResult(success=True, message=f"Événement {id} supprimé")
        return DeleteResult(success=False, message=f"Événement {id} introuvable")

schema = strawberry.Schema(query=Query, mutation=Mutation)
