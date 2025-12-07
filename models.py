from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import Base
import enum
from datetime import datetime

class RoleEnum(str, enum.Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    users = relationship("User", back_populates="company")
    articles = relationship("Article", back_populates="company")
    retraits = relationship("Retrait", back_populates="company")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.USER)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    
    # 🆕 NOUVEAUX CHAMPS pour gestion première connexion
    first_login = Column(Boolean, default=True)  # True = doit changer son mot de passe
    password_reset_required = Column(Boolean, default=False)  # Pour reset forcé
    email = Column(String, nullable=True)  # Pour envoi mot de passe
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