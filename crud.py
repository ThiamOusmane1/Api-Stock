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
    # Vérifier si l'entreprise existe déjà
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

# ------------------------------
# ARTICLES
# ------------------------------
def get_articles_for_entreprise(db: Session, company_id: Optional[int] = None):
    query = db.query(Article)
    if company_id is not None:
        query = query.filter(Article.company_id == company_id)
    return query.all()

def get_article_by_fields(db: Session, nom: str, longueur, largeur, hauteur, company_id: Optional[int] = None):
    query = db.query(Article).filter(Article.nom == nom)
    
    if company_id is not None:
        query = query.filter(Article.company_id == company_id)
    
    query = query.filter(
        Article.longueur == longueur if longueur is not None else Article.longueur.is_(None),
        Article.largeur == largeur if largeur is not None else Article.largeur.is_(None),
        Article.hauteur == hauteur if hauteur is not None else Article.hauteur.is_(None)
    )
    
    return query.first()

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
    
    # ✅ CORRECTION : date -> date_retrait
    retrait = Retrait(
        article_id=article_id,
        company_id=company_id,
        quantite=quantite,
        poids_total=poids_total,
        date_retrait=datetime.utcnow(),  # ✅ Corrigé ici
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
# SYNONYMES - catégorisation
# ------------------------------------------------------------
SYNONYMES = {
    "poteau": ["poteau", "upright", "montant"],
    "moise": ["moise", "lisse", "ledger"],
    "transverse": ["transverse", "entretoise", "transom"],
    "diagonale": ["diagonale", "brace"],
    "plancher": ["plancher", "deck", "platform"],
    "plinthe": ["plinthe", "toe board"],
    "gardeCorps": ["garde-corps", "guardrail"],
    "embase": ["embase", "base"],
    "cale": ["cale", "shim"]
}

def detect_categorie(nom: str):
    if not nom:
        return "autres"
    lower = nom.lower()
    for cat, mots in SYNONYMES.items():
        for m in mots:
            if m in lower:
                return cat
    return "autres"

# ------------------------------------------------------------
# ALGORITHMES DE COIN-CHANGE (DP)
# ------------------------------------------------------------
def coin_change_min_pieces(target: float, pieces: List[float], resolution: int = 100) -> Optional[List[float]]:
    T = int(round(target * resolution))
    coin_vals = [int(round(p * resolution)) for p in pieces]
    
    INF = 10**9
    dp = [INF] * (T + 1)
    parent = [-1] * (T + 1)
    
    dp[0] = 0
    
    for i in range(1, T+1):
        for idx, c in enumerate(coin_vals):
            if c <= i and dp[i - c] + 1 < dp[i]:
                dp[i] = dp[i - c] + 1
                parent[i] = idx
    
    if dp[T] >= INF:
        return None
    
    res = []
    cur = T
    for _ in range(dp[T]):
        idx = parent[cur]
        res.append(pieces[idx])
        cur -= coin_vals[idx]
    
    return res

def coin_change_min_over(target: float, pieces: List[float], max_over: float = 1.0, resolution: int = 100) -> Optional[List[float]]:
    T = int(round(target * resolution))
    T2 = int(round((target + max_over) * resolution))
    
    coin_vals = [int(round(p * resolution)) for p in pieces]
    
    INF = 10**9
    dp = [INF] * (T2 + 1)
    parent = [-1] * (T2 + 1)
    
    dp[0] = 0
    
    for i in range(1, T2+1):
        for idx, c in enumerate(coin_vals):
            if c <= i and dp[i - c] + 1 < dp[i]:
                dp[i] = dp[i - c] + 1
                parent[i] = idx
    
    best_i = None
    best_over = None
    best_count = INF
    
    for i in range(T, T2+1):
        if dp[i] < INF:
            over = i - T
            if best_over is None or over < best_over or (over == best_over and dp[i] < best_count):
                best_over = over
                best_count = dp[i]
                best_i = i
    
    if best_i is None:
        return None
    
    res = []
    cur = best_i
    for _ in range(best_count):
        idx = parent[cur]
        res.append(pieces[idx])
        cur -= coin_vals[idx]
    
    return res

# ------------------------------------------------------------
# ALLOCATION D'ÉCHAFAUDAGE
# ------------------------------------------------------------
def allocate_echafaudage(db: Session, hauteur: float, longueur: float, largeur: float, company_id: Optional[int] = None):
    
    STANDARD_HEIGHT = 2.0
    MOISES_DISPO = [0.75, 1, 1.5, 2, 2.5, 3]
    DECK_DISPO = [0.75, 1, 1.5, 2, 2.5, 3]
    
    # ------------------------------
    # CALCUL DES NIVEAUX
    # ------------------------------
    niveaux = int(hauteur // STANDARD_HEIGHT)
    reste = round(hauteur - niveaux * STANDARD_HEIGHT, 3)
    
    niveau_list = [STANDARD_HEIGHT] * niveaux
    if reste > 0:
        niveau_list.append(reste)
    
    nb_niveaux = len(niveau_list)
    
    # ------------------------------
    # CALCUL DES TRAVÉES PAR DP / GREEDY AMÉLIORÉ
    # ------------------------------
    travees = []
    remaining = round(longueur, 6)
    
    while remaining > 1e-6:
        if remaining <= max(MOISES_DISPO):
            combo = coin_change_min_pieces(remaining, MOISES_DISPO)
            if combo:
                travees.extend(combo)
                remaining = 0
                break
            
            combo2 = coin_change_min_over(remaining, MOISES_DISPO)
            if combo2:
                travees.extend(combo2)
                remaining = 0
                break
            
            choices = [m for m in MOISES_DISPO if m <= remaining]
            if choices:
                c = max(choices)
            else:
                c = min(MOISES_DISPO)
            
            travees.append(c)
            remaining = round(max(0, remaining - c), 6)
        else:
            cands = [m for m in MOISES_DISPO if m <= remaining]
            if not cands:
                c = max(MOISES_DISPO)
            else:
                c = max(cands)
            travees.append(c)
            remaining = round(max(0, remaining - c), 6)
    
    # ------------------------------
    # CHOIX DES PLANCHERS / LARGEUR
    # ------------------------------
    if largeur in DECK_DISPO:
        largeurChoisie = largeur
    else:
        compatibles = [d for d in DECK_DISPO if d <= largeur]
        largeurChoisie = compatibles[-1] if compatibles else DECK_DISPO[0]
    
    deckCols = max(1, int(round(largeur / (largeurChoisie or largeur))))
    
    nb_travees = len(travees)
    nb_cadres = nb_travees + 1
    
    # ------------------------------
    # CALCUL DES BESOINS EN PIÈCES
    # ------------------------------
    besoins = {
        "embase": nb_cadres * 2,
        "cale": nb_cadres * 2,
        "poteau": nb_cadres * 2 * nb_niveaux,
        "transverse": nb_travees * nb_niveaux,
        "diagonale": max(0, (nb_travees // 2) * nb_niveaux),
        "plancher": nb_travees * nb_niveaux * deckCols,
        "plinthe": nb_travees * nb_niveaux * deckCols,
        "gardeCorps": nb_travees * nb_niveaux * 2,
    }
    
    # ------------------------------
    # CALCUL SPÉCIFIQUE DES MOISES PAR LONGUEUR
    # ------------------------------
    required_moises_by_length: Dict[float, int] = {}
    
    for t in travees:
        combo = coin_change_min_pieces(t, MOISES_DISPO)
        if not combo:
            combo = coin_change_min_over(t, MOISES_DISPO)
        
        if not combo:
            m = max(MOISES_DISPO)
            count = math.ceil(t / m)
            combo = [m] * count
        
        for length_piece in combo:
            required_moises_by_length[length_piece] = required_moises_by_length.get(length_piece, 0) + 2 * nb_niveaux
    
    # ------------------------------
    # RÉCUPÉRER ARTICLES DISPONIBLES
    # ------------------------------
    all_articles = get_articles_for_entreprise(db, company_id)
    
    articles_by_cat: Dict[str, List] = {}
    for a in all_articles:
        cat = detect_categorie(a.nom)
        articles_by_cat.setdefault(cat, []).append(a)
    
    pieces_result = []
    ajustements = []
    
    # ------------------------------
    # ALLOCATION PAR CATÉGORIE STANDARD
    # ------------------------------
    def allocate_category(cat_name: str, needed: int):
        allocated = []
        remaining_need = needed
        
        candidates = articles_by_cat.get(cat_name, [])
        candidates = sorted(candidates, key=lambda x: -x.quantite)
        
        for art in candidates:
            available = art.quantite
            take = min(available, remaining_need)
            if take > 0:
                allocated.append((art, take))
                remaining_need -= take
            if remaining_need <= 0:
                break
        
        return allocated, remaining_need
    
    for cat in besoins:
        needed = besoins[cat]
        allocated, rem = allocate_category(cat, needed)
        
        for art, q in allocated:
            pieces_result.append({
                "article_id": art.id,
                "nom": art.nom,
                "longueur": art.longueur,
                "largeur": art.largeur,
                "hauteur": art.hauteur,
                "poids": art.poids,
                "quantite_utilisee": q,
                "note": None,
            })
        
        if rem > 0:
            ajustements.append(f"{cat}: manque {rem} pièces")
    
    # ------------------------------
    # ALLOCATION DES MOISES PAR LONGUEUR
    # ------------------------------
    for length_piece, needed_qty in required_moises_by_length.items():
        candidates = [
            a for a in all_articles
            if detect_categorie(a.nom) == "moise"
            and a.longueur == length_piece
        ]
        
        if not candidates:
            candidates = [
                a for a in all_articles
                if detect_categorie(a.nom) == "moise"
            ]
            candidates = sorted(candidates, key=lambda x: abs((x.longueur or 0) - length_piece))
        
        remaining = needed_qty
        
        for art in candidates:
            available = art.quantite
            take = min(available, remaining)
            
            if take > 0:
                pieces_result.append({
                    "article_id": art.id,
                    "nom": art.nom,
                    "longueur": art.longueur,
                    "largeur": art.largeur,
                    "hauteur": art.hauteur,
                    "poids": art.poids,
                    "quantite_utilisee": take,
                    "note": f"moise {length_piece}m",
                })
                remaining -= take
            
            if remaining <= 0:
                break
        
        if remaining > 0:
            ajustements.append(f"moise {length_piece}m: manque {remaining}")
    
    # ------------------------------
    # POIDS TOTAL
    # ------------------------------
    poids_total = sum(
        (p.get("poids") or 0) * p["quantite_utilisee"]
        for p in pieces_result
    )
    
    meta = {
        "niveaux": nb_niveaux,
        "travees": travees,
        "nb_cadres": nb_cadres,
        "largeurChoisie": largeurChoisie,
        "poids_total": poids_total,
    }
    
    return pieces_result, meta, ajustements


# ------------------------------------------------------------
# APPLICATION DE L'ALLOCATION AU STOCK
# ------------------------------------------------------------
def apply_allocation_to_stock(db: Session, pieces_result: List[Dict], company_id: Optional[int] = None, user_id: Optional[int] = None):
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
        
        # ✅ CORRECTION : date -> date_retrait
        retrait = Retrait(
            article_id=aid,
            company_id=company_id,
            quantite=qty,
            poids_total=poids_total,
            date_retrait=datetime.utcnow(),  # ✅ Corrigé ici
            user_id=user_id
        )
        
        db.add(retrait)
    
    db.commit()
    return errors