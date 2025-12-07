# crud_filters.py
"""
Fonctions de recherche et filtrage avancés pour les articles
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from models import Article, Retrait
from typing import Optional, List
from datetime import datetime, timedelta

def search_articles(
    db: Session,
    search: Optional[str] = None,
    categorie: Optional[str] = None,
    min_stock: Optional[int] = None,
    max_stock: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Article]:
    """Recherche avancée d'articles avec filtres multiples"""
    query = db.query(Article)
    
    if search:
        query = query.filter(
            or_(
                Article.nom.ilike(f"%{search}%"),
                Article.reference.ilike(f"%{search}%") if hasattr(Article, 'reference') else False,
                Article.category.ilike(f"%{search}%")
            )
        )
    
    if categorie:
        query = query.filter(Article.category.ilike(f"%{categorie}%"))
    
    if min_stock is not None:
        query = query.filter(Article.quantite >= min_stock)
    
    if max_stock is not None:
        query = query.filter(Article.quantite <= max_stock)
    
    return query.offset(skip).limit(limit).all()

def get_low_stock_articles(db: Session, threshold: int = 10) -> List[Article]:
    """Récupère les articles avec stock faible"""
    return db.query(Article).filter(Article.quantite <= threshold).all()

def get_stats_by_category(db: Session):
    """Statistiques par catégorie"""
    return db.query(
        Article.category.label('categorie'),  # Alias pour compatibilité
        func.count(Article.id).label('nombre_articles'),
        func.sum(Article.quantite).label('stock_total')
    ).group_by(Article.category).all()

def get_recent_retraits(db: Session, days: int = 7, limit: int = 50):
    """Récupère les retraits récents"""
    date_limite = datetime.now() - timedelta(days=days)
    
    # Utiliser le bon nom de colonne (date_retrait ou date)
    date_column = Retrait.date_retrait if hasattr(Retrait, 'date_retrait') else Retrait.date
    
    return db.query(Retrait).filter(
        date_column >= date_limite
    ).order_by(date_column.desc()).limit(limit).all()