# app/api/routes/markets.py
"""Routes pour les marchés - Structure préparée pour future implémentation"""

from fastapi import APIRouter, HTTPException
from typing import List

# Ces routes seront implémentées dans le futur
# Pour l'instant, la structure est préparée mais les endpoints ne sont pas actifs

router = APIRouter(prefix="/api/markets", tags=["markets"])


@router.get("", summary="Liste des marchés disponibles")
async def get_markets():
    """
    Retourne la liste des marchés disponibles.
    
    À implémenter dans le futur avec la couche de services.
    """
    # TODO: Implémenter avec MarketAnalysisService.get_available_markets()
    pass


@router.get("/{symbol}", summary="Analyse d'un marché")
async def analyze_market(symbol: str, timeframe: str = "M10"):
    """
    Analyse un marché spécifique.
    
    À implémenter dans le futur avec la couche de services.
    """
    # TODO: Implémenter avec MarketAnalysisService.analyze_market()
    pass


@router.post("/{symbol}/trade-plan", summary="Générer un plan de trade")
async def generate_trade_plan(symbol: str):
    """
    Génère un plan de trade pour un marché.
    
    À implémenter dans le futur avec la couche de services.
    """
    # TODO: Implémenter avec MarketAnalysisService.generate_trade_plan()
    pass
