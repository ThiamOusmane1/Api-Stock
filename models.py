# models.py
from sqlalchemy import Table, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy import Boolean
from database import metadata
from datetime import datetime

# Entreprises
entreprises = Table(
    "entreprises",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("nom", String, unique=True, nullable=False),
)

# Utilisateurs (role: superadmin | admin | user)
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("role", String, default="user", nullable=False),
    Column("entreprise_id", Integer, ForeignKey("entreprises.id"), nullable=True),
)

# Articles (tenant aware)
articles = Table(
    "articles",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("entreprise_id", Integer, ForeignKey("entreprises.id")),
    Column("nom", String, nullable=False),
    Column("description", String, nullable=True),
    Column("quantite", Integer, nullable=False, default=0),
    Column("longueur", Float, nullable=True),
    Column("largeur", Float, nullable=True),
    Column("hauteur", Float, nullable=True),
    Column("poids", Float, nullable=True),
)

# Retraits (historique)
retraits = Table(
    "retraits",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("entreprise_id", Integer, ForeignKey("entreprises.id")),
    Column("article_id", Integer, ForeignKey("articles.id")),
    Column("quantite", Integer, nullable=False),
    Column("poids_total", Float, nullable=False),
    Column("date", DateTime, default=datetime.utcnow),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=True),
)
