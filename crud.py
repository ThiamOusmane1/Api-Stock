# crud.py
from database import database
from models import entreprises, users, articles, retraits
import schemas
from sqlalchemy import select, insert, update, and_, delete
from fastapi import HTTPException
from typing import Optional, List, Dict, Tuple
from datetime import datetime
import math

# -------------------- ENTREPRISES / USERS --------------------
async def create_entreprise(nom: str):
    q = insert(entreprises).values(nom=nom)
    eid = await database.execute(q)
    return {"id": eid, "nom": nom}

async def get_entreprise_by_id(eid: int):
    q = select(entreprises).where(entreprises.c.id == eid)
    return await database.fetch_one(q)

async def create_user(username: str, hashed_password: str, role: str = "user", entreprise_id: Optional[int] = None):
    q = insert(users).values(username=username, hashed_password=hashed_password, role=role, entreprise_id=entreprise_id)
    uid = await database.execute(q)
    return {"id": uid, "username": username, "role": role, "entreprise_id": entreprise_id}

async def get_user_by_username(username: str):
    q = select(users).where(users.c.username == username)
    return await database.fetch_one(q)

# -------------------- ARTICLES --------------------
async def get_articles_for_entreprise(entreprise_id: Optional[int] = None):
    q = select(articles)
    if entreprise_id is not None:
        q = q.where(articles.c.entreprise_id == entreprise_id)
    return await database.fetch_all(q)

async def get_article_by_fields(nom: str, longueur, largeur, hauteur, entreprise_id: Optional[int] = None):
    conds = [articles.c.nom == nom]
    if entreprise_id is not None:
        conds.append(articles.c.entreprise_id == entreprise_id)

    if longueur is None:
        conds.append(articles.c.longueur.is_(None))
    else:
        conds.append(articles.c.longueur == longueur)

    if largeur is None:
        conds.append(articles.c.largeur.is_(None))
    else:
        conds.append(articles.c.largeur == largeur)

    if hauteur is None:
        conds.append(articles.c.hauteur.is_(None))
    else:
        conds.append(articles.c.hauteur == hauteur)

    q = select(articles).where(and_(*conds))
    return await database.fetch_one(q)

async def create_article(article: schemas.ArticleCreate):
    q = insert(articles).values(**article.dict())
    article_id = await database.execute(q)
    return {**article.dict(), "id": article_id}

async def update_article_quantite_by_id(article_id: int, nouvelle_qte: int):
    q = update(articles).where(articles.c.id == article_id).values(quantite=nouvelle_qte)
    await database.execute(q)
    s = select(articles).where(articles.c.id == article_id)
    return await database.fetch_one(s)

async def delete_article_by_id(article_id: int):
    q = delete(articles).where(articles.c.id == article_id)
    await database.execute(q)
    return {"message": "Article supprimé", "id": article_id}

# -------------------- RETRAITS --------------------
async def retirer_article_by_id(article_id: int, quantite: int, entreprise_id: Optional[int] = None, user_id: Optional[int] = None):
    q = select(articles).where(articles.c.id == article_id)
    article = await database.fetch_one(q)
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    if article["quantite"] < quantite:
        raise HTTPException(status_code=400, detail="Pas assez de stock")
    nouvelle_qte = article["quantite"] - quantite
    poids_total = quantite * (article["poids"] or 0)
    await database.execute(update(articles).where(articles.c.id == article_id).values(quantite=nouvelle_qte))
    await database.execute(insert(retraits).values(article_id=article_id, entreprise_id=entreprise_id, quantite=quantite, poids_total=poids_total, date=datetime.utcnow(), user_id=user_id))
    return schemas.RetraitResponse(
        message="Retrait effectué avec succès",
        article_id=article_id,
        nom_article=article["nom"],
        quantite_retirée=quantite,
        poids_total=poids_total,
        stock_restant=nouvelle_qte
    )

async def get_retraits_for_entreprise(entreprise_id: Optional[int] = None):
    q = select(retraits)
    if entreprise_id:
        q = q.where(retraits.c.entreprise_id == entreprise_id)
    return await database.fetch_all(q)

# -------------------- HELPERS CATEGORIE --------------------
SYNONYMES = {
    "poteau": ["poteau", "montant", "standard", "upright"],
    "moise": ["moise", "lisse", "longitudinale", "ledger"],
    "transverse": ["transverse", "entretoise", "traverse", "transom"],
    "diagonale": ["diagonale", "contrevent", "brace"],
    "plancher": ["plancher", "plateau", "deck", "platform", "trappe"],
    "plinthe": ["plinthe", "toe board", "toeboard"],
    "gardeCorps": ["garde-corps", "gc", "guardrail", "lisse de protection"],
    "embase": ["embase", "pied", "base jack", "socle"],
    "cale": ["cale", "shim", "bloc"]
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

# -------------------- ALLOCATION (coin change DP + overcover) --------------------
def coin_change_min_pieces(target: float, pieces: List[float], resolution: int = 100) -> Optional[List[float]]:
    T = int(round(target * resolution))
    coin_vals = [int(round(p * resolution)) for p in pieces]
    INF = 10**9
    dp = [INF] * (T + 1)
    parent = [-1] * (T + 1)
    dp[0] = 0
    for i in range(1, T+1):
        for idx, c in enumerate(coin_vals):
            if c <= i and dp[i-c] + 1 < dp[i]:
                dp[i] = dp[i-c] + 1
                parent[i] = idx
    if dp[T] >= INF:
        return None
    res = []
    cur = T
    for _ in range(dp[T]):
        idx = parent[cur]
        res.append(pieces[idx])
        cur -= int(round(pieces[idx] * resolution))
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
            if c <= i and dp[i-c] + 1 < dp[i]:
                dp[i] = dp[i-c] + 1
                parent[i] = idx
    best_i = None
    best_over = None
    best_count = INF
    for i in range(T, T2+1):
        if dp[i] < INF:
            over = i - T
            if (best_over is None) or (over < best_over) or (over == best_over and dp[i] < best_count):
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

# Main allocation
async def allocate_echafaudage(hauteur: float, longueur: float, largeur: float, entreprise_id: Optional[int] = None):
    STANDARD_HEIGHT = 2.0
    MOISES_DISPO = [0.75, 1, 1.5, 2, 2.5, 3]
    DECK_DISPO = [0.75, 1, 1.5, 2, 2.5, 3]

    niveaux = int(hauteur // STANDARD_HEIGHT)
    reste = round(hauteur - niveaux * STANDARD_HEIGHT, 3)
    niveau_list = [STANDARD_HEIGHT] * niveaux
    if reste > 0:
        niveau_list.append(reste)
    nb_niveaux = len(niveau_list)

    # Determine travées using DP strategy + greedy fallback
    travées = []
    remaining = round(longueur, 6)
    while remaining > 1e-6:
        if remaining <= max(MOISES_DISPO):
            combo = coin_change_min_pieces(remaining, MOISES_DISPO, resolution=100)
            if combo:
                travées.extend(combo)
                remaining = 0
                break
            combo2 = coin_change_min_over(remaining, MOISES_DISPO, max_over=max(MOISES_DISPO), resolution=100)
            if combo2:
                travées.extend(combo2)
                remaining = 0
                break
            choices = [m for m in MOISES_DISPO if m <= remaining]
            if choices:
                c = max(choices)
            else:
                c = min(MOISES_DISPO)
            travées.append(c)
            remaining = round(max(0, remaining - c), 6)
        else:
            cands = [m for m in MOISES_DISPO if m <= remaining]
            if not cands:
                c = max(MOISES_DISPO)
            else:
                c = max(cands)
            travées.append(c)
            remaining = round(max(0, remaining - c), 6)

    # deck columns
    if largeur in DECK_DISPO:
        largeurChoisie = largeur
    else:
        le = [d for d in DECK_DISPO if d <= largeur]
        largeurChoisie = le[-1] if le else DECK_DISPO[0]
    deckCols = max(1, int(round(largeur / (largeurChoisie or largeur))))

    nb_travees = len(travées)
    nb_cadres = nb_travees + 1

    besoins = {}
    besoins["embase"] = nb_cadres * 2
    besoins["cale"] = nb_cadres * 2
    besoins["poteau"] = nb_cadres * 2 * nb_niveaux
    besoins["transverse"] = nb_travees * nb_niveaux
    besoins["diagonale"] = max(0, (nb_travees // 2) * nb_niveaux)
    besoins["plancher"] = nb_travees * nb_niveaux * deckCols
    besoins["plinthe"] = besoins["plancher"]
    besoins["gardeCorps"] = nb_travees * nb_niveaux * 2

    # required moises by length
    required_moises_by_length: Dict[float, int] = {}
    for t in travées:
        combo = coin_change_min_pieces(t, MOISES_DISPO, resolution=100)
        if not combo:
            combo = coin_change_min_over(t, MOISES_DISPO, max_over=max(MOISES_DISPO), resolution=100)
        if not combo:
            m = max(MOISES_DISPO)
            count = int(math.ceil(t / m))
            combo = [m] * count
        for length_piece in combo:
            required_moises_by_length[length_piece] = required_moises_by_length.get(length_piece, 0) + 2 * nb_niveaux

    # fetch articles for entreprise
    all_articles = await get_articles_for_entreprise(entreprise_id)

    # group by category
    articles_by_cat: Dict[str, List] = {}
    for a in all_articles:
        cat = detect_categorie(a["nom"])
        articles_by_cat.setdefault(cat, []).append(a)

    pieces_result = []
    ajustements = []

    def allocate_category(cat_name: str, needed: int):
        allocated = []
        remaining_need = needed
        candidates = articles_by_cat.get(cat_name, [])
        candidates = sorted(candidates, key=lambda x: (- (x["quantite"] or 0), 0 if x["longueur"] is None else 1))
        for art in candidates:
            available = art["quantite"] or 0
            take = min(available, remaining_need)
            if take <= 0:
                continue
            allocated.append((art, take))
            remaining_need -= take
            if remaining_need <= 0:
                break
        return allocated, remaining_need

    # allocate generic categories
    for cat in ["embase","cale","poteau","transverse","diagonale","plancher","plinthe","gardeCorps"]:
        need = besoins.get(cat, 0)
        if need <= 0:
            continue
        allocated, rem = allocate_category(cat, need)
        for art, q in allocated:
            pieces_result.append({
                "article_id": art["id"],
                "nom": art["nom"],
                "longueur": art.get("longueur"),
                "largeur": art.get("largeur"),
                "hauteur": art.get("hauteur"),
                "poids": art.get("poids"),
                "quantite_utilisee": q,
                "note": None,
            })
        if rem > 0:
            ajustements.append(f"{cat}: besoin {need} => disponible {need - rem} (manque {rem})")

    # allocate moises by length
    for length_piece, needed_qty in required_moises_by_length.items():
        candidates = [a for a in all_articles if (a.get("longueur") is not None and abs((a.get("longueur") or 0) - length_piece) < 1e-6 and detect_categorie(a["nom"]) == "moise")]
        if not candidates:
            candidates = [a for a in all_articles if detect_categorie(a["nom"]) == "moise"]
            candidates = sorted(candidates, key=lambda x: (abs((x.get("longueur") or 0) - length_piece), - (x.get("quantite") or 0)))
        remaining = needed_qty
        for art in candidates:
            available = art.get("quantite") or 0
            take = min(available, remaining)
            if take <= 0:
                continue
            pieces_result.append({
                "article_id": art["id"],
                "nom": art["nom"],
                "longueur": art.get("longueur"),
                "largeur": art.get("largeur"),
                "hauteur": art.get("hauteur"),
                "poids": art.get("poids"),
                "quantite_utilisee": take,
                "note": f"moise target {length_piece}m",
            })
            remaining -= take
            if remaining <= 0:
                break
        if remaining > 0:
            ajustements.append(f"moise {length_piece}m: besoin {needed_qty} => disponible {needed_qty - remaining} (manque {remaining})")

    # compute poids
    poids_total = sum((p.get("poids") or 0) * p["quantite_utilisee"] for p in pieces_result)

    meta = {"niveaux": nb_niveaux, "travées": travées, "nb_cadres": nb_cadres, "largeurChoisie": largeurChoisie}
    return pieces_result, meta, ajustements

# apply allocation to stock (decrement quantities and add retraits)
async def apply_allocation_to_stock(pieces_result: List[Dict], entreprise_id: Optional[int] = None, user_id: Optional[int] = None):
    errors = []
    for p in pieces_result:
        aid = p.get("article_id")
        qty = p.get("quantite_utilisee", 0)
        if not aid:
            errors.append(f"No article mapping for {p.get('nom')}")
            continue
        q = select(articles).where(articles.c.id == aid)
        art = await database.fetch_one(q)
        if not art:
            errors.append(f"Article id {aid} introuvable")
            continue
        if art["quantite"] < qty:
            errors.append(f"Article {art['nom']} stock insuffisant ({art['quantite']} < {qty})")
            continue
        await database.execute(update(articles).where(articles.c.id == aid).values(quantite=art["quantite"] - qty))
        poids_total = qty * (art.get("poids") or 0)
        await database.execute(insert(retraits).values(article_id=aid, entreprise_id=entreprise_id, quantite=qty, poids_total=poids_total, date=datetime.utcnow(), user_id=user_id))
    return errors
