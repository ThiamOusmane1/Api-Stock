"""
Seed échafaudage multidirectionnel
Conforme EN 12810 / EN 12811

Systèmes :
- Layher Allround
- PERI UP
- Hünnebeck Bosta
- Plettac Multitec

Modules :
- 0.73m
- 1.09m

⚠️ IMPORTANT :
Les articles marqués [CALCUL] doivent garder EXACTEMENT le même nom
car ils sont utilisés dans allocate_echafaudage() de crud.py
"""

import sys
from database import SessionLocal
from models import Company, Article


ARTICLES_ECHAFAUDAGE = [

    # ============================================================
    # 🔵 POTEAUX / MONTANTS VERTICAUX
    # ============================================================

    {
        "nom": "Poteau 0.50m",
        "category": "poteau",
        "poids": 3.2,
        "hauteur": 0.50,
        "longueur": None,
        "largeur": None,
        "quantite": 80,
        "prix_unitaire": 18.0,
        "description": "Poteau vertical 0.50m Ringlock - Layher Allround - EN12811"
    },

    {
        "nom": "Poteau 1.00m",
        "category": "poteau",
        "poids": 5.8,
        "hauteur": 1.00,
        "longueur": None,
        "largeur": None,
        "quantite": 100,
        "prix_unitaire": 28.0,
        "description": "Poteau vertical 1.00m Ringlock - PERI UP - EN12811"
    },

    {
        "nom": "Poteau 1.50m",
        "category": "poteau",
        "poids": 8.1,
        "hauteur": 1.50,
        "longueur": None,
        "largeur": None,
        "quantite": 120,
        "prix_unitaire": 36.0,
        "description": "Poteau vertical 1.50m Ringlock - Hünnebeck Bosta - EN12811"
    },

    {
        "nom": "Poteau 2m",
        "category": "poteau",
        "poids": 12.5,
        "hauteur": 2.00,
        "longueur": None,
        "largeur": None,
        "quantite": 280,
        "prix_unitaire": 45.0,
        "description": "Poteau vertical 2.00m Ringlock - Layher Allround - EN12811 [CALCUL]"
    },

    # ============================================================
    # 🟢 SOCLES FIXES
    # ============================================================

    {
        "nom": "Socle fixe carré 150x150mm",
        "category": "embase",
        "poids": 3.8,
        "hauteur": 0.05,
        "longueur": 0.15,
        "largeur": 0.15,
        "quantite": 120,
        "prix_unitaire": 15.0,
        "description": "Socle fixe carré 150x150mm acier galvanisé - Layher Allround - EN12811"
    },

    {
        "nom": "Socle fixe carré 200x200mm",
        "category": "embase",
        "poids": 5.2,
        "hauteur": 0.05,
        "longueur": 0.20,
        "largeur": 0.20,
        "quantite": 60,
        "prix_unitaire": 20.0,
        "description": "Socle fixe carré 200x200mm acier galvanisé - PERI UP - EN12811"
    },

    # ============================================================
    # 🟢 SOCLES INCLINABLES
    # ============================================================

    {
        "nom": "Socle inclinable 10° 150x150mm",
        "category": "embase",
        "poids": 5.5,
        "hauteur": 0.06,
        "longueur": 0.15,
        "largeur": 0.15,
        "quantite": 40,
        "prix_unitaire": 35.0,
        "description": "Socle inclinable jusqu'à 10° 150x150mm - toiture standard - Layher Allround - EN12811"
    },

    {
        "nom": "Socle inclinable 10° 200x200mm",
        "category": "embase",
        "poids": 7.2,
        "hauteur": 0.06,
        "longueur": 0.20,
        "largeur": 0.20,
        "quantite": 20,
        "prix_unitaire": 48.0,
        "description": "Socle inclinable jusqu'à 10° 200x200mm - toiture standard - PERI UP - EN12811"
    },

    # ============================================================
    # 🟢 EMBASES / VÉRINS
    # ============================================================

    {
        "nom": "Embase standard",
        "category": "embase",
        "poids": 4.2,
        "hauteur": None,
        "longueur": None,
        "largeur": None,
        "quantite": 150,
        "prix_unitaire": 18.0,
        "description": "Embase réglable standard Ø48mm - Layher Allround - EN12811 [CALCUL]"
    },

    {
        "nom": "Embase à vis 45cm",
        "category": "embase",
        "poids": 5.5,
        "hauteur": 0.45,
        "longueur": None,
        "largeur": None,
        "quantite": 60,
        "prix_unitaire": 32.0,
        "description": "Embase à vis 45cm terrain irrégulier - Plettac Multitec - EN12811"
    },

    {
        "nom": "Vérin de socle 30cm",
        "category": "socle",
        "poids": 3.8,
        "hauteur": 0.30,
        "longueur": None,
        "largeur": None,
        "quantite": 150,
        "prix_unitaire": 22.0,
        "description": "Vérin de réglage 30cm Ø38mm - PERI UP - EN12811 [CALCUL]"
    },

    {
        "nom": "Vérin de socle 50cm",
        "category": "socle",
        "poids": 5.1,
        "hauteur": 0.50,
        "longueur": None,
        "largeur": None,
        "quantite": 60,
        "prix_unitaire": 28.0,
        "description": "Vérin de réglage 50cm Ø38mm - Hünnebeck Bosta - EN12811"
    },

    # ============================================================
    # 🟤 CALES BOIS
    # ============================================================

    {
        "nom": "Cale bois 50mm",
        "category": "cale",
        "poids": 0.5,
        "hauteur": 0.05,
        "longueur": 0.20,
        "largeur": 0.20,
        "quantite": 300,
        "prix_unitaire": 2.5,
        "description": "Cale bois 50mm 200x200mm mise à niveau socle - EN12811 [CALCUL]"
    },

    {
        "nom": "Cale bois 100mm",
        "category": "cale",
        "poids": 0.9,
        "hauteur": 0.10,
        "longueur": 0.20,
        "largeur": 0.20,
        "quantite": 150,
        "prix_unitaire": 4.0,
        "description": "Cale bois 100mm 200x200mm fort dénivelé - EN12811"
    },

    {
        "nom": "Cale bois 150mm",
        "category": "cale",
        "poids": 1.3,
        "hauteur": 0.15,
        "longueur": 0.20,
        "largeur": 0.20,
        "quantite": 80,
        "prix_unitaire": 5.5,
        "description": "Cale bois 150mm 200x200mm très fort dénivelé - EN12811"
    },

    {
        "nom": "Cale bois 200mm",
        "category": "cale",
        "poids": 1.8,
        "hauteur": 0.20,
        "longueur": 0.20,
        "largeur": 0.20,
        "quantite": 60,
        "prix_unitaire": 7.0,
        "description": "Cale bois 200mm 200x200mm compensation maximale - EN12811"
    },

    # ============================================================
    # 🔵 CALES PLASTIQUE
    # ============================================================

    {
        "nom": "Cale plastique 20mm 150x150mm",
        "category": "cale",
        "poids": 0.3,
        "hauteur": 0.02,
        "longueur": 0.15,
        "largeur": 0.15,
        "quantite": 300,
        "prix_unitaire": 3.5,
        "description": "Cale plastique HD 20mm 150x150mm réglage fin - protection sol - EN12811"
    },

    {
        "nom": "Cale plastique 10mm 150x150mm",
        "category": "cale",
        "poids": 0.2,
        "hauteur": 0.01,
        "longueur": 0.15,
        "largeur": 0.15,
        "quantite": 200,
        "prix_unitaire": 2.5,
        "description": "Cale plastique HD 10mm 150x150mm réglage très fin - protection sol - EN12811"
    },

    {
        "nom": "Cale plastique 5mm 150x150mm",
        "category": "cale",
        "poids": 0.1,
        "hauteur": 0.005,
        "longueur": 0.15,
        "largeur": 0.15,
        "quantite": 200,
        "prix_unitaire": 1.5,
        "description": "Cale plastique HD 5mm 150x150mm réglage millimétrique - EN12811"
    },

    # ============================================================
    # 🟡 MOISES
    # ============================================================

    {
        "nom": "Moise 0.73m",
        "category": "moise",
        "poids": 2.1,
        "hauteur": None,
        "longueur": 0.73,
        "largeur": None,
        "quantite": 200,
        "prix_unitaire": 12.0,
        "description": "Lisse transversale 0.73m Ø48.3mm - Layher Allround - EN12811 [CALCUL]"
    },

    {
        "nom": "Moise 3.07m",
        "category": "moise",
        "poids": 8.2,
        "hauteur": None,
        "longueur": 3.07,
        "largeur": None,
        "quantite": 300,
        "prix_unitaire": 32.0,
        "description": "Lisse horizontale 3.07m Ø48.3mm - Layher Allround - EN12811 [CALCUL]"
    },

    # ============================================================
    # 🔴 PLANCHERS
    # ============================================================

    {
        "nom": "plancher acier 3.07m",
        "category": "plancher",
        "poids": 18.5,
        "hauteur": None,
        "longueur": 3.07,
        "largeur": 0.61,
        "quantite": 150,
        "prix_unitaire": 65.0,
        "description": "Plancher acier galvanisé 3.07x0.61m - Layher Allround - EN12811 [CALCUL]"
    },

    {
        "nom": "Trappe d'accès 3.07m",
        "category": "plancher",
        "poids": 20.0,
        "hauteur": None,
        "longueur": 3.07,
        "largeur": 0.61,
        "quantite": 40,
        "prix_unitaire": 95.0,
        "description": "Plancher trappe avec échelle intégrée 3.07m - Layher Allround - EN12811 [CALCUL]"
    },

    # ============================================================
    # 🟣 GARDE-CORPS
    # ============================================================

    {
        "nom": "Garde-corps latéral 3.07m",
        "category": "gardeCorps",
        "poids": 6.8,
        "hauteur": 1.00,
        "longueur": 3.07,
        "largeur": None,
        "quantite": 150,
        "prix_unitaire": 28.0,
        "description": "Garde-corps latéral 3.07m H=1.00m - Layher Allround - EN12811 [CALCUL]"
    },

    {
        "nom": "Garde-corps frontal 0.73m",
        "category": "gardeCorps",
        "poids": 2.5,
        "hauteur": 1.00,
        "longueur": 0.73,
        "largeur": None,
        "quantite": 100,
        "prix_unitaire": 15.0,
        "description": "Garde-corps frontal 0.73m H=1.00m - Layher Allround - EN12811 [CALCUL]"
    },

    # ============================================================
    # ⚪ PLINTHES
    # ============================================================

    {
        "nom": "Plinthe alu 3.07m",
        "category": "plinthe",
        "poids": 2.2,
        "hauteur": 0.15,
        "longueur": 3.07,
        "largeur": None,
        "quantite": 150,
        "prix_unitaire": 12.0,
        "description": "Plinthe aluminium 3.07m H=0.15m - Layher Allround - EN12811 [CALCUL]"
    },

    # ============================================================
    # 🔶 DIAGONALES
    # ============================================================

    {
        "nom": "Diagonale 0.73m",
        "category": "diagonale",
        "poids": 1.8,
        "hauteur": None,
        "longueur": 0.73,
        "largeur": None,
        "quantite": 100,
        "prix_unitaire": 10.0,
        "description": "Diagonale transversale 0.73m - Layher Allround - EN12811 [CALCUL]"
    },

    {
        "nom": "Diagonale 1.09m",
        "category": "diagonale",
        "poids": 2.5,
        "hauteur": None,
        "longueur": 1.09,
        "largeur": None,
        "quantite": 60,
        "prix_unitaire": 14.0,
        "description": "Diagonale transversale 1.09m - PERI UP - EN12811"
    },

    {
        "nom": "Diagonale 1.57m",
        "category": "diagonale",
        "poids": 3.5,
        "hauteur": None,
        "longueur": 1.57,
        "largeur": None,
        "quantite": 60,
        "prix_unitaire": 16.0,
        "description": "Diagonale 1.57m - PERI UP - EN12811"
    },

    {
        "nom": "Diagonale 2.07m",
        "category": "diagonale",
        "poids": 4.8,
        "hauteur": None,
        "longueur": 2.07,
        "largeur": None,
        "quantite": 60,
        "prix_unitaire": 20.0,
        "description": "Diagonale 2.07m - Hünnebeck Bosta - EN12811"
    },

    {
        "nom": "Diagonale 3.0m",
        "category": "diagonale",
        "poids": 5.5,
        "hauteur": None,
        "longueur": 3.00,
        "largeur": None,
        "quantite": 120,
        "prix_unitaire": 22.0,
        "description": "Diagonale longitudinale 3.00m - Layher Allround - EN12811 [CALCUL]"
    },
]


def create_articles(company_id=None):
    db = SessionLocal()

    try:

        # ========================================================
        # ENTREPRISE
        # ========================================================

        if company_id:
            company = db.query(Company).filter(
                Company.id == company_id
            ).first()
        else:
            company = db.query(Company).first()

        if not company:
            print("❌ Aucune entreprise trouvée")
            return

        print("=" * 60)
        print(f"🏢 Entreprise : {company.name} (ID: {company.id})")
        print("=" * 60)

        created = 0
        updated = 0

        # ========================================================
        # SEED
        # ========================================================

        for art in ARTICLES_ECHAFAUDAGE:

            existing = db.query(Article).filter(
                Article.nom == art["nom"],
                Article.company_id == company.id
            ).first()

            # ====================================================
            # UPDATE
            # ====================================================

            if existing:

                existing.category = art["category"]
                existing.description = art.get("description")
                existing.quantite = art["quantite"]
                existing.prix_unitaire = art["prix_unitaire"]
                existing.poids = art["poids"]
                existing.longueur = art.get("longueur")
                existing.largeur = art.get("largeur")
                existing.hauteur = art.get("hauteur")

                print(f"🔄 Mis à jour : {art['nom']}")
                updated += 1
                continue

            # ====================================================
            # CREATE
            # ====================================================

            article = Article(
                nom=art["nom"],
                category=art["category"],
                description=art.get("description"),
                quantite=art["quantite"],
                prix_unitaire=art["prix_unitaire"],
                poids=art["poids"],
                longueur=art.get("longueur"),
                largeur=art.get("largeur"),
                hauteur=art.get("hauteur"),
                company_id=company.id
            )

            db.add(article)

            print(
                f"✅ Créé : {art['nom']} "
                f"({art['quantite']} unités)"
            )

            created += 1

        # ========================================================
        # COMMIT
        # ========================================================

        db.commit()

        print("=" * 60)
        print("🎉 Seed terminé")
        print(f"✅ Créés      : {created}")
        print(f"🔄 Mis à jour : {updated}")
        print(f"📦 Total      : {created + updated}")
        print("=" * 60)

    except Exception as e:

        db.rollback()

        print("=" * 60)
        print("❌ ERREUR SEED")
        print(str(e))
        print("=" * 60)

        raise

    finally:
        db.close()


if __name__ == "__main__":

    print("=" * 60)
    print("🏗️ SEED ÉCHAFAUDAGE EN12810 / EN12811")
    print("=" * 60)

    company_id = int(sys.argv[1]) if len(sys.argv) > 1 else None

    if company_id:
        print(f"🎯 Company ID ciblé : {company_id}")

    create_articles(company_id)