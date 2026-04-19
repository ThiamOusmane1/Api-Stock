from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

# Imports absolus depuis la racine
from database import get_db
from models import Article
from calcul.structure import calculer_echafaudage
from calcul.mapping import map_articles_to_db

router = APIRouter(prefix="/calcul", tags=["Calcul"])

@router.post("/", summary="Calculer les articles pour un échafaudage")
def calcul_endpoint(
    hauteur: float,
    longueur: float,
    largeur: float,
    db: Session = Depends(get_db)
) -> List[dict]:
    calculated = calculer_echafaudage(hauteur, longueur, largeur)
    db_articles = db.query(Article).all()
    mapped = map_articles_to_db(calculated, db_articles)
    return mapped
