"""
Analyseur optimisé pour les favoris et marchés ciblés
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np

from app.config.favorites import favorites_manager, PriorityLevel, MarketFavorite
from app.engine.analyzer import MarketAnalyzer
from app.data.mt5_provider import MT5Provider

class FavoritesAnalyzer:
    """Analyseur spécialisé pour les marchés favoris"""
    
    def __init__(self):
        self.analyzer = MarketAnalyzer()
        self.data_provider = MT5Provider()
        self.current_session = self._get_current_session()
        self.analysis_cache = {}
        self.last_cache_update = {}
    
    def _get_current_session(self) -> str:
        """Déterminer la session de trading actuelle"""
        hour = datetime.utcnow().hour
        
        if 22 <= hour or hour < 8:
            return "Tokyo"
        elif 8 <= hour < 13:
            return "London"
        elif 13 <= hour < 17:
            return "Overlap"
        elif 17 <= hour < 22:
            return "New York"
        else:
            return "Off"
    
    def get_priority_symbols_to_analyze(self, max_symbols: int = 10) -> List[str]:
        """Récupérer les symboles prioritaires à analyser maintenant"""
        # Obtenir les favoris optimisés pour la session actuelle
        session_favorites = favorites_manager.get_session_favorites(self.current_session)
        
        # Limiter au nombre maximum de symboles
        priority_symbols = []
        
        # Toujours inclure les critiques
        critical_symbols = favorites_manager.get_critical_symbols()
        priority_symbols.extend(critical_symbols)
        
        # Ajouter les hauts prioritaires de la session
        for favorite in session_favorites:
            if favorite.priority == PriorityLevel.HIGH and favorite.symbol not in priority_symbols:
                priority_symbols.append(favorite.symbol)
        
        # Ajouter les moyens prioritaires si on a encore de la place
        for favorite in session_favorites:
            if (favorite.priority == PriorityLevel.MEDIUM and 
                favorite.symbol not in priority_symbols and 
                len(priority_symbols) < max_symbols):
                priority_symbols.append(favorite.symbol)
        
        return priority_symbols[:max_symbols]
    
    def analyze_favorite_symbol(self, symbol: str, timeframe: str = "M5") -> Optional[Dict]:
        """Analyser un symbole favori avec ses paramètres personnalisés"""
        try:
            # Vérifier le cache
            cache_key = f"{symbol}_{timeframe}_{self.current_session}"
            now = datetime.now()
            
            if (cache_key in self.analysis_cache and 
                cache_key in self.last_cache_update and
                (now - self.last_cache_update[cache_key]).seconds < 30):  # Cache 30 secondes
                return self.analysis_cache[cache_key]
            
            # Récupérer les paramètres personnalisés
            favorite = favorites_manager.get_favorite(symbol)
            if not favorite or not favorite.active:
                return None
            
            # Obtenir les données
            df = self.data_provider.get_candles(symbol, timeframe, 200)
            if df is None or len(df) < 50:
                return None
            
            # Appliquer les filtres personnalisés
            if not self._apply_custom_filters(df, favorite):
                return None
            
            # Analyse avec le score minimum personnalisé
            analysis = self.analyzer.analyze(df, symbol=symbol)
            
            if analysis and analysis.get("score", 0) >= favorite.min_score:
                # Enrichir l'analyse avec les infos du favori
                analysis["favorite_info"] = {
                    "priority": favorite.priority.value,
                    "min_score": favorite.min_score,
                    "description": favorite.description,
                    "custom_settings": favorite.custom_settings
                }
                
                # Mettre en cache
                self.analysis_cache[cache_key] = analysis
                self.last_cache_update[cache_key] = now
                
                return analysis
            
            return None
            
        except Exception as e:
            print(f"Erreur analyse favori {symbol}: {e}")
            return None
    
    def _apply_custom_filters(self, df: pd.DataFrame, favorite: MarketFavorite) -> bool:
        """Appliquer les filtres personnalisés du favori"""
        try:
            custom_settings = favorite.custom_settings
            
            # Filtrer par spread si spécifié
            if "spread_limit" in custom_settings:
                # Simuler un check de spread (à adapter avec MT5 réel)
                current_spread = df["close"].iloc[-1] - df["open"].iloc[-1]
                spread_pips = abs(current_spread * 10000)  # Approximation
                
                if spread_pips > custom_settings["spread_limit"]:
                    return False
            
            # Filtrer par volume si spécifié
            if "volume_threshold" in custom_settings:
                avg_volume = df["volume"].rolling(20).mean().iloc[-1]
                current_volume = df["volume"].iloc[-1]
                
                if current_volume < avg_volume * custom_settings["volume_threshold"]:
                    return False
            
            # Filtrer par volatilité si spécifié
            if "volatility_filter" in custom_settings and custom_settings["volatility_filter"]:
                # Calculer l'ATR
                high_low = df["high"] - df["low"]
                high_close = abs(df["high"] - df["close"].shift())
                low_close = abs(df["low"] - df["close"].shift())
                atr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1).rolling(14).mean()
                
                current_atr = atr.iloc[-1]
                avg_atr = atr.iloc[-20:].mean()
                
                # Éviter les marchés trop calmes ou trop agités
                if current_atr < avg_atr * 0.5 or current_atr > avg_atr * 2.0:
                    return False
            
            return True
            
        except Exception as e:
            print(f"Erreur filtres personnalisés: {e}")
            return True  # En cas d'erreur, ne pas filtrer
    
    def get_all_favorites_analysis(self, max_symbols: int = 10) -> List[Dict]:
        """Analyser tous les favoris prioritaires"""
        priority_symbols = self.get_priority_symbols_to_analyze(max_symbols)
        results = []
        
        for symbol in priority_symbols:
            analysis = self.analyze_favorite_symbol(symbol)
            if analysis:
                results.append(analysis)
        
        # Trier par score décroissant
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results
    
    def get_best_opportunity(self) -> Optional[Dict]:
        """Trouver la meilleure opportunité parmi les favoris"""
        analyses = self.get_all_favorites_analysis()
        
        if not analyses:
            return None
        
        # Prendre la meilleure analyse
        best = analyses[0]
        
        # Ajouter le plan de trade
        from app.engine.trade_setup import generate_trade_plan_multi
        try:
            trade_plan = generate_trade_plan_multi(best, min_score=55)
            best["trade_plan"] = trade_plan
        except:
            best["trade_plan"] = None
        
        return best
    
    def should_alert_on_symbol(self, symbol: str, analysis: Dict) -> bool:
        """Déterminer si une alerte doit être envoyée pour ce symbole"""
        favorite = favorites_manager.get_favorite(symbol)
        if not favorite:
            return False
        
        score = analysis.get("score", 0)
        min_score = favorite.min_score
        
        # Alertes pour scores élevés
        if score >= min_score + 10:
            return True
        
        # Alertes pour changements de direction sur les critiques
        if (favorite.priority == PriorityLevel.CRITICAL and 
            score >= min_score and 
            analysis.get("direction") in ["HAUSSIER", "BAISSIER"]):
            return True
        
        return False
    
    def get_session_summary(self) -> Dict:
        """Résumé de la session actuelle pour les favoris"""
        session_favorites = favorites_manager.get_session_favorites(self.current_session)
        
        summary = {
            "session": self.current_session,
            "total_favorites": len(session_favorites),
            "active_favorites": len([f for f in session_favorites if f.active]),
            "priority_breakdown": {
                "critical": len([f for f in session_favorites if f.priority == PriorityLevel.CRITICAL]),
                "high": len([f for f in session_favorites if f.priority == PriorityLevel.HIGH]),
                "medium": len([f for f in session_favorites if f.priority == PriorityLevel.MEDIUM]),
                "low": len([f for f in session_favorites if f.priority == PriorityLevel.LOW])
            },
            "recommended_symbols": self.get_priority_symbols_to_analyze()
        }
        
        return summary
    
    def update_session(self):
        """Mettre à jour la session actuelle et nettoyer le cache"""
        new_session = self._get_current_session()
        if new_session != self.current_session:
            self.current_session = new_session
            self.analysis_cache.clear()
            self.last_cache_update.clear()
            print(f"Nouvelle session: {self.current_session}")
    
    def get_favorite_performance_stats(self, symbol: str) -> Dict:
        """Statistiques de performance pour un favori"""
        favorite = favorites_manager.get_favorite(symbol)
        if not favorite:
            return {}
        
        # Calculer les stats basées sur l'historique (à implémenter avec le journal)
        stats = {
            "symbol": symbol,
            "priority": favorite.priority.value,
            "min_score": favorite.min_score,
            "session_optimal": favorite.session_focus,
            "current_session_optimal": self.current_session in favorite.session_focus,
            "custom_settings": favorite.custom_settings
        }
        
        return stats
