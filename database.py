# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
# Charger les variables d'environnement depuis .env
load_dotenv()

# Exemple pour PostgreSQL :
# DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/stockdb
# (Sinon, SQLite sera utilisé par défaut)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Création du moteur SQLAlchemy
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Fabrique de sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base commune pour tous les modèles ORM
Base = declarative_base()
