from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# -----------------------------
# AUTH / USERS
# -----------------------------
class UserCreate(BaseModel):
    username: str
    password: str
    role: str  # "superadmin", "admin", "user"
    entreprise_id: Optional[int] = None  # obligatoire pour admin ou user

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class User(BaseModel):
    id: int
    username: str
    role: str
    entreprise_id: Optional[int] = None

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    entreprise_id: Optional[int] = None

    class Config:
        orm_mode = True

# -----------------------------
# ENTREPRISES
# -----------------------------
class EntrepriseCreate(BaseModel):
    nom: str

class Entreprise(BaseModel):
    id: int
    nom: str

    class Config:
        orm_mode = True

class EntrepriseResponse(BaseModel):
    id: int
    nom: str

    class Config:
        orm_mode = True

# -----------------------------
# ARTICLES
# -----------------------------
class ArticleBase(BaseModel):
    nom: str
    description: Optional[str] = None
    quantite: int
    longueur: Optional[float] = None
    largeur: Optional[float] = None
    hauteur: Optional[float] = None
    poids: Optional[float] = None

class ArticleCreate(ArticleBase):
    entreprise_id: Optional[int] = None

class ArticleUpdate(BaseModel):
    quantite: int

class Article(ArticleBase):
    id: int
    entreprise_id: int

    class Config:
        orm_mode = True

class ArticleResponse(ArticleBase):
    id: int
    entreprise_id: int

    class Config:
        orm_mode = True

# -----------------------------
# RETRAITS
# -----------------------------
class RetraitRequest(BaseModel):
    quantite: int

class Retrait(BaseModel):
    id: int
    article_id: int
    quantite: int
    poids_total: float
    date: datetime
    user_id: int

    class Config:
        orm_mode = True

class RetraitResponse(BaseModel):
    message: str
    article_id: int
    nom_article: str
    quantite_retirée: int
    poids_total: float
    stock_restant: int

# -----------------------------
# CALCUL / ALLOCATION
# -----------------------------
class PieceUsed(BaseModel):
    article_id: Optional[int] = None
    nom: str
    longueur: Optional[float] = None
    largeur: Optional[float] = None
    hauteur: Optional[float] = None
    poids: Optional[float] = None
    quantite_utilisee: int
    note: Optional[str] = None

class CalculRequest(BaseModel):
    hauteur: float
    longueur: float
    largeur: float
    entreprise_id: Optional[int] = None
    apply_to_stock: bool = False

class CalculResponse(BaseModel):
    pieces: List[PieceUsed]
    poids_total: float
    meta: dict
    ajustements: List[str]
