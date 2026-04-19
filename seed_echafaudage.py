"""
Seed échafaudage multidirectionnel
Conforme EN 12810 / EN 12811
Système type Ringlock / Rosett
"""

from database import SessionLocal
from models import Company, Article


def create_articles():
    db = SessionLocal()

    try:
        company = db.query(Company).first()
        if not company:
            print("❌ Aucune entreprise trouvée")
            return

        company_id = company.id
        print(f"✅ Entreprise : {company.name}")

        # ================== MONTANTS ==================
        montants = [
            {"nom": "Montant multidirectionnel 0.5m", "hauteur": 0.5, "poids": 6.5, "quantite": 80},
            {"nom": "Montant multidirectionnel 1.0m", "hauteur": 1.0, "poids": 11.0, "quantite": 120},
            {"nom": "Montant multidirectionnel 1.5m", "hauteur": 1.5, "poids": 15.5, "quantite": 100},
            {"nom": "Montant multidirectionnel 2.0m", "hauteur": 2.0, "poids": 20.0, "quantite": 300},
        ]

        # ================== LISSES ==================
        lisses = [
            {"nom": "Lisse multidirectionnelle 2.07m", "longueur": 2.07, "poids": 13.5, "quantite": 300},
            {"nom": "Lisse multidirectionnelle 2.57m", "longueur": 2.57, "poids": 16.0, "quantite": 200},
            {"nom": "Lisse multidirectionnelle 3.07m", "longueur": 3.07, "poids": 18.5, "quantite": 150},
        ]

        # ================== TRAVERSES ==================
        traverses = [
            {"nom": "Traverse plancher 0.73m", "longueur": 0.73, "poids": 6.8, "quantite": 250},
            {"nom": "Traverse plancher 1.09m", "longueur": 1.09, "poids": 8.5, "quantite": 200},
        ]

        # ================== DIAGONALES ==================
        diagonales = [
            {"nom": "Diagonale multidirectionnelle 2.07m", "longueur": 2.07, "poids": 10.5, "quantite": 120},
            {"nom": "Diagonale multidirectionnelle 3.07m", "longueur": 3.07, "poids": 13.0, "quantite": 80},
        ]

        # ================== PLANCHERS (CLASSES 3 → 6) ==================
        planchers = [
            {
                "nom": "Plancher acier 2.07 x 0.32m",
                "description": "Plancher EN 12811 – Classe 3 à 6 (200–600 kg/m²)",
                "longueur": 2.07,
                "largeur": 0.32,
                "poids": 16.0,
                "quantite": 120
            },
            {
                "nom": "Plancher acier 2.07 x 0.73m",
                "description": "Plancher EN 12811 – Classe 3 à 6 (200–600 kg/m²)",
                "longueur": 2.07,
                "largeur": 0.73,
                "poids": 23.0,
                "quantite": 200
            },
            {
                "nom": "Plancher avec trappe 2.07 x 0.73m",
                "description": "Plancher avec trappe EN 12811 – Classe 3 à 6",
                "longueur": 2.07,
                "largeur": 0.73,
                "poids": 25.0,
                "quantite": 40
            }
        ]

        # ================== PROTECTIONS ==================
        protections = [
            {"nom": "Garde-corps 2.07m", "longueur": 2.07, "poids": 5.5, "quantite": 200},
            {"nom": "Garde-corps 3.07m", "longueur": 3.07, "poids": 7.5, "quantite": 120},
            {"nom": "Plinthe acier 2.07m", "longueur": 2.07, "hauteur": 0.15, "poids": 2.5, "quantite": 200},
        ]

        # ================== BASES ==================
        bases = [
            {"nom": "Embase fixe 150x150mm", "poids": 4.5, "quantite": 200},
            {"nom": "Vérin réglable 60cm", "hauteur": 0.60, "poids": 6.5, "quantite": 200},
        ]

        # ================== ANCRAGES ==================
        ancrages = [
            {"nom": "Ancrage façade EN 12811", "poids": 3.0, "quantite": 200},
            {"nom": "Stabilisateur télescopique 2–3m", "longueur": 3.0, "poids": 9.5, "quantite": 80},
        ]

        # ================== ACCÈS ==================
        acces = [
            {
                "nom": "Échelle intérieure 2.0m",
                "description": "Échelle d’accès EN 12811 – Classe 3 à 6",
                "hauteur": 2.0,
                "poids": 12.0,
                "quantite": 40
            },
            {
                "nom": "Escalier multidirectionnel 2.0m",
                "description": "Escalier porteur EN 12811 – Classe 4 à 6",
                "hauteur": 2.0,
                "poids": 38.0,
                "quantite": 20
            }
        ]

        # ================== FUSION ==================
        tous_articles = (
            montants + lisses + traverses + diagonales +
            planchers + protections + bases + ancrages + acces
        )

        for a in tous_articles:
            db.add(Article(
                nom=a["nom"],
                description=a.get("description", "Échafaudage multidirectionnel EN 12811"),
                quantite=a["quantite"],
                longueur=a.get("longueur"),
                largeur=a.get("largeur"),
                hauteur=a.get("hauteur"),
                poids=a.get("poids"),
                company_id=company_id
            ))

        db.commit()
        print(f"✅ {len(tous_articles)} articles ajoutés avec succès")

    except Exception as e:
        db.rollback()
        print("❌ Erreur:", e)
    finally:
        db.close()


if __name__ == "__main__":
    print("🏗️ Seed échafaudage multidirectionnel EN 12811")
    print("=" * 60)
    create_articles()
