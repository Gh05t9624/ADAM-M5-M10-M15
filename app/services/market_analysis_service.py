# app/services/market_analysis_service.py
"""Service d'analyse de marché - Couche d'abstraction pour l'API"""

from typing import Optional, Dict, Any
import pandas as pd

from app.engine.analyzer import MarketAnalyzer
from app.engine.trade_setup import generate_trade_plan_multi
from app.engine.priority import compute_priority
from app.data.mt5_provider import MT5Provider


class MarketAnalysisService:
    """
    Service encapsulant la logique d'analyse de marché.
    Permet une séparation entre la logique métier et l'interface.
    """
    
    def __init__(self):
        self.analyzer = MarketAnalyzer()
        self.mt5_provider = MT5Provider()
    
    def analyze_market(
        self,
        symbol: str,
        timeframe: str = "M10",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyse un marché et retourne les résultats.

        Args:
            symbol: Symbole du marché (ex: "EURUSD")
            timeframe: Timeframe d'analyse (M30, M5, M10)
            context: Contexte de marché optionnel

        Returns:
            Dictionnaire contenant les résultats d'analyse
        """
        # Récupérer les données MT5
        df = self.mt5_provider.get_candles(symbol, timeframe)
        
        if df is None or df.empty:
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "error": "Unable to fetch market data"
            }
        
        # Analyser avec le moteur ADAM (logique inchangée)
        result = self.analyzer.analyze(
            df,
            context=context,
            symbol=symbol,
            timeframe=timeframe
        )
        
        # Ajouter des métadonnées
        result["symbol"] = symbol
        result["timeframe"] = timeframe
        
        return result
    
    def generate_trade_plan(
        self,
        analysis: Dict[str, Any],
        min_score: int = 55
    ) -> Optional[Dict[str, Any]]:
        """
        Génère un plan de trade basé sur l'analyse.
        
        Args:
            analysis: Résultat d'analyse du marché
            min_score: Score minimum pour générer un plan
        
        Returns:
            Dictionnaire contenant le plan de trade ou None
        """
        # Préparer les données pour le générateur (logique inchangée)
        trade_analysis = {
            "df": analysis.get("df"),
            "direction": analysis.get("direction"),
            "symbol": analysis.get("symbol"),
            "zone": analysis.get("zone", {"low": None, "high": None}),
            "score": analysis.get("score", 0),
            "trend_continuation": analysis.get("trend_continuation", False),
            "pullback_active": analysis.get("pullback_active", False),
            "has_impulse": analysis.get("has_impulse", False)
        }
        
        # Générer le plan avec le moteur ADAM (logique inchangée)
        trade_plan = generate_trade_plan_multi(trade_analysis, min_score=min_score)
        
        return trade_plan
    
    def get_market_priority(
        self,
        symbol: str,
        analysis: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Calcule la priorité d'un marché.
        
        Args:
            symbol: Symbole du marché
            analysis: Résultat d'analyse optionnel
        
        Returns:
            Niveau de priorité (CRITICAL, HIGH, MEDIUM, LOW, WATCH)
        """
        return compute_priority(symbol, analysis)
    
    def get_available_markets(self) -> list:
        """
        Retourne la liste des marchés disponibles.
        
        Returns:
            Liste des symboles disponibles
        """
        return self.mt5_provider.get_visible_symbols()
