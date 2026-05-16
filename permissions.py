# permissions.py
# ================================================================
# Matrice des permissions par sous-rôle
# ================================================================
from models import SubRoleEnum

# Définition des permissions pour chaque sous-rôle
PERMISSIONS = {
    SubRoleEnum.COMMERCIAL: {
        "voir_stock":          True,
        "faire_retraits":      True,
        "calcul_echafaudage":  True,
        "historique_chantiers":True,
        "ajouter_articles":    False,
        "supprimer_articles":  False,
        "export_pdf_excel":    True,
        "gerer_utilisateurs":  False,
    },
    SubRoleEnum.MAGASINIER: {
        "voir_stock":          True,
        "faire_retraits":      True,
        "calcul_echafaudage":  False,
        "historique_chantiers":False,
        "ajouter_articles":    False,
        "supprimer_articles":  False,
        "export_pdf_excel":    True,
        "gerer_utilisateurs":  False,
    },
    SubRoleEnum.CHEF_CHANTIER: {
        "voir_stock":          True,
        "faire_retraits":      True,
        "calcul_echafaudage":  True,
        "historique_chantiers":True,
        "ajouter_articles":    False,
        "supprimer_articles":  False,
        "export_pdf_excel":    True,
        "gerer_utilisateurs":  False,
    },
    SubRoleEnum.GESTIONNAIRE_STOCK: {
        "voir_stock":          True,
        "faire_retraits":      True,
        "calcul_echafaudage":  False,
        "historique_chantiers":True,
        "ajouter_articles":    True,
        "supprimer_articles":  True,
        "export_pdf_excel":    True,
        "gerer_utilisateurs":  False,
    },
    SubRoleEnum.AUCUN: {
        # Accès standard (ancien comportement USER)
        "voir_stock":          True,
        "faire_retraits":      True,
        "calcul_echafaudage":  True,
        "historique_chantiers":True,
        "ajouter_articles":    False,
        "supprimer_articles":  False,
        "export_pdf_excel":    True,
        "gerer_utilisateurs":  False,
    },
}

def get_permissions(sub_role: SubRoleEnum) -> dict:
    """Retourne les permissions d'un sous-rôle"""
    return PERMISSIONS.get(sub_role, PERMISSIONS[SubRoleEnum.AUCUN])

def has_permission(sub_role: SubRoleEnum, permission: str) -> bool:
    """Vérifie si un sous-rôle a une permission spécifique"""
    perms = get_permissions(sub_role)
    return perms.get(permission, False)
