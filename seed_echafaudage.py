# seed_echafaudage.py
"""
Script pour peupler la base avec des articles d'échafaudage
conformes aux normes européennes EN 12810 et EN 12811
"""
from database import SessionLocal
from models import Company, Article
from sqlalchemy.exc import IntegrityError

def create_articles():
    db = SessionLocal()
    
    try:
        # Vérifier qu'une entreprise existe
        company = db.query(Company).first()
        if not company:
            print("❌ Aucune entreprise trouvée. Créez d'abord une entreprise.")
            return
        
        company_id = company.id
        print(f"✅ Entreprise trouvée: {company.name} (ID: {company_id})")
        
        # ============================================================
        # POTEAUX / MONTANTS / UPRIGHTS (Verticaux)
        # ============================================================
        poteaux = [
            {"nom": "Poteau 0.5m", "description": "Montant vertical 0.5m", "hauteur": 0.5, "poids": 7.5, "quantite": 50},
            {"nom": "Poteau 1m", "description": "Montant vertical 1m", "hauteur": 1.0, "poids": 12.0, "quantite": 100},
            {"nom": "Poteau 1.5m", "description": "Montant vertical 1.5m", "hauteur": 1.5, "poids": 16.5, "quantite": 80},
            {"nom": "Poteau 2m", "description": "Montant vertical 2m (standard)", "hauteur": 2.0, "poids": 19.5, "quantite": 200},
            {"nom": "Poteau 2.5m", "description": "Montant vertical 2.5m", "hauteur": 2.5, "poids": 23.0, "quantite": 60},
            {"nom": "Poteau 3m", "description": "Montant vertical 3m", "hauteur": 3.0, "poids": 26.5, "quantite": 100},
        ]
        
        # ============================================================
        # MOISES / LISSES / LEDGERS (Horizontales longitudinales)
        # ============================================================
        moises = [
            {"nom": "Moise 0.73m", "description": "Lisse horizontale 0.73m", "longueur": 0.73, "poids": 6.8, "quantite": 100},
            {"nom": "Moise 1.09m", "description": "Lisse horizontale 1.09m", "longueur": 1.09, "poids": 8.5, "quantite": 120},
            {"nom": "Moise 1.40m", "description": "Lisse horizontale 1.40m", "longueur": 1.40, "poids": 10.2, "quantite": 100},
            {"nom": "Moise 2.07m", "description": "Lisse horizontale 2.07m (standard)", "longueur": 2.07, "poids": 13.5, "quantite": 250},
            {"nom": "Moise 2.57m", "description": "Lisse horizontale 2.57m", "longueur": 2.57, "poids": 16.0, "quantite": 150},
            {"nom": "Moise 3.07m", "description": "Lisse horizontale 3.07m", "longueur": 3.07, "poids": 18.5, "quantite": 120},
        ]
        
        # ============================================================
        # TRANSVERSES / ENTRETOISES / TRANSOMS (Horizontales transversales)
        # ============================================================
        transverses = [
            {"nom": "Traverse 0.73m", "description": "Entretoise 0.73m", "longueur": 0.73, "poids": 6.5, "quantite": 150},
            {"nom": "Traverse 1.09m", "description": "Entretoise 1.09m", "longueur": 1.09, "poids": 8.2, "quantite": 180},
            {"nom": "Traverse 1.40m", "description": "Entretoise 1.40m", "longueur": 1.40, "poids": 9.8, "quantite": 120},
        ]
        
        # ============================================================
        # DIAGONALES / CONTREVENTEMENTS / BRACES
        # ============================================================
        diagonales = [
            {"nom": "Diagonale 2.0m", "description": "Contreventement diagonal 2.0m", "longueur": 2.0, "poids": 9.5, "quantite": 100},
            {"nom": "Diagonale 2.5m", "description": "Contreventement diagonal 2.5m", "longueur": 2.5, "poids": 11.0, "quantite": 80},
            {"nom": "Diagonale 3.0m", "description": "Contreventement diagonal 3.0m", "longueur": 3.0, "poids": 12.5, "quantite": 60},
        ]
        
        # ============================================================
        # PLANCHERS / PLATEFORMES / DECKS
        # ============================================================
        planchers = [
            {"nom": "Plancher alu 0.61m", "description": "Plateforme aluminium 0.61m x 2.07m", "longueur": 2.07, "largeur": 0.61, "poids": 18.5, "quantite": 80},
            {"nom": "Plancher alu 0.73m", "description": "Plateforme aluminium 0.73m x 2.07m", "longueur": 2.07, "largeur": 0.73, "poids": 21.0, "quantite": 150},
            {"nom": "Plancher alu 0.32m", "description": "Plateforme aluminium 0.32m x 2.07m", "longueur": 2.07, "largeur": 0.32, "poids": 14.5, "quantite": 60},
            {"nom": "Plancher bois 0.61m", "description": "Plateforme bois 0.61m x 2.50m", "longueur": 2.50, "largeur": 0.61, "poids": 24.0, "quantite": 50},
            {"nom": "Plancher bois 0.73m", "description": "Plateforme bois 0.73m x 2.50m", "longueur": 2.50, "largeur": 0.73, "poids": 28.0, "quantite": 100},
            {"nom": "Trappe d'accès 0.61m", "description": "Plancher avec trappe 0.61m x 2.07m", "longueur": 2.07, "largeur": 0.61, "poids": 20.0, "quantite": 30},
        ]
        
        # ============================================================
        # PLINTHES / TOE BOARDS
        # ============================================================
        plinthes = [
            {"nom": "Plinthe alu 2.07m", "description": "Plinthe de sécurité alu 2.07m", "longueur": 2.07, "hauteur": 0.15, "poids": 2.5, "quantite": 150},
            {"nom": "Plinthe alu 2.57m", "description": "Plinthe de sécurité alu 2.57m", "longueur": 2.57, "hauteur": 0.15, "poids": 3.0, "quantite": 100},
            {"nom": "Plinthe alu 3.07m", "description": "Plinthe de sécurité alu 3.07m", "longueur": 3.07, "hauteur": 0.15, "poids": 3.5, "quantite": 80},
        ]
        
        # ============================================================
        # GARDE-CORPS / MAIN COURANTE / GUARDRAILS
        # ============================================================
        garde_corps = [
            {"nom": "Garde-corps latéral 2.07m", "description": "Lisse de protection latérale 2.07m", "longueur": 2.07, "poids": 5.5, "quantite": 120},
            {"nom": "Garde-corps latéral 2.57m", "description": "Lisse de protection latérale 2.57m", "longueur": 2.57, "poids": 6.5, "quantite": 100},
            {"nom": "Garde-corps frontal 0.73m", "description": "Lisse de protection frontale 0.73m", "longueur": 0.73, "poids": 3.5, "quantite": 80},
            {"nom": "Main courante 2.07m", "description": "Main courante supérieure 2.07m", "longueur": 2.07, "poids": 4.5, "quantite": 100},
        ]
        
        # ============================================================
        # EMBASES / PIEDS / BASE PLATES
        # ============================================================
        embases = [
            {"nom": "Embase standard", "description": "Embase réglable standard 200x200mm", "longueur": 0.20, "largeur": 0.20, "poids": 4.5, "quantite": 200},
            {"nom": "Embase pivotante", "description": "Embase pivotante 200x200mm", "longueur": 0.20, "largeur": 0.20, "poids": 5.0, "quantite": 100},
            {"nom": "Embase à vérin", "description": "Embase avec vérin de réglage 300mm", "longueur": 0.20, "largeur": 0.20, "hauteur": 0.30, "poids": 6.5, "quantite": 150},
        ]
        
        # ============================================================
        # SOCLES RÉGLABLES ET INCLINABLES
        # ============================================================
        socles = [
            {"nom": "Socle réglable U standard", "description": "Socle en U réglable 30-60cm", "longueur": 0.20, "largeur": 0.20, "hauteur": 0.60, "poids": 8.5, "quantite": 150},
            {"nom": "Socle réglable tubulaire", "description": "Socle tubulaire réglable 40-80cm", "longueur": 0.15, "largeur": 0.15, "hauteur": 0.80, "poids": 7.8, "quantite": 120},
            {"nom": "Socle inclinable 0-8°", "description": "Socle inclinable 0-8 degrés", "longueur": 0.20, "largeur": 0.20, "hauteur": 0.50, "poids": 9.2, "quantite": 100},
            {"nom": "Socle inclinable 0-15°", "description": "Socle inclinable 0-15 degrés (terrains irréguliers)", "longueur": 0.22, "largeur": 0.22, "hauteur": 0.55, "poids": 10.5, "quantite": 80},
            {"nom": "Vérin de socle 30cm", "description": "Vérin de réglage 20-30cm", "hauteur": 0.30, "poids": 3.5, "quantite": 200},
            {"nom": "Vérin de socle 60cm", "description": "Vérin de réglage 40-60cm", "hauteur": 0.60, "poids": 5.0, "quantite": 150},
            {"nom": "Platine d'ancrage au sol", "description": "Platine à cheviller au sol 250x250mm", "longueur": 0.25, "largeur": 0.25, "poids": 6.5, "quantite": 100},
            {"nom": "Pointe de socle", "description": "Pointe d'ancrage pour terrain meuble", "hauteur": 0.30, "poids": 2.8, "quantite": 150},
        ]
        
        # ============================================================
        # CALES / STABILISATEURS / SHIMS
        # ============================================================
        cales = [
            {"nom": "Cale bois 50mm", "description": "Cale de calage bois 50mm", "hauteur": 0.05, "poids": 0.5, "quantite": 300},
            {"nom": "Cale bois 100mm", "description": "Cale de calage bois 100mm", "hauteur": 0.10, "poids": 0.8, "quantite": 200},
            {"nom": "Cale plastique réglable", "description": "Cale plastique réglable 20-50mm", "hauteur": 0.05, "poids": 0.3, "quantite": 250},
        ]
        
        # ============================================================
        # ÉCHELLES / ESCALIERS / LADDERS
        # ============================================================
        acces = [
            {"nom": "Échelle d'accès 2m", "description": "Échelle intégrée 2m", "hauteur": 2.0, "poids": 12.0, "quantite": 40},
            {"nom": "Échelle d'accès 3m", "description": "Échelle intégrée 3m", "hauteur": 3.0, "poids": 16.0, "quantite": 30},
            {"nom": "Escalier 1m", "description": "Escalier d'accès 1m", "hauteur": 1.0, "poids": 25.0, "quantite": 20},
            {"nom": "Escalier incliné 2m", "description": "Escalier d'accès incliné 2m", "hauteur": 2.0, "poids": 35.0, "quantite": 15},
        ]
        
        # ============================================================
        # ANCRAGES ET STABILISATION
        # ============================================================
        ancrages = [
            {"nom": "Ancrage mural", "description": "Point d'ancrage mural", "poids": 2.5, "quantite": 100},
            {"nom": "Ancrage traversant", "description": "Ancrage traversant pour façade", "poids": 3.8, "quantite": 80},
            {"nom": "Stabilisateur télescopique", "description": "Stabilisateur télescopique 1.5-3m", "longueur": 3.0, "poids": 8.5, "quantite": 60},
            {"nom": "Contrepoids béton", "description": "Contrepoids béton 25kg", "poids": 25.0, "quantite": 80},
            {"nom": "Lest d'eau 50L", "description": "Lest d'eau réutilisable 50L", "poids": 2.5, "quantite": 60},
        ]
        
        # ============================================================
        # CONSOLES ET EXTENSIONS
        # ============================================================
        consoles = [
            {"nom": "Console porte-plancher 0.73m", "description": "Console d'extension 0.73m", "longueur": 0.73, "poids": 7.5, "quantite": 40},
            {"nom": "Console porte-plancher 1.09m", "description": "Console d'extension 1.09m", "longueur": 1.09, "poids": 9.5, "quantite": 30},
            {"nom": "Console de façade", "description": "Console de protection façade", "longueur": 1.5, "poids": 12.0, "quantite": 25},
        ]
        
        # ============================================================
        # BÂCHES ET PROTECTIONS
        # ============================================================
        protections = [
            {"nom": "Bâche de protection 2.57m x 3.07m", "description": "Bâche mesh ignifugée", "longueur": 3.07, "largeur": 2.57, "poids": 2.5, "quantite": 50},
            {"nom": "Filet anti-chute 2.07m x 2.07m", "description": "Filet de sécurité", "longueur": 2.07, "largeur": 2.07, "poids": 1.8, "quantite": 60},
            {"nom": "Bâche opaque 2.57m x 3.07m", "description": "Bâche opaque ignifugée (confidentialité)", "longueur": 3.07, "largeur": 2.57, "poids": 3.2, "quantite": 30},
        ]
        
        # ============================================================
        # ACCESSOIRES DE SÉCURITÉ
        # ============================================================
        securite = [
            {"nom": "Ligne de vie horizontale 10m", "description": "Ligne de vie temporaire 10m", "longueur": 10.0, "poids": 5.5, "quantite": 20},
            {"nom": "Point d'ancrage mobile", "description": "Point d'ancrage mobile pour harnais", "poids": 3.2, "quantite": 40},
            {"nom": "Panneau 'Accès interdit'", "description": "Panneau de signalisation", "poids": 1.5, "quantite": 30},
            {"nom": "Protection d'angle", "description": "Protection angle de plancher", "poids": 2.0, "quantite": 50},
        ]
        
        # ============================================================
        # CONNECTEURS ET FIXATIONS
        # ============================================================
        connecteurs = [
            {"nom": "Goupille de sécurité", "description": "Goupille de verrouillage", "poids": 0.15, "quantite": 500},
            {"nom": "Collier de serrage", "description": "Collier de fixation rapide", "poids": 0.3, "quantite": 300},
            {"nom": "Boulon de liaison", "description": "Boulon M12 avec écrou", "poids": 0.1, "quantite": 400},
        ]
        
        # Regrouper tous les articles
        tous_articles = (
            poteaux + moises + transverses + diagonales + 
            planchers + plinthes + garde_corps + embases + socles + 
            cales + acces + ancrages + consoles + protections +
            securite + connecteurs
        )
        
        # Ajouter les articles à la base
        added_count = 0
        for art_data in tous_articles:
            try:
                article = Article(
                    nom=art_data["nom"],
                    description=art_data.get("description", ""),
                    quantite=art_data.get("quantite", 0),
                    longueur=art_data.get("longueur"),
                    largeur=art_data.get("largeur"),
                    hauteur=art_data.get("hauteur"),
                    poids=art_data.get("poids"),
                    company_id=company_id
                )
                db.add(article)
                added_count += 1
            except Exception as e:
                print(f"❌ Erreur pour {art_data['nom']}: {e}")
        
        db.commit()
        print(f"\n✅ {added_count} articles d'échafaudage ajoutés avec succès !")
        print(f"📦 Stock total disponible pour l'entreprise '{company.name}'")
        print("\n📋 Résumé par catégorie:")
        print(f"   - Poteaux/Montants: {len(poteaux)}")
        print(f"   - Moises/Lisses: {len(moises)}")
        print(f"   - Transverses: {len(transverses)}")
        print(f"   - Diagonales: {len(diagonales)}")
        print(f"   - Planchers: {len(planchers)}")
        print(f"   - Plinthes: {len(plinthes)}")
        print(f"   - Garde-corps: {len(garde_corps)}")
        print(f"   - Embases: {len(embases)}")
        print(f"   - Socles réglables: {len(socles)}")
        print(f"   - Cales: {len(cales)}")
        print(f"   - Accès (échelles): {len(acces)}")
        print(f"   - Ancrages: {len(ancrages)}")
        print(f"   - Consoles: {len(consoles)}")
        print(f"   - Protections: {len(protections)}")
        print(f"   - Sécurité: {len(securite)}")
        print(f"   - Connecteurs: {len(connecteurs)}")
        print(f"\n🎯 Total: {added_count} articles conformes EN 12810/EN 12811")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🏗️  Peuplement de la base avec articles d'échafaudage")
    print("=" * 60)
    create_articles()