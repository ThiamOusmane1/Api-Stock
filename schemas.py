# schemas.py
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List, Dict
from models import CompanyStatusEnum
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
    first_login: bool = False

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

    model_config = ConfigDict(from_attributes=True)

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
    status: CompanyStatusEnum
    suspended_at: datetime | None
    terminated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

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
    
    @field_validator("quantite")
    @classmethod
    def quantite_positive(cls, v):
        if v < 0:
            raise ValueError('La quantité doit être positive ou nulle')
        return v

class ArticleCreate(ArticleBase):
    """Schéma pour créer un article"""
    company_id: Optional[int] = None

class ArticleUpdate(BaseModel):
    """Schéma pour mettre à jour la quantité d'un article"""
    quantite: int
    
    @field_validator("quantite")
    @classmethod
    def quantite_positive(cls, v):
        if v < 0:
            raise ValueError('La quantité doit être positive ou nulle')
        return v

class ArticleResponse(ArticleBase):
    """Schéma pour la réponse article"""
    id: int
    company_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

# -----------------------------
# RETRAITS
# -----------------------------
class RetraitRequest(BaseModel):
    """Schéma pour demander un retrait"""
    nom_article: str
    quantite: int
    nom_chantier: str = ""  # 🆕 Nom du chantier (optionnel)
    duree_location: Optional[int] = None  # 🆕 Durée de location en jours (optionnel)
    
    @field_validator("quantite")
    @classmethod
    def quantite_positive(cls, v):
        if v <= 0:
            raise ValueError('La quantité doit être strictement positive')
        return v

class RetraitCreate(BaseModel):
    """Schéma pour créer un retrait"""
    article_id: int = Field(..., gt=0)
    quantite: int = Field(..., gt=0)

class RetraitRead(BaseModel):
    """Schéma complet d'un retrait"""
    id: int
    company_id: Optional[int]
    article_id: int
    quantite: int
    poids_total: float
    date: datetime
    user_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)

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
    poids_unitaire: float = 0 
    poids_total_ligne: float = 0 
    quantite_utilisee: int
    note: Optional[str] = None

class CalculRequest(BaseModel):
    """Schéma pour demander un calcul d'échafaudage"""
    hauteur: float
    longueur: float
    largeur: float
    company_id: Optional[int] = None
    apply_to_stock: bool = False
    niveaux_travail: str = "tous"  # "tous", "dernier", "liste:1,3,5"
    nom_chantier: str = ""  # 🆕 Nom du chantier (optionnel)
    duree_location: Optional[int] = None  # 🆕 Durée de location en jours (optionnel)
    
    @field_validator("hauteur", "longueur", "largeur")
    @classmethod
    def dimensions_positives(cls, v):
        if v <= 0:
            raise ValueError('Les dimensions doivent être strictement positives')
        return v

class CalculResponse(BaseModel):
    """Schéma pour la réponse du calcul"""
    pieces: List[PieceUsed]
    poids_total: float
    meta: Dict
    ajustements: List[str]

# -----------------------------
# 🆕 CHANTIERS
# -----------------------------
class ChantierBase(BaseModel):
    """Schéma de base pour un chantier"""
    nom_chantier: str
    duree_location: Optional[int] = None  # en jours
    hauteur: Optional[float] = None
    longueur: Optional[float] = None
    largeur: Optional[float] = None
    niveaux_travail: Optional[str] = None
    poids_total: Optional[float] = None

class ChantierCreate(ChantierBase):
    """Schéma pour créer un chantier"""
    company_id: Optional[int] = None

class ChantierResponse(ChantierBase):
    """Schéma pour la réponse chantier"""
    id: int
    company_id: int
    date_creation: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ChantierUpdate(BaseModel):
    """Schéma pour mettre à jour un chantier"""
    nom_chantier: Optional[str] = None
    duree_location: Optional[int] = None
    
    @field_validator("duree_location")
    @classmethod
    def duree_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('La durée doit être strictement positive')
        return v

# -----------------------------
# GESTION ADMIN/USER
# -----------------------------
class AdminCreate(BaseModel):
    """Schéma pour créer un admin (par SUPERADMIN)"""
    username: str
    email: str
    company_id: int
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Email invalide')
        return v

class UserCreateByAdmin(BaseModel):
    """Schéma pour créer un user (par ADMIN)"""
    username: str
    email: str
    company_id: int
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Email invalide')
        return v

class PasswordChange(BaseModel):
    """Schéma pour changer le mot de passe"""
    old_password: str
    new_password: str
    
    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Le mot de passe doit contenir au moins 8 caractères')
        return v