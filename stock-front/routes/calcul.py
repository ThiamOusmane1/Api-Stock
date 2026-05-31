from fastapi import APIRouter
from calcul.service import calcul_echafaudage_service

router = APIRouter(prefix="/calcul", tags=["Calcul"])

@router.post("/echafaudage")
def calcul_echafaudage(data: dict):
    return calcul_echafaudage_service(
        hauteur=data["hauteur"],
        longueur=data["longueur"],
        largeur=data["largeur"]
    )
