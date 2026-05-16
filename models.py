from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import Base
import enum
from datetime import datetime

class RoleEnum(str, enum.Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"

# 🆕 NOUVEAU : Sous-rôles pour les utilisateurs d'une entreprise
class SubRoleEnum(str, enum.Enum):
    COMMERCIAL = "commercial"
    MAGASINIER = "magasinier"
    CHEF_CHANTIER = "chef_chantier"
    GESTIONNAIRE_STOCK = "gestionnaire_stock"
    AUCUN = "aucun"  # Rôle par défaut (accès standard)

class CompanyStatusEnum(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    status = Column(
        Enum(CompanyStatusEnum),
        default=CompanyStatusEnum.ACTIVE,
        nullable=False
    )
    suspended_at = Column(DateTime, nullable=True)
    terminated_at = Column(DateTime, nullable=True)

    users = relationship("User", back_populates="company")
    articles = relationship("Article", back_populates="company")
    retraits = relationship("Retrait", back_populates="company")
    chantiers = relationship("Chantier", back_populates="company")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.USER)

    # 🆕 Sous-rôle pour les utilisateurs d'une entreprise
    sub_role = Column(
        Enum(SubRoleEnum),
        default=SubRoleEnum.AUCUN,
        nullable=False,
        server_default="aucun"
    )

    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    first_login = Column(Boolean, default=True)
    password_reset_required = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="users")
    retraits = relationship("Retrait", back_populates="user")

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False, index=True)
    reference = Column(String, nullable=True, index=True)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True, index=True)
    quantite = Column(Integer, default=0)
    prix_unitaire = Column(Float, default=0.0)
    longueur = Column(Float, nullable=True)
    largeur = Column(Float, nullable=True)
    hauteur = Column(Float, nullable=True)
    poids = Column(Float, nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    company = relationship("Company", back_populates="articles")
    retraits = relationship("Retrait", back_populates="article")

class Retrait(Base):
    __tablename__ = "retraits"
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    nom_utilisateur = Column(String, nullable=True)
    quantite = Column(Integer, nullable=False)
    poids_total = Column(Float, default=0.0)
    date_retrait = Column(DateTime, default=datetime.utcnow)

    article = relationship("Article", back_populates="retraits")
    company = relationship("Company", back_populates="retraits")
    user = relationship("User", back_populates="retraits")

class Chantier(Base):
    __tablename__ = "chantiers"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    nom_chantier = Column(String, nullable=False)
    duree_location = Column(Integer)
    hauteur = Column(Float)
    longueur = Column(Float)
    largeur = Column(Float)
    niveaux_travail = Column(String)
    date_creation = Column(DateTime, default=datetime.utcnow)
    poids_total = Column(Float)

    company = relationship("Company", back_populates="chantiers")
