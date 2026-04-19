from typing import List, Dict
from models import Article  # SQLAlchemy

def map_articles_to_db(calculated: List[Dict], db_articles: List[Article]) -> List[Dict]:
    result = []
    for item in calculated:
        db_match = next((a for a in db_articles if a.nom.lower() == item["nom"].lower()), None)
        if db_match:
            item["article_id"] = db_match.id
        result.append(item)
    return result
