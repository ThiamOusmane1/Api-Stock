# schemas.py
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

# -----------------------------
# AUTH / USERS
# -----------------------------
class Login(BaseModel):
    """Schéma pour la connexion"""
    username: str
    password: str

class Token(BaseModel):
    """Schéma pour le token JWT"""
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    """Schéma pour créer un utilisateur"""
    username: str
    password: str
    role: str  # "superadmin", "admin", "user"
    company_id: Optional[int] = None

class UserResponse(BaseModel):
    """Schéma pour la réponse utilisateur"""
    id: int
    username: str
    role: str
    company_id: Optional[int] = None
    company_name: Optional[str] = None
    first_login: bool = False 
    email: Optional[str] = None

    class Config:
        from_attributes = True

# -----------------------------
# ENTREPRISES
# -----------------------------
class EntrepriseCreate(BaseModel):
    """Schéma pour créer une entreprise"""
    nom: str

class EntrepriseResponse(BaseModel):
    """Schéma pour la réponse entreprise"""
    id: int
    name: str

    class Config:
        from_attributes = True

# -----------------------------
# ARTICLES
# -----------------------------
class ArticleBase(BaseModel):
    """Schéma de base pour un article"""
    nom: str
    description: Optional[str] = None
    quantite: int = 0
    longueur: Optional[float] = None
    largeur: Optional[float] = None
    hauteur: Optional[float] = None
    poids: Optional[float] = None

class ArticleCreate(ArticleBase):
    """Schéma pour créer un article"""
    company_id: Optional[int] = None

class ArticleUpdate(BaseModel):
    """Schéma pour mettre à jour la quantité d'un article"""
    quantite: int

class ArticleResponse(ArticleBase):
    """Schéma pour la réponse article"""
    id: int
    company_id: Optional[int] = None

    class Config:
        from_attributes = True

# -----------------------------
# RETRAITS
# -----------------------------
class RetraitRequest(BaseModel):
    """Schéma pour demander un retrait"""
    quantite: int

class Retrait(BaseModel):
    """Schéma complet d'un retrait"""
    id: int
    company_id: Optional[int]
    article_id: int
    quantite: int
    poids_total: float
    date: datetime
    user_id: Optional[int]

    class Config:
        from_attributes = True

class ArticleRetraitResponse(BaseModel):
    """Schéma pour la réponse après un retrait"""
    message: str
    article_id: int
    nom_article: str
    quantite_retirée: int
    poids_total: float
    stock_restant: int

# -----------------------------
# CALCUL / ALLOCATION ÉCHAFAUDAGE
# -----------------------------
class PieceUsed(BaseModel):
    """Schéma pour une pièce utilisée dans le calcul"""
    article_id: Optional[int] = None
    nom: str
    longueur: Optional[float] = None
    largeur: Optional[float] = None
    hauteur: Optional[float] = None
    poids: Optional[float] = None
    quantite_utilisee: int
    note: Optional[str] = None

class CalculRequest(BaseModel):
    """Schéma pour demander un calcul d'échafaudage"""
    hauteur: float
    longueur: float
    largeur: float
    company_id: Optional[int] = None
    apply_to_stock: bool = False

class CalculResponse(BaseModel):
    """Schéma pour la réponse du calcul"""
    pieces: List[PieceUsed]
    poids_total: float
    meta: Dict
    ajustements: List[str]

    # ======================= NOUVEAUX SCHÉMAS - GESTION ADMIN/USER =======================

class AdminCreate(BaseModel):
    """Schéma pour créer un admin (par SUPERADMIN)"""
    username: str
    email: str
    company_id: int

class UserCreateByAdmin(BaseModel):
    """Schéma pour créer un user (par ADMIN)"""
    username: str
    email: str
    company_id: int

class PasswordChange(BaseModel):
    """Schéma pour changer le mot de passe"""
    old_password: str
    new_password: str