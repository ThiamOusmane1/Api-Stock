# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from auth import get_password_hash
from models import User, RoleEnum
from email_service import generate_temp_password, send_welcome_email
import io

from database import SessionLocal, engine, Base
import models, schemas, crud, auth
from crud_filters import (
    search_articles, 
    get_low_stock_articles,
    get_stats_by_category,
    get_recent_retraits
)
from pdf_generator import (
    create_inventory_pdf,
    create_low_stock_alert_pdf,
    create_category_report_pdf
)

# Initialisation de la base de données
Base.metadata.create_all(bind=engine)

# Initialisation de l'application FastAPI
app = FastAPI(
    title="API Gestion de Stock Multi-Entreprises",
    description="API sécurisée pour la gestion des articles et retraits par entreprise",
    version="2.0.0"
)

# ============================================================
# 🔐 Création automatique du SUPERADMIN au démarrage
# ============================================================
@app.on_event("startup")
def create_default_superadmin():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("🔧 Création automatique du superadmin...")

            new_admin = User(
                username="admin",
                password_hash=get_password_hash("superadmin"),
                role=RoleEnum.SUPERADMIN,
                first_login=False,
                password_reset_required=False,
            )

            db.add(new_admin)
            db.commit()

            print("✅ Superadmin créé ! (username=admin, password=superadmin)")
    finally:
        db.close()

# Configuration CORS (pour connexion front React)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dépendance pour obtenir la session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# 🧠 AUTHENTIFICATION
# -----------------------------
@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Connexion avec username et password"""
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Bearer"}
        )
    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# -----------------------------
# 👑 SUPER ADMIN : Gestion entreprises
# -----------------------------
@app.post("/entreprises/", response_model=schemas.EntrepriseResponse)
def create_entreprise(
    entreprise: schemas.EntrepriseCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_superadmin)
):
    """Créer une nouvelle entreprise (Superadmin uniquement)"""
    try:
        return crud.create_entreprise(db, entreprise.nom)
    except ValueError as e:
        # Erreur volontaire envoyée depuis crud → ex: doublon
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Erreur imprévue
        raise HTTPException(status_code=500, detail="Erreur serveur : " + str(e))

@app.get("/entreprises/", response_model=List[schemas.EntrepriseResponse])
def list_entreprises(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.require_superadmin)
):
    """Lister toutes les entreprises (Superadmin uniquement)"""
    return db.query(models.Company).all()

# -----------------------------
# 👨‍💼 ADMIN ENTREPRISE : Gestion utilisateurs
# -----------------------------
@app.post("/users/", response_model=schemas.UserResponse)
def create_user(
    user: schemas.UserCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin_or_super)
):
    """Créer un nouvel utilisateur (Admin/Superadmin)"""
    # Vérifier si l'utilisateur existe déjà
    existing_user = crud.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")
    
    # Hash du mot de passe
    hashed_password = auth.get_password_hash(user.password)
    
    # Déterminer le company_id
    company_id = user.company_id
    if current_user.role == models.RoleEnum.ADMIN and not company_id:
        company_id = current_user.company_id
    
    # Créer l'utilisateur
    new_user = crud.create_user(
        db=db,
        username=user.username,
        hashed_password=hashed_password,
        role=user.role,
        company_id=company_id
    )
    
    return new_user

@app.get("/users/me")
async def get_current_user_route(
    token: str = Depends(auth.oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Retourner l'utilisateur actuellement authentifié"""
    print(f"🔍 Route /users/me - Token reçu: {token[:50]}...")
    
    try:
        from jose import jwt, JWTError
        
        # Décoder le token
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        print(f"✅ Token décodé - Username: {username}")
        
        if username is None:
            print("❌ Username est None")
            raise HTTPException(status_code=401, detail="Token invalide")
        
        # Chercher l'utilisateur
        user = db.query(models.User).filter(models.User.username == username).first()
        
        if not user:
            print(f"❌ Utilisateur '{username}' non trouvé en BDD")
            raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
        
        print(f"✅ Utilisateur trouvé: {user.username} (role: {user.role})")
        
        # Retourner la réponse
        return {
            "id": user.id,
            "username": user.username,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            "company_id": user.company_id,
            "company_name": user.company.name if user.company else None
        }
        
    except JWTError as e:
        print(f"❌ Erreur JWT: {e}")
        raise HTTPException(
            status_code=401,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/users/", response_model=List[schemas.UserResponse])
def get_users(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.require_admin_or_super)
):
    """Lister les utilisateurs (Admin voit son entreprise, Superadmin voit tous)"""
    if current_user.role == models.RoleEnum.SUPERADMIN:
        return db.query(models.User).all()
    else:
        return db.query(models.User).filter(
            models.User.company_id == current_user.company_id
        ).all()
    
    

# -----------------------------
# 📦 ARTICLES
# -----------------------------
@app.post("/articles/", response_model=schemas.ArticleResponse)
def create_article(
    article: schemas.ArticleCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Créer un nouvel article"""
    # Si pas de company_id fourni, utiliser celui de l'utilisateur
    if not article.company_id and current_user.company_id:
        article.company_id = current_user.company_id
    
    return crud.create_article(db, article)

@app.get("/articles/", response_model=List[schemas.ArticleResponse])
def list_articles(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    """Lister les articles (filtrés par entreprise sauf pour Superadmin)"""
    if current_user.role == models.RoleEnum.SUPERADMIN:
        return crud.get_articles_for_entreprise(db, None)
    else:
        return crud.get_articles_for_entreprise(db, current_user.company_id)

@app.put("/articles/{article_id}", response_model=schemas.ArticleResponse)
def update_article(
    article_id: int,
    article_update: schemas.ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Mettre à jour la quantité d'un article"""
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    # Vérifier les permissions
    if current_user.role != models.RoleEnum.SUPERADMIN:
        if article.company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Accès refusé")
    
    return crud.update_article_quantite_by_id(db, article_id, article_update.quantite)

@app.delete("/articles/{article_id}")
def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin_or_super)
):
    """Supprimer un article (Admin/Superadmin)"""
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    # Vérifier les permissions
    if current_user.role != models.RoleEnum.SUPERADMIN:
        if article.company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Accès refusé")
    
    return crud.delete_article_by_id(db, article_id)

# -----------------------------
# 📤 RETRAITS
# -----------------------------
@app.post("/retraits/{article_id}", response_model=schemas.ArticleRetraitResponse)
def retirer_article(
    article_id: int,
    retrait: schemas.RetraitRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Effectuer un retrait de stock"""
    return crud.retirer_article_by_id(
        db=db,
        article_id=article_id,
        quantite=retrait.quantite,
        company_id=current_user.company_id,
        user_id=current_user.id
    )

@app.get("/retraits/", response_model=List[schemas.Retrait])
def list_retraits(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    """Lister l'historique des retraits"""
    if current_user.role == models.RoleEnum.SUPERADMIN:
        return db.query(models.Retrait).all()
    else:
        return db.query(models.Retrait).filter(
            models.Retrait.company_id == current_user.company_id
        ).all()

# -----------------------------
# 🧮 CALCUL ÉCHAFAUDAGE
# -----------------------------
@app.post("/calcul/", response_model=schemas.CalculResponse)
def calculer_echafaudage(
    calcul: schemas.CalculRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Calculer les besoins en matériel pour un échafaudage"""
    # Déterminer le company_id
    company_id = calcul.company_id
    if not company_id and current_user.company_id:
        company_id = current_user.company_id
    
    # Effectuer le calcul
    pieces, meta, ajustements = crud.allocate_echafaudage(
        db=db,
        hauteur=calcul.hauteur,
        longueur=calcul.longueur,
        largeur=calcul.largeur,
        company_id=company_id
    )
    
    # Appliquer au stock si demandé
    if calcul.apply_to_stock:
        errors = crud.apply_allocation_to_stock(
            db=db,
            pieces_result=pieces,
            company_id=company_id,
            user_id=current_user.id
        )
        if errors:
            ajustements.extend(errors)
    
    return schemas.CalculResponse(
        pieces=[schemas.PieceUsed(**p) for p in pieces],
        poids_total=meta["poids_total"],
        meta=meta,
        ajustements=ajustements
    )

# ----------------------------- 
# 🔍 RECHERCHE AVANCÉE
# ----------------------------- 

@app.get("/articles/search/", response_model=List[schemas.ArticleResponse])
def search_articles_advanced(
    search: Optional[str] = None,
    categorie: Optional[str] = None,
    min_stock: Optional[int] = None,
    max_stock: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Recherche avancée d'articles avec filtres multiples"""
    articles = search_articles(db, search, categorie, min_stock, max_stock, skip, limit)
    return articles

@app.get("/articles/low-stock/", response_model=List[schemas.ArticleResponse])
def get_low_stock_alert(
    threshold: int = 10,
    db: Session = Depends(get_db)
):
    """Alerte: Articles avec stock faible"""
    return get_low_stock_articles(db, threshold)

# ----------------------------- 
# 📊 STATISTIQUES
# ----------------------------- 

@app.get("/stats/stock")
def get_stock_stats(db: Session = Depends(get_db)):
    """Statistiques globales du stock"""
    total_articles = db.query(models.Article).count()
    stock_total = db.query(func.sum(models.Article.quantite)).scalar() or 0
    alertes = db.query(models.Article).filter(models.Article.quantite <= 10).count()
    
    return {
        "total_articles": total_articles,
        "stock_total": stock_total,
        "alertes_stock_faible": alertes,
        "categories": db.query(models.Article.categorie).distinct().count()
    }

@app.get("/stats/categories")
def get_category_stats(db: Session = Depends(get_db)):
    """Statistiques par catégorie"""
    stats = get_stats_by_category(db)
    return [
        {
            "categorie": stat.categorie,
            "nombre_articles": stat.nombre_articles,
            "stock_total": stat.stock_total
        }
        for stat in stats
    ]

@app.get("/stats/retraits/recent")
def get_recent_withdrawals(
    days: int = 7,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Derniers retraits effectués"""
    retraits = get_recent_retraits(db, days, limit)
    return retraits

@app.get("/stats/retraits/by-user")
def get_withdrawal_stats_by_user(db: Session = Depends(get_db)):
    """Statistiques de retraits par utilisateur"""
    stats = db.query(
        models.Retrait.nom_utilisateur,
        func.count(models.Retrait.id).label('nombre_retraits'),
        func.sum(models.Retrait.quantite).label('total_retire')
    ).group_by(models.Retrait.nom_utilisateur).all()
    
    return [
        {
            "utilisateur": stat.nom_utilisateur,
            "nombre_retraits": stat.nombre_retraits,
            "total_retire": stat.total_retire
        }
        for stat in stats
    ]

# ----------------------------- 
# 🔧 AJUSTEMENTS STOCK
# ----------------------------- 

@app.post("/articles/{article_id}/adjust-stock")
def adjust_stock(
    article_id: int,
    quantite: int,
    raison: str = "Ajustement manuel",
    db: Session = Depends(get_db)
):
    """Ajuster le stock d'un article (ajout ou retrait)"""
    article = crud.get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    nouvelle_quantite = article.quantite + quantite
    if nouvelle_quantite < 0:
        raise HTTPException(status_code=400, detail="Stock insuffisant")
    
    article.quantite = nouvelle_quantite
    db.commit()
    
    return {
        "message": "Stock ajusté avec succès",
        "article_id": article_id,
        "ancienne_quantite": article.quantite - quantite,
        "nouvelle_quantite": article.quantite,
        "raison": raison
    }

# ----------------------------- 
# 📄 EXPORT PDF
# ----------------------------- 

@app.get("/export/inventory/pdf")
def export_inventory_pdf(
    categorie: Optional[str] = None,
    min_stock: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    📄 Exporte l'inventaire complet en PDF
    
    Filtres optionnels:
    - categorie: Filtrer par catégorie
    - min_stock: Stock minimum
    """
    # Récupérer les articles
    articles = search_articles(db, categorie=categorie, min_stock=min_stock)
    
    if not articles:
        raise HTTPException(status_code=404, detail="Aucun article trouvé")
    
    # Récupérer les stats
    total_articles = len(articles)
    stock_total = sum(a.quantite for a in articles)
    alertes = sum(1 for a in articles if a.quantite <= 10)
    categories = len(set(a.categorie for a in articles))
    
    stats = {
        "total_articles": total_articles,
        "stock_total": stock_total,
        "alertes_stock_faible": alertes,
        "categories": categories
    }
    
    # Générer le PDF
    pdf_content = create_inventory_pdf(articles, stats)
    
    # Retourner le PDF
    return StreamingResponse(
        io.BytesIO(pdf_content),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=inventaire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        }
    )


@app.get("/export/low-stock/pdf")
def export_low_stock_pdf(
    threshold: int = 10,
    db: Session = Depends(get_db)
):
    """
    🚨 Exporte un rapport d'alerte pour les articles en stock faible
    """
    articles = get_low_stock_articles(db, threshold)
    
    if not articles:
        raise HTTPException(
            status_code=404, 
            detail="Aucun article en stock faible trouvé"
        )
    
    # Générer le PDF d'alerte
    pdf_content = create_low_stock_alert_pdf(articles)
    
    return StreamingResponse(
        io.BytesIO(pdf_content),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=alerte_stock_{datetime.now().strftime('%Y%m%d')}.pdf"
        }
    )


@app.get("/export/categories/pdf")
def export_categories_pdf(db: Session = Depends(get_db)):
    """
    📊 Exporte un rapport des statistiques par catégorie en PDF
    """
    stats = get_stats_by_category(db)
    
    if not stats:
        raise HTTPException(status_code=404, detail="Aucune statistique disponible")
    
    # Formater les données
    categories_data = [
        {
            "categorie": stat.categorie,
            "nombre_articles": stat.nombre_articles,
            "stock_total": stat.stock_total
        }
        for stat in stats
    ]
    
    # Générer le PDF
    pdf_content = create_category_report_pdf(categories_data)
    
    return StreamingResponse(
        io.BytesIO(pdf_content),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=rapport_categories_{datetime.now().strftime('%Y%m%d')}.pdf"
        }
    )


@app.get("/export/custom/pdf")
def export_custom_pdf(
    search: Optional[str] = None,
    categorie: Optional[str] = None,
    min_stock: Optional[int] = None,
    max_stock: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    🎯 Export PDF personnalisé avec filtres avancés
    """
    articles = search_articles(
        db, 
        search=search, 
        categorie=categorie, 
        min_stock=min_stock, 
        max_stock=max_stock
    )
    
    if not articles:
        raise HTTPException(status_code=404, detail="Aucun article correspondant aux critères")
    
    # Stats basiques
    stats = {
        "total_articles": len(articles),
        "stock_total": sum(a.quantite for a in articles),
        "alertes_stock_faible": sum(1 for a in articles if a.quantite <= 10),
        "categories": len(set(a.categorie for a in articles))
    }
    
    pdf_content = create_inventory_pdf(articles, stats)
    
    return StreamingResponse(
        io.BytesIO(pdf_content),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=rapport_personnalise_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        }
    )

# ======================= GESTION ADMINS/USERS =======================

@app.post("/admin/create-admin")
async def create_admin_for_company(
    admin_data: schemas.AdminCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_superadmin)
):
    """Créer un admin pour une entreprise (SUPERADMIN uniquement)"""
    
    # Vérifier si l'utilisateur existe déjà
    existing_user = crud.get_user_by_username(db, admin_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur existe déjà")
    
    # Vérifier que l'entreprise existe
    company = crud.get_entreprise_by_id(db, admin_data.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Entreprise introuvable")
    
    # Générer un mot de passe temporaire
    temp_password = generate_temp_password()
    hashed_password = auth.get_password_hash(temp_password)
    
    # Créer l'admin
    new_admin = models.User(
        username=admin_data.username,
        password_hash=hashed_password,
        role=models.RoleEnum.ADMIN,
        company_id=admin_data.company_id,
        email=admin_data.email,
        first_login=True,
        password_reset_required=False
    )
    
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    
    # Envoyer l'email
    send_welcome_email(
        username=admin_data.username,
        email=admin_data.email,
        temp_password=temp_password,
        role="admin",
        company_name=company.name
    )
    
    return {
        "message": "Admin créé avec succès",
        "username": new_admin.username,
        "email": admin_data.email,
        "temp_password": temp_password,
        "company": company.name
    }


@app.post("/admin/create-user")
async def create_user_for_company(
    user_data: schemas.UserCreateByAdmin,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin_or_super)
):
    """Créer un user pour son entreprise (ADMIN uniquement)"""
    
    # Si ADMIN, il ne peut créer que pour SON entreprise
    if current_user.role == models.RoleEnum.ADMIN:
        if user_data.company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Vous ne pouvez créer des utilisateurs que pour votre entreprise")
    
    # Vérifier si l'utilisateur existe déjà
    existing_user = crud.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur existe déjà")
    
    # Vérifier que l'entreprise existe
    company = crud.get_entreprise_by_id(db, user_data.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Entreprise introuvable")
    
    # Générer un mot de passe temporaire
    temp_password = generate_temp_password()
    hashed_password = auth.get_password_hash(temp_password)
    
    # Créer l'utilisateur
    new_user = models.User(
        username=user_data.username,
        password_hash=hashed_password,
        role=models.RoleEnum.USER,
        company_id=user_data.company_id,
        email=user_data.email,
        first_login=True,
        password_reset_required=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Envoyer l'email
    send_welcome_email(
        username=user_data.username,
        email=user_data.email,
        temp_password=temp_password,
        role="user",
        company_name=company.name
    )
    
    return {
        "message": "Utilisateur créé avec succès",
        "username": new_user.username,
        "email": user_data.email,
        "temp_password": temp_password,
        "company": company.name
    }


@app.post("/auth/change-password")
async def change_password(
    password_data: schemas.PasswordChange,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Changer le mot de passe (obligatoire à la première connexion)"""
    
    # Vérifier l'ancien mot de passe
    if not auth.verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect")
    
    # Vérifier que le nouveau mot de passe est différent
    if auth.verify_password(password_data.new_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Le nouveau mot de passe doit être différent de l'ancien")
    
    # Valider la force du mot de passe (min 8 caractères)
    if len(password_data.new_password) < 8:
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 8 caractères")
    
    # Mettre à jour le mot de passe
    current_user.password_hash = auth.get_password_hash(password_data.new_password)
    current_user.first_login = False
    current_user.password_reset_required = False
    
    db.commit()
    
    return {"message": "Mot de passe changé avec succès"}


@app.get("/admin/list-admins")
async def list_admins(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_superadmin)
):
    """Lister tous les administrateurs (SUPERADMIN uniquement)"""

    admins = db.query(models.User).filter(
        models.User.role == models.RoleEnum.ADMIN
    ).all()

    return [
        {
            "id": admin.id,
            "username": admin.username,
            "email": admin.email,
            "company_id": admin.company_id,
            "company_name": admin.company.name if admin.company else None,
            "created_at": admin.created_at.isoformat() if hasattr(admin, 'created_at') and admin.created_at else None
        }
        for admin in admins
    ]

# ✅ NOUVELLE ROUTE : Liste des users d'une entreprise
@app.get("/admin/list-users-of-company")
async def list_users_of_company(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin_or_super)
):
    """Lister les users de son entreprise (ADMIN) ou tous (SUPERADMIN)"""
    
    if current_user.role == models.RoleEnum.SUPERADMIN:
        users = db.query(models.User).filter(models.User.role == models.RoleEnum.USER).all()
    else:
        users = db.query(models.User).filter(
            models.User.role == models.RoleEnum.USER,
            models.User.company_id == current_user.company_id
        ).all()
    
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email if hasattr(user, 'email') else None,
            "company_id": user.company_id,
            "company_name": user.company.name if user.company else None,
            "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None,
            "first_login": user.first_login if hasattr(user, 'first_login') else False
        }
        for user in users
    ]

# -----------------------------
# 🏥 HEALTHCHECK
# -----------------------------
@app.get("/")
def root():
    """Page d'accueil de l'API"""
    return {
        "message": "API Gestion de Stock Multi-Entreprises",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health():
    """Vérification de l'état de l'API"""
    return {"status": "healthy"}