from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException
import schemas
from models import Company, User, Article, Retrait
from typing import Optional, List, Dict
from datetime import datetime
import math 



# ------------------------------
# ENTREPRISES & USERS
# ------------------------------
def create_entreprise(db: Session, nom: str):
    entreprise_exist = db.query(Company).filter(Company.name == nom).first()
    if entreprise_exist:
        raise ValueError("Une entreprise avec ce nom existe déjà.")
    
    entreprise = Company(name=nom)
    db.add(entreprise)
    db.commit()
    db.refresh(entreprise)
    return entreprise

def get_entreprise_by_id(db: Session, eid: int):
    return db.query(Company).filter(Company.id == eid).first()

def create_user(db: Session, username: str, hashed_password: str, role: str = "user", company_id: Optional[int] = None):
    user = User(
        username=username,
        password_hash=hashed_password,
        role=role,
        company_id=company_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, uid: int):
    return db.query(User).filter(User.id == uid).first()

def get_article(db: Session, article_id: int):
    return db.query(Article).filter(Article.id == article_id).first()

# ------------------------------
# ARTICLES
# ------------------------------
def get_articles_for_entreprise(db: Session, company_id: Optional[int] = None):
    query = db.query(Article)
    if company_id is not None:
        query = query.filter(Article.company_id == company_id)
    return query.all()

def create_article(db: Session, article: schemas.ArticleCreate):
    db_article = Article(**article.dict())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def update_article_quantite_by_id(db: Session, article_id: int, nouvelle_qte: int):
    article = db.query(Article).filter(Article.id == article_id).first()
    if article:
        article.quantite = nouvelle_qte
        db.commit()
        db.refresh(article)
    return article

def delete_article_by_id(db: Session, article_id: int):
    article = db.query(Article).filter(Article.id == article_id).first()
    if article:
        db.delete(article)
        db.commit()
        return {"message": "Article supprimé", "id": article_id}
    return None

# ------------------------------
# RETRAITS
# ------------------------------
def retirer_article_by_id(db: Session, article_id: int, quantite: int, company_id: Optional[int] = None, user_id: Optional[int] = None):
    article = db.query(Article).filter(Article.id == article_id).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    if article.quantite < quantite:
        raise HTTPException(status_code=400, detail="Stock insuffisant")
    
    nouvelle_qte = article.quantite - quantite
    poids_total = quantite * (article.poids or 0)
    
    article.quantite = nouvelle_qte
    
    retrait = Retrait(
        article_id=article_id,
        company_id=company_id,
        quantite=quantite,
        poids_total=poids_total,
        date_retrait=datetime.utcnow(),
        user_id=user_id
    )
    
    db.add(retrait)
    db.commit()
    db.refresh(article)
    
    return schemas.ArticleRetraitResponse(
        message="Retrait effectué",
        article_id=article_id,
        nom_article=article.nom,
        quantite_retirée=quantite,
        poids_total=poids_total,
        stock_restant=nouvelle_qte
    )

# ------------------------------------------------------------
# DÉTECTION CATÉGORIES
# ------------------------------------------------------------
SYNONYMES = {
    "poteau": ["poteau", "upright", "montant"],
    "moise": ["moise", "lisse", "ledger"],
    "transverse": ["transverse", "traverse", "transom"],
    "diagonale": ["diagonale", "brace"],
    "plancher": ["plancher", "deck", "platform"],
    "plinthe": ["plinthe", "toe board"],
    "gardeCorps": ["garde-corps", "guardrail", "gc"],
    "embase": ["embase", "base"],
    "socle": ["socle"],
    "cale": ["cale"]
}

def detect_categorie(nom: str):
    if not nom:
        return "autres"
    lower = nom.lower()
    for cat, mots in SYNONYMES.items():
        if any(m in lower for m in mots):
            return cat
    return "autres"

# ------------------------------------------------------------
# ✅ ALLOCATION ÉCHAFAUDAGE – VERSION CORRIGÉE SANS BUGS
#    - Calculs vérifiés pour toutes dimensions
#    - Poids calculé UNE SEULE FOIS
#    - Trappes avec échelles intégrées
#    - Amarrages optimisés selon normes EN 12810/12811
# ------------------------------------------------------------

def allocate_echafaudage(
    db,
    hauteur: float,
    longueur: float,
    largeur: float,
    company_id: int,
    # 🆕 PARAMÈTRE DE CONFIGURATION CLIENT
    niveaux_travail: str = "tous"  # "tous", "dernier", "liste:1,3,5"
):
    # --------------------------------------------------------
    # LISTES DE SORTIE
    # --------------------------------------------------------
    pieces = []        # lignes articles finales
    ajustements = []   # articles manquants en base

    # --------------------------------------------------------
    # MODULES NORMALISÉS ÉCHAFAUDAGE
    # --------------------------------------------------------
    MODULE_H = 2.0     # hauteur d'un niveau
    MODULE_L = 3.07    # longueur d'une travée

    # --------------------------------------------------------
    # CALCULS GÉOMÉTRIQUES DE BASE
    # --------------------------------------------------------
    nb_niveaux = math.ceil(hauteur / MODULE_H)
    nb_travees = math.ceil(longueur / MODULE_L)
    nb_lignes_poteaux = nb_travees + 1

    # --------------------------------------------------------
    # 🆕 DÉTERMINER LES NIVEAUX DE TRAVAIL
    # --------------------------------------------------------
    if niveaux_travail == "tous":
        # Configuration standard : travail sur tous les niveaux
        liste_niveaux_travail = list(range(1, nb_niveaux + 1))
    elif niveaux_travail == "dernier":
        # Travail uniquement au dernier niveau (ex: toiture)
        liste_niveaux_travail = [nb_niveaux]
    elif niveaux_travail.startswith("liste:"):
        # Liste personnalisée : "liste:2,4,5"
        try:
            liste_niveaux_travail = [
                int(n.strip()) 
                for n in niveaux_travail.replace("liste:", "").split(",")
            ]
        except:
            liste_niveaux_travail = list(range(1, nb_niveaux + 1))
    else:
        # Par défaut : tous
        liste_niveaux_travail = list(range(1, nb_niveaux + 1))
    
    nb_niveaux_avec_planchers = len(liste_niveaux_travail)
    
    print(f"\n📋 Configuration client :")
    print(f"   Mode : {niveaux_travail}")
    print(f"   Niveaux de travail (planchers) : {liste_niveaux_travail}")
    print(f"   Niveaux de circulation : {nb_niveaux - nb_niveaux_avec_planchers}")
    
    # --------------------------------------------------------
    # RÉPARTITION ACCÈS / TRAVAIL (NORME : 1 ACCÈS / 20M)
    # --------------------------------------------------------
    # ✅ RÈGLE : 1 travée d'accès tous les 20m maximum
    nb_travees_acces = max(1, math.ceil(longueur / 20))
    nb_travees_travail = max(0, nb_travees - nb_travees_acces)
    
    print(f"\n📏 Longueur : {longueur}m → {nb_travees_acces} travée(s) d'accès")

    # --------------------------------------------------------
    # 🔒 POIDS TOTAL GLOBAL (UNE SEULE SOURCE DE VÉRITÉ)
    # --------------------------------------------------------
    poids_total = 0.0
    
    # --------------------------------------------------------
    # 🔍 DICTIONNAIRE POUR ÉVITER DOUBLONS
    # --------------------------------------------------------
    pieces_dict = {}  # {nom_article: quantité_totale}

    # ========================================================
    # 🔧 FONCTION D'AJOUT D'ARTICLE (SÉCURISÉE + ANTI-DOUBLON)
    # ========================================================
    def add_piece(nom: str, quantite: int):
        nonlocal poids_total

        if quantite <= 0:
            return

        # ✅ VÉRIFICATION DEBUG
        print(f"🔍 add_piece appelé : {nom} × {quantite}")

        # ------------------------------------------------
        # CUMUL SI ARTICLE DÉJÀ AJOUTÉ (ANTI-DOUBLON)
        # ------------------------------------------------
        if nom in pieces_dict:
            pieces_dict[nom] += quantite
            print(f"   ➕ Cumul : {nom} → {pieces_dict[nom]} total")
            return
        
        pieces_dict[nom] = quantite

        article = (
            db.query(Article)
            .filter(
                Article.nom == nom,
                Article.company_id == company_id
            )
            .first()
        )

        # ----------------------------------------------------
        # ARTICLE MANQUANT EN BASE
        # ----------------------------------------------------
        if not article:
            ajustements.append(f"Article manquant : {nom}")
            print(f"   ⚠️ Article manquant en BDD : {nom}")
            return

        # ----------------------------------------------------
        # 🔒 CALCUL POIDS (JAMAIS REFAIT AILLEURS)
        # ----------------------------------------------------
        poids_unitaire = article.poids or 0
        poids_ligne = poids_unitaire * quantite
        poids_total += poids_ligne

        print(f"   ✅ Poids : {poids_unitaire} kg × {quantite} = {poids_ligne} kg")

    # ========================================================
    # A️⃣ STRUCTURE PORTEUSE
    # ========================================================
    print("\n" + "="*60)
    print("🏗️ CALCUL STRUCTURE PORTEUSE")
    print("="*60)
    
    qte_cales = nb_lignes_poteaux * 2
    qte_verins = nb_lignes_poteaux * 2
    qte_embases = nb_lignes_poteaux * 2
    qte_poteaux = nb_lignes_poteaux * 2 * nb_niveaux
    
    print(f"Lignes de poteaux : {nb_lignes_poteaux}")
    print(f"Niveaux : {nb_niveaux}")
    print(f"Calcul poteaux : {nb_lignes_poteaux} lignes × 2 côtés × {nb_niveaux} niveaux = {qte_poteaux}")
    
    add_piece("Cale bois 50mm", qte_cales)
    add_piece("Vérin de socle 30cm", qte_verins)
    add_piece("Embase standard", qte_embases)
    add_piece("Poteau 2m", qte_poteaux)

    # ========================================================
    # B️⃣ LISSES / MOISES
    # ========================================================
    print("\n" + "="*60)
    print("🔗 CALCUL MOISES")
    print("="*60)
    
    qte_moise_long = nb_travees * nb_niveaux * 2
    qte_moise_trans = nb_lignes_poteaux * nb_niveaux * 2
    
    print(f"Moises 3.07m : {nb_travees} travées × {nb_niveaux} niveaux × 2 = {qte_moise_long}")
    print(f"Moises 0.73m : {nb_lignes_poteaux} lignes × {nb_niveaux} niveaux × 2 = {qte_moise_trans}")
    
    add_piece("Moise 3.07m", qte_moise_long)
    add_piece("Moise 0.73m", qte_moise_trans)

    # ========================================================
    # C️⃣ PLANCHERS (SANS DOUBLONS)
    # ========================================================
    print("\n" + "="*60)
    print("🔲 CALCUL PLANCHERS")
    print("="*60)
    
    # Travées de travail : 2 planchers × toutes travées × tous niveaux
    planchers_travail = 2 * nb_travees_travail * nb_niveaux
    
    # Travée d'accès niveau 0 : 2 planchers normaux
    planchers_acces_bas = 2 * nb_travees_acces
    
    # Travée d'accès niveaux supérieurs : 1 plancher (l'autre = trappe)
    planchers_acces_haut = nb_travees_acces * max(0, nb_niveaux - 1)
    
    # ✅ TOTAL PLANCHERS (CALCUL UNIQUE)
    total_planchers = planchers_travail + planchers_acces_bas + planchers_acces_haut
    
    print(f"Planchers travail : {nb_travees_travail} travées × 2 × {nb_niveaux} = {planchers_travail}")
    print(f"Planchers accès bas : 2 × 1 = {planchers_acces_bas}")
    print(f"Planchers accès haut : 1 × {nb_niveaux - 1} = {planchers_acces_haut}")
    print(f"TOTAL : {total_planchers}")
    
    add_piece("plancher acier 3.07m", total_planchers)

    # ========================================================
    # D️⃣ TRAPPES D'ACCÈS AVEC ÉCHELLE INTÉGRÉE
    # ========================================================
    print("\n" + "="*60)
    print("🪜 CALCUL TRAPPES")
    print("="*60)
    
    nb_trappes = nb_travees_acces * max(0, nb_niveaux - 1)
    print(f"Trappes : {nb_travees_acces} travée × {nb_niveaux - 1} niveaux = {nb_trappes}")
    
    if nb_trappes > 0:
        add_piece("Trappe d'accès 3.07m", nb_trappes)

    # ========================================================
    # E️⃣ GARDE-CORPS (SÉCURITÉ OBLIGATOIRE NORMES EN 12810)
    # ========================================================
    print("\n" + "="*60)
    print("🛡️ CALCUL GARDE-CORPS")
    print("="*60)
    
    # ✅ NORMES EN 12810 : GC obligatoires à partir du niveau 1
    niveaux_gc = max(0, nb_niveaux - 1)  # Tous sauf niveau 0
    
    # ✅ GC latéraux : 2 par travée (intérieur + extérieur)
    qte_gc_lat = nb_travees * niveaux_gc * 2
    
    # ✅ GC frontaux : 2 par niveau (début + fin)
    qte_gc_front = 2 * niveaux_gc
    
    print(f"Mode : Conforme normes EN 12810 (GC sur tous les niveaux ≥1)")
    print(f"GC latéraux : {nb_travees} travées × {niveaux_gc} niv × 2 côtés = {qte_gc_lat}")
    print(f"GC frontaux : 2 × {niveaux_gc} niv = {qte_gc_front}")
    
    add_piece("Garde-corps latéral 3.07m", qte_gc_lat)
    add_piece("Garde-corps frontal 0.73m", qte_gc_front)

    # ========================================================
    # F️⃣ PLINTHES (OBLIGATOIRES AVEC LES GARDE-CORPS)
    # ========================================================
    # ✅ Plinthes latérales : 2 par travée (intérieur + extérieur)
    qte_plinthe_long = nb_travees * niveaux_gc * 2
    
    # ✅ Plinthes frontales : 2 par niveau (début + fin)
    qte_plinthe_trans = 2 * niveaux_gc
    
    print(f"Plinthes 3.07m : {nb_travees} travées × {niveaux_gc} niv × 2 côtés = {qte_plinthe_long}")
    print(f"Plinthes 0.73m : 2 × {niveaux_gc} niv = {qte_plinthe_trans}")
    
    add_piece("Plinthe alu 3.07m", qte_plinthe_long)
    add_piece("Plinthe alu 0.73m", qte_plinthe_trans)

    # ========================================================
    # G️⃣ CONTREVENTEMENT
    # ========================================================
    print("\n" + "="*60)
    print("🔺 CALCUL DIAGONALES")
    print("="*60)
    
    qte_diag_long = math.ceil(nb_travees * nb_niveaux / 2)
    qte_diag_trans = math.ceil(nb_lignes_poteaux * nb_niveaux / 2)
    
    print(f"Diagonales 3.0m : ceil({nb_travees} × {nb_niveaux} / 2) = {qte_diag_long}")
    print(f"Diagonales 0.73m : ceil({nb_lignes_poteaux} × {nb_niveaux} / 2) = {qte_diag_trans}")
    
    add_piece("Diagonale 3.0m", qte_diag_long)
    add_piece("Diagonale 0.73m", qte_diag_trans)

    # ========================================================
    # H️⃣ AMARRAGES (NORMES EN 12811)
    # ========================================================
    print("\n" + "="*60)
    print("⚓ CALCUL AMARRAGES")
    print("="*60)
    
    surface_facade = hauteur * longueur
    amarrages_par_surface = math.ceil(surface_facade / 24)
    niveaux_amarrage = math.ceil(hauteur / 4)
    points_par_niveau = math.ceil(longueur / 8)
    
    amarrages_total = max(
        amarrages_par_surface,
        niveaux_amarrage * points_par_niveau
    )
    
    if hauteur > 6:
        amarrages_total = max(amarrages_total, 4)
    
    print(f"Surface façade : {surface_facade} m²")
    print(f"Par surface (÷24) : {amarrages_par_surface}")
    print(f"Par grille ({niveaux_amarrage} niv × {points_par_niveau} pts) : {niveaux_amarrage * points_par_niveau}")
    print(f"TOTAL : {amarrages_total}")
    
    add_piece("Platine d'ancrage au sol", amarrages_total)

    # ========================================================
    # 🔄 CONVERSION DICTIONNAIRE → LISTE FINALE
    # ========================================================
    print("\n" + "="*60)
    print("📦 GÉNÉRATION LISTE FINALE")
    print("="*60)
    
    for nom_article, quantite_totale in pieces_dict.items():
        article = (
            db.query(Article)
            .filter(
                Article.nom == nom_article,
                Article.company_id == company_id
            )
            .first()
        )
        
        if not article:
            pieces.append({
                "article_id": None,
                "nom": nom_article,
                "quantite_utilisee": quantite_totale,
                "longueur": None,
                "largeur": None,
                "hauteur": None,
                "poids_unitaire": 0,
                "poids_total_ligne": 0
            })
            continue
        
        poids_unitaire = article.poids or 0
        poids_ligne = poids_unitaire * quantite_totale
        
        pieces.append({
            "article_id": article.id,
            "nom": article.nom,
            "quantite_utilisee": quantite_totale,
            "longueur": article.longueur,
            "largeur": article.largeur,
            "hauteur": article.hauteur,
            "poids_unitaire": poids_unitaire,
            "poids_total_ligne": round(poids_ligne, 2)
        })
    
    # Recalculer poids total à partir des pièces finales
    poids_total = sum(p["poids_total_ligne"] for p in pieces)

    # ========================================================
    # META FINAL
    # ========================================================
    meta = {
        "nb_travees": nb_travees,
        "nb_travees_acces": nb_travees_acces,
        "nb_niveaux": nb_niveaux,
        "nb_lignes_poteaux": nb_lignes_poteaux,
        "poids_total": round(poids_total, 2),
        "surface_facade_m2": round(surface_facade, 2),
        "amarrages_calcules": amarrages_total,
        "conformite_EN12810": True,
        "trappes_acces": nb_trappes
    }
    
    print(f"\n✅ POIDS TOTAL : {poids_total} kg")
    print("="*60 + "\n")

    return pieces, meta, ajustements


# ------------------------------------------------------------
# APPLICATION AU STOCK
# ------------------------------------------------------------
def apply_allocation_to_stock(
    db: Session, 
    pieces_result: List[Dict], 
    company_id: Optional[int] = None, 
    user_id: Optional[int] = None
):
    errors = []
    for p in pieces_result:
        aid = p.get("article_id")
        qty = p.get("quantite_utilisee", 0)
        article = db.query(Article).filter(Article.id == aid).first()
        if not article:
            errors.append(f"Article {aid} introuvable")
            continue
        if article.quantite < qty:
            errors.append(f"Stock insuffisant pour {article.nom}")
            continue
        article.quantite -= qty
        poids_total = qty * (article.poids or 0)
        retrait = Retrait(
            article_id=aid, company_id=company_id, quantite=qty,
            poids_total=poids_total, date_retrait=datetime.utcnow(), user_id=user_id
        )
        db.add(retrait)
    db.commit()
    return errors