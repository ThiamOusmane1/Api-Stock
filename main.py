from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import database, engine, metadata
import crud, schemas, auth
from auth import get_password_hash, verify_password, create_access_token
from fastapi import status
from sqlalchemy import select
from models import users as model_users, entreprises as model_entreprises, articles as model_articles
from typing import Optional
from datetime import timedelta

# create tables (use migrate.py for reset)
metadata.create_all(bind=engine)

app = FastAPI(title="API Stock Échafaudages", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# ------------- AUTH -------------
@app.post("/auth/signup", response_model=schemas.UserResponse)
async def signup(user: schemas.UserCreate, current=Depends(auth.require_superadmin)):
    existing = await crud.get_user_by_username(user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Utilisateur déjà existant")
    hashed = get_password_hash(user.password)
    created = await crud.create_user(user.username, hashed, user.role, user.entreprise_id)
    return created

@app.post("/auth/login", response_model=schemas.Token)
async def login(payload: schemas.UserLogin):
    username = payload.username
    password = payload.password
    user = await crud.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    if not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    access_token_expires = timedelta(hours=8)
    token = create_access_token(
        {"sub": user["username"], "user_id": user["id"], "role": user["role"], "entreprise_id": user["entreprise_id"]},
        expires_delta=access_token_expires
    )
    return {"access_token": token, "token_type": "bearer"}

# ------------- ENTREPRISES -------------
@app.post("/entreprises/", response_model=schemas.EntrepriseResponse)
async def create_entreprise(payload: schemas.EntrepriseCreate, current_user=Depends(auth.require_superadmin)):
    return await crud.create_entreprise(payload.nom)

# ------------- USERS (superadmin/admin) -------------
@app.get("/users/", response_model=list[schemas.UserResponse])
async def list_users(current_user=Depends(auth.require_admin_or_super)):
    q = select(model_users)
    rows = await database.fetch_all(q)
    return rows

# ------------- ARTICLES -------------
@app.get("/articles/", response_model=list[schemas.ArticleResponse])
async def list_articles(entreprise_id: Optional[int] = None, current_user=Depends(auth.get_current_user)):
    if entreprise_id is None:
        entreprise_id = current_user["entreprise_id"]
    return await crud.get_articles_for_entreprise(entreprise_id)

@app.post("/articles/", response_model=schemas.ArticleResponse)
async def add_article(article: schemas.ArticleCreate, current_user=Depends(auth.get_current_user)):
    entreprise_id = article.entreprise_id or current_user["entreprise_id"]
    existing = await crud.get_article_by_fields(article.nom, article.longueur, article.largeur, article.hauteur, entreprise_id)
    if existing:
        updated = await crud.update_article_quantite_by_id(existing["id"], existing["quantite"] + article.quantite)
        return updated
    payload = article.dict()
    payload["entreprise_id"] = entreprise_id
    return await crud.create_article(schemas.ArticleCreate(**payload))

@app.delete("/articles/{article_id}")
async def delete_article(article_id: int, current_user=Depends(auth.get_current_user)):
    q = select(model_articles).where(model_articles.c.id == article_id)
    art = await database.fetch_one(q)
    if not art:
        raise HTTPException(status_code=404, detail="Article introuvable")
    if current_user["role"] != "superadmin" and art["entreprise_id"] != current_user["entreprise_id"]:
        raise HTTPException(status_code=403, detail="Interdit")
    return await crud.delete_article_by_id(article_id)

@app.patch("/articles/{article_id}", response_model=schemas.ArticleResponse)
async def patch_article_quantite(article_id: int, data: schemas.ArticleUpdate, current_user=Depends(auth.get_current_user)):
    q = select(model_articles).where(model_articles.c.id == article_id)
    art = await database.fetch_one(q)
    if not art:
        raise HTTPException(status_code=404, detail="Article introuvable")
    if current_user["role"] != "superadmin" and art["entreprise_id"] != current_user["entreprise_id"]:
        raise HTTPException(status_code=403, detail="Interdit")
    new_qte = art["quantite"] + data.quantite
    if new_qte < 0:
        new_qte = 0
    updated = await crud.update_article_quantite_by_id(article_id, new_qte)
    return updated

# ------------- RETRAITS -------------
@app.post("/articles/{article_id}/retrait", response_model=schemas.RetraitResponse)
async def retrait_article(article_id: int, retrait: schemas.RetraitRequest, current_user=Depends(auth.get_current_user)):
    entreprise_id = current_user["entreprise_id"]
    return await crud.retirer_article_by_id(article_id, retrait.quantite, entreprise_id, current_user["id"])

@app.get("/retraits/", response_model=list[schemas.Retrait])
async def list_retraits(current_user=Depends(auth.get_current_user)):
    entreprise_id = current_user["entreprise_id"]
    return await crud.get_retraits_for_entreprise(entreprise_id)

# ------------- CALCUL (allocation) -------------
@app.post("/calcul/", response_model=schemas.CalculResponse)
async def calcul_echafaudage(req: schemas.CalculRequest, current_user=Depends(auth.get_current_user)):
    entreprise_id = req.entreprise_id or current_user["entreprise_id"]
    pieces, meta, ajustements = await crud.allocate_echafaudage(req.hauteur, req.longueur, req.largeur, entreprise_id)
    if req.apply_to_stock:
        errors = await crud.apply_allocation_to_stock(pieces, entreprise_id, current_user["id"])
        if errors:
            ajustements.extend(errors)
    poids_total = sum((p.get("poids") or 0) * p["quantite_utilisee"] for p in pieces)
    pieces_schema = [
        schemas.PieceUsed(
            article_id=p.get("article_id"),
            nom=p.get("nom"),
            longueur=p.get("longueur"),
            largeur=p.get("largeur"),
            hauteur=p.get("hauteur"),
            poids=p.get("poids"),
            quantite_utilisee=p.get("quantite_utilisee"),
            note=p.get("note")
        )
        for p in pieces
    ]
    return schemas.CalculResponse(pieces=pieces_schema, poids_total=poids_total, meta=meta, ajustements=ajustements)
