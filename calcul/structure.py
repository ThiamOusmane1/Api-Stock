# app-stock-api/calcul/structure.py
from typing import List, Dict

def calculer_echafaudage(hauteur: float, longueur: float, largeur: float) -> List[Dict]:
    """
    Calcule les articles nécessaires pour un échafaudage donné.
    Arguments:
        hauteur: hauteur totale en m
        longueur: longueur totale en m
        largeur: largeur totale en m
    Retour:
        Liste de dict {nom, quantite, longueur, largeur, hauteur, poids}
    """
    # Exemple simplifié : on va calculer le nombre de poteaux et planchers
    articles = []

    # 🟢 Poteaux : 1 poteau tous les 2 m de hauteur et à chaque coin
    poteau_par_metre = 2  # 2 poteaux par mètre de hauteur
    coins = 4
    nb_poteaux = int(hauteur * poteau_par_metre * coins)
    articles.append({
        "nom": "Poteau standard",
        "quantite": nb_poteaux,
        "longueur": None,
        "largeur": None,
        "hauteur": hauteur,
        "poids": nb_poteaux * 12  # poids moyen d’un poteau
    })

    # 🟢 Planchers : 1 plancher tous les 2m de hauteur
    plancher_par_niveau = int(longueur / 2 * largeur / 0.6)  # 0.6m largeur plancher standard
    niveaux = int(hauteur / 2) + 1
    nb_planchers = plancher_par_niveau * niveaux
    articles.append({
        "nom": "Plancher standard",
        "quantite": nb_planchers,
        "longueur": 2,
        "largeur": 0.6,
        "hauteur": None,
        "poids": nb_planchers * 20
    })

    # 🟢 Garde-corps : un par niveau et par longueur
    articles.append({
        "nom": "Garde-corps latéral",
        "quantite": niveaux * 2,
        "longueur": longueur,
        "largeur": None,
        "hauteur": None,
        "poids": niveaux * 5
    })

    return articles
