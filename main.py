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
from models import User, RoleEnum, Company, CompanyStatusEnum
from email_service import generate_temp_password, send_welcome_email
import io
from database import SessionLocal, engine, Base, get_db
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
    import os
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("🔧 Création automatique du superadmin...")
            new_admin = User(
                username="admin",
                password_hash=get_password_hash(os.getenv("SUPERADMIN_PASSWORD", "changeme_at_first_login")),
                role=RoleEnum.SUPERADMIN,
                first_login=True,
                password_reset_required=True,
            )
            db.add(new_admin)
            db.commit()
            print("✅ Superadmin créé depuis variable d'environnement SUPERADMIN_PASSWORD")
    finally:
        db.close()

# Configuration CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://api-stock-echafaudages.onrender.com",
    "https://api-stock-echafaudages.vercel.app",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return {
        "access_token": token,
        "token_type": "bearer",
        "first_login": user.first_login
    }

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
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur serveur : " + str(e))

@app.get("/entreprises/", response_model=List[schemas.EntrepriseResponse])
def list_entreprises(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_superadmin)
):
    """Lister toutes les entreprises (Superadmin uniquement)"""
    return db.query(models.Company).all()

# ===================== SUPERADMIN - GESTION ENTREPRISES =====================

@app.post("/superadmin/companies/{company_id}/suspend")
def suspend_company(
    company_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.require_superadmin)
):
    company = db.query(models.Company).get(company_id)
    if not company:
        raise HTTPException(404, "Entreprise introuvable")
    company.status = CompanyStatusEnum.SUSPENDED
    company.suspended_at = datetime.utcnow()
    users = db.query(models.User).filter(models.User.company_id == company_id).all()
    for user in users:
        user.is_active = False
    db.commit()
    return {"message": "Entreprise suspendue"}


@app.post("/superadmin/companies/{company_id}/activate")
def activate_company(
    company_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.require_superadmin)
):
    company = db.query(models.Company).get(company_id)
    if not company:
        raise HTTPException(404, "Entreprise introuvable")
    company.status = CompanyStatusEnum.ACTIVE
    company.suspended_at = None
    company.terminated_at = None
    users = db.query(models.User).filter(models.User.company_id == company_id).all()
    for user in users:
        user.is_active = True
    db.commit()
    return {"message": "Entreprise réactivée"}


@app.post("/superadmin/companies/{company_id}/terminate")
def terminate_company(
    company_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.require_superadmin)
):
    company = db.query(models.Company).get(company_id)
    if not company:
        raise HTTPException(404, "Entreprise introuvable")
    company.status = CompanyStatusEnum.TERMINATED
    company.terminated_at = datetime.utcnow()
    db.commit()
    return {"message": "Entreprise résiliée définitivement"}


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
    existing_user = crud.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")
    hashed_password = auth.get_password_hash(user.password)
    company_id = user.company_id
    if current_user.role == models.RoleEnum.ADMIN and not company_id:
        company_id = current_user.company_id
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
    try:
        from jose import jwt, JWTError
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token invalide")
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
        return {
            "id": user.id,
            "username": user.username,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            "company_id": user.company_id,
            "company_name": user.company.name if user.company else None,
            "first_login": user.first_login
        }
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/users/", response_model=List[schemas.UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin_or_super)
):
    """Lister les utilisateurs"""
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
    if not article.company_id and current_user.company_id:
        article.company_id = current_user.company_id
    return crud.create_article(db, article)

@app.get("/articles/", response_model=List[schemas.ArticleResponse])
def list_articles(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Lister les articles"""
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
    """Supprimer un article"""
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    if current_user.role != models.RoleEnum.SUPERADMIN:
        if article.company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Accès refusé")
    return crud.delete_article_by_id(db, article_id)

@app.get("/articles/noms", response_model=list[str])
def get_article_names(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    articles = db.query(models.Article.nom).filter(
        models.Article.company_id == current_user.company_id
    ).all()
    return [a.nom for a in articles]

# -----------------------------
# 📤 RETRAITS
# -----------------------------
@app.post("/retraits/", response_model=schemas.ArticleRetraitResponse)
def retirer_article(
    retrait: schemas.RetraitRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    article = db.query(models.Article).filter(
        models.Article.nom == retrait.nom_article,
        models.Article.company_id == current_user.company_id
    ).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article introuvable")
    return crud.retirer_article_by_id(
        db=db,
        article_id=article.id,
        quantite=retrait.quantite,
        company_id=current_user.company_id,
        user_id=current_user.id
    )

@app.get("/retraits/", response_model=List[schemas.RetraitRead])
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
    company_id = calcul.company_id or current_user.company_id

    pieces_brutes, meta, ajustements = crud.allocate_echafaudage(
        db=db,
        hauteur=calcul.hauteur,
        longueur=calcul.longueur,
        largeur=calcul.largeur,
        company_id=company_id,
        niveaux_travail=calcul.niveaux_travail
    )

    pieces_normalisees = []
    if isinstance(pieces_brutes, list):
        for p in pieces_brutes:
            if isinstance(p, dict):
                pieces_normalisees.append({
                    "article_id": p.get("article_id"),
                    "nom": p.get("nom", "Article inconnu"),
                    "quantite_utilisee": p.get("quantite_utilisee", 0),
                    "longueur": p.get("longueur"),
                    "largeur": p.get("largeur"),
                    "hauteur": p.get("hauteur"),
                    "poids_unitaire": p.get("poids_unitaire", 0),
                    "poids_total_ligne": p.get("poids_total_ligne", 0),
                    "note": p.get("note")
                })

    if calcul.apply_to_stock:
        erreurs_stock = crud.apply_allocation_to_stock(
            db=db,
            pieces_result=pieces_normalisees,
            company_id=company_id,
            user_id=current_user.id
        )
        if erreurs_stock:
            ajustements.extend(erreurs_stock)

    poids_total = meta.get("poids_total", 0)

    # Enregistrer le chantier
    chantier = models.Chantier(
        company_id=company_id,
        nom_chantier=calcul.nom_chantier,
        duree_location=calcul.duree_location,
        hauteur=calcul.hauteur,
        longueur=calcul.longueur,
        largeur=calcul.largeur,
        niveaux_travail=calcul.niveaux_travail,
        poids_total=poids_total
    )
    db.add(chantier)
    db.commit()
    db.refresh(chantier)
    meta["chantier_id"] = chantier.id

    return schemas.CalculResponse(
        pieces=[schemas.PieceUsed(**p) for p in pieces_normalisees],
        poids_total=poids_total,
        meta=meta,
        ajustements=ajustements
    )

@app.get("/chantiers/", response_model=List[schemas.ChantierResponse])
def get_chantiers(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    chantiers = db.query(models.Chantier).filter(
        models.Chantier.company_id == current_user.company_id
    ).order_by(models.Chantier.date_creation.desc()).all()
    return chantiers

@app.delete("/chantiers/{chantier_id}")
def delete_chantier(
    chantier_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    chantier = db.query(models.Chantier).filter(
        models.Chantier.id == chantier_id,
        models.Chantier.company_id == current_user.company_id
    ).first()
    if not chantier:
        raise HTTPException(status_code=404, detail="Chantier non trouvé")
    db.delete(chantier)
    db.commit()
    return {"message": "Chantier supprimé avec succès"}

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
        # ✅ CORRIGÉ : category (pas categorie)
        "categories": db.query(models.Article.category).distinct().count()
    }

@app.get("/stats/categories")
def get_category_stats(db: Session = Depends(get_db)):
    """Statistiques par catégorie"""
    stats = get_stats_by_category(db)
    return [
        {
            "categorie": stat.categorie,  # alias défini dans crud_filters.py
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
    return get_recent_retraits(db, days, limit)

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
    """Ajuster le stock d'un article"""
    article = crud.get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    nouvelle_quantite = article.quantite + quantite
    if nouvelle_quantite < 0:
        raise HTTPException(status_code=400, detail="Stock insuffisant")
    ancienne_quantite = article.quantite
    article.quantite = nouvelle_quantite
    db.commit()
    return {
        "message": "Stock ajusté avec succès",
        "article_id": article_id,
        "ancienne_quantite": ancienne_quantite,
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
    """Exporte l'inventaire complet en PDF"""
    articles = search_articles(db, categorie=categorie, min_stock=min_stock)
    if not articles:
        raise HTTPException(status_code=404, detail="Aucun article trouvé")
    stats = {
        "total_articles": len(articles),
        "stock_total": sum(a.quantite for a in articles),
        "alertes_stock_faible": sum(1 for a in articles if a.quantite <= 10),
        # ✅ CORRIGÉ : a.category (pas a.categorie)
        "categories": len(set(a.category for a in articles))
    }
    pdf_content = create_inventory_pdf(articles, stats)
    return StreamingResponse(
        io.BytesIO(pdf_content),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=inventaire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"}
    )

@app.get("/export/low-stock/pdf")
def export_low_stock_pdf(threshold: int = 10, db: Session = Depends(get_db)):
    """Exporte un rapport d'alerte pour les articles en stock faible"""
    articles = get_low_stock_articles(db, threshold)
    if not articles:
        raise HTTPException(status_code=404, detail="Aucun article en stock faible trouvé")
    pdf_content = create_low_stock_alert_pdf(articles)
    return StreamingResponse(
        io.BytesIO(pdf_content),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=alerte_stock_{datetime.now().strftime('%Y%m%d')}.pdf"}
    )

@app.get("/export/categories/pdf")
def export_categories_pdf(db: Session = Depends(get_db)):
    """Exporte un rapport des statistiques par catégorie en PDF"""
    stats = get_stats_by_category(db)
    if not stats:
        raise HTTPException(status_code=404, detail="Aucune statistique disponible")
    categories_data = [
        {
            "categorie": stat.categorie,
            "nombre_articles": stat.nombre_articles,
            "stock_total": stat.stock_total
        }
        for stat in stats
    ]
    pdf_content = create_category_report_pdf(categories_data)
    return StreamingResponse(
        io.BytesIO(pdf_content),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=rapport_categories_{datetime.now().strftime('%Y%m%d')}.pdf"}
    )

@app.get("/export/custom/pdf")
def export_custom_pdf(
    search: Optional[str] = None,
    categorie: Optional[str] = None,
    min_stock: Optional[int] = None,
    max_stock: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Export PDF personnalisé avec filtres avancés"""
    articles = search_articles(db, search=search, categorie=categorie, min_stock=min_stock, max_stock=max_stock)
    if not articles:
        raise HTTPException(status_code=404, detail="Aucun article correspondant aux critères")
    stats = {
        "total_articles": len(articles),
        "stock_total": sum(a.quantite for a in articles),
        "alertes_stock_faible": sum(1 for a in articles if a.quantite <= 10),
        # ✅ CORRIGÉ : a.category (pas a.categorie)
        "categories": len(set(a.category for a in articles))
    }
    pdf_content = create_inventory_pdf(articles, stats)
    return StreamingResponse(
        io.BytesIO(pdf_content),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=rapport_personnalise_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"}
    )

# ======================= GESTION ADMINS/USERS =======================

@app.post("/admin/create-admin")
async def create_admin_for_company(
    admin_data: schemas.AdminCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_superadmin)
):
    """Créer un admin pour une entreprise (SUPERADMIN uniquement)"""
    existing_user = crud.get_user_by_username(db, admin_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur existe déjà")
    company = crud.get_entreprise_by_id(db, admin_data.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Entreprise introuvable")
    temp_password = generate_temp_password()
    hashed_password = auth.get_password_hash(temp_password)
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
    try:
        send_welcome_email(
            username=admin_data.username,
            email=admin_data.email,
            temp_password=temp_password,
            role="admin",
            company_name=company.name
        )
        email_sent = True
    except Exception as e:
        print(f"⚠️ Erreur envoi email : {e}")
        email_sent = False
    return {
        "message": "Admin créé avec succès",
        "username": new_admin.username,
        "email": admin_data.email,
        "company": company.name,
        "email_sent": email_sent,
        "first_login_required": True
    }

@app.post("/admin/create-user")
async def create_user_for_company(
    user_data: schemas.UserCreateByAdmin,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin_or_super)
):
    """Créer un user pour son entreprise (ADMIN uniquement)"""
    if current_user.role == models.RoleEnum.ADMIN:
        if user_data.company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Vous ne pouvez créer des utilisateurs que pour votre entreprise")
    existing_user = crud.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur existe déjà")
    company = crud.get_entreprise_by_id(db, user_data.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Entreprise introuvable")
    temp_password = generate_temp_password()
    hashed_password = auth.get_password_hash(temp_password)
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
    try:
        send_welcome_email(
            username=user_data.username,
            email=user_data.email,
            temp_password=temp_password,
            role="user",
            company_name=company.name
        )
        email_sent = True
    except Exception as e:
        print(f"⚠️ Erreur envoi email : {e}")
        email_sent = False
    # ✅ CORRIGÉ : temp_password retiré de la réponse (sécurité)
    return {
        "message": "Utilisateur créé avec succès",
        "username": new_user.username,
        "email": user_data.email,
        "company": company.name,
        "email_sent": email_sent,
        "first_login_required": True
    }

@app.post("/auth/change-password")
def change_password(
    password_data: schemas.PasswordChange,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Changer le mot de passe"""
    if not auth.verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect")
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if auth.verify_password(password_data.new_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Le nouveau mot de passe doit être différent de l'ancien")
    user.password_hash = auth.get_password_hash(password_data.new_password)
    user.first_login = False
    user.password_reset_required = False
    db.commit()
    return {"message": "Mot de passe changé avec succès", "first_login": False}

@app.get("/admin/list-admins")
async def list_admins(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_superadmin)
):
    """Lister tous les administrateurs (SUPERADMIN uniquement)"""
    admins = db.query(models.User).filter(models.User.role == models.RoleEnum.ADMIN).all()
    return [
        {
            "id": admin.id,
            "username": admin.username,
            "email": admin.email,
            "company_id": admin.company_id,
            "company_name": admin.company.name if admin.company else None,
            "created_at": admin.created_at.isoformat() if hasattr(admin, 'created_at') and admin.created_at else None,
            "first_login": admin.first_login
        }
        for admin in admins
    ]

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
            "first_login": user.first_login
        }
        for user in users
    ]

@app.delete("/admin/users/{user_id}")
def delete_user_by_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin_or_super)
):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(404, "Utilisateur introuvable")
    if current_user.role == RoleEnum.ADMIN and user.company_id != current_user.company_id:
        raise HTTPException(403, "Action interdite")
    db.delete(user)
    db.commit()
    return {"message": "Utilisateur supprimé avec succès"}

# -----------------------------
# 🏥 HEALTHCHECK
# -----------------------------
@app.get("/")
def root():
    return {
        "message": "API Gestion de Stock Multi-Entreprises",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
