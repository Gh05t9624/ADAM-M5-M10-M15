# app/engine/advanced_optimizations.py
# Optimisations avancées pour le trading algorithmique

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

class MultiTimeframeValidator:
    """Validation multi-timeframe pour éviter les faux signaux"""
    
    @staticmethod
    def confirm_m10_signal(df_m10: pd.DataFrame, direction: str) -> bool:
        """Confirmation M10 pour valider les signaux M5"""
        if len(df_m10) < 50:
            return False

        ema_20_m10 = df_m10["close"].ewm(span=20).mean().iloc[-1]
        ema_50_m10 = df_m10["close"].ewm(span=50).mean().iloc[-1]
        current_price_m10 = df_m10["close"].iloc[-1]

        if direction == "HAUSSIER":
            return (ema_20_m10 > ema_50_m10 and
                   current_price_m10 > ema_20_m10 and
                   df_m10["close"].iloc[-3] < ema_20_m10)  # Croissance confirmée
        else:
            return (ema_20_m10 < ema_50_m10 and
                   current_price_m10 < ema_20_m10 and
                   df_m10["close"].iloc[-3] > ema_20_m10)  # Baisse confirmée
    
    @staticmethod
    def confirm_d1_trend(df_d1: pd.DataFrame, direction: str) -> bool:
        """Confirmation Daily pour la tendance principale"""
        if len(df_d1) < 20:
            return False
            
        ema_20_d1 = df_d1["close"].ewm(span=20).mean().iloc[-1]
        current_price_d1 = df_d1["close"].iloc[-1]
        
        if direction == "HAUSSIER":
            return current_price_d1 > ema_20_d1
        else:
            return current_price_d1 < ema_20_d1

class VolumeValidator:
    """Validation basée sur le volume pour éviter les signaux sans force"""
    
    @staticmethod
    def validate_volume_signal(df: pd.DataFrame, symbol: str) -> bool:
        """Valide que le volume supporte le signal"""
        if "volume" not in df.columns or len(df) < 20:
            return True  # Pas de volume = pas de filtrage
            
        volume_avg = df["volume"].rolling(20).mean().iloc[-1]
        current_volume = df["volume"].iloc[-1]
        volume_spike = current_volume / volume_avg if volume_avg > 0 else 1
        
        # Volume doit être significativement supérieur à la moyenne
        min_volume_ratio = {
            "XAUUSD": 1.3,  # Gold moins volatile en volume
            "EURUSD": 1.5,  # Forex standard
            "GBPUSD": 1.6,  # GBP plus volatile
            "USDJPY": 1.4   # JPY modéré
        }.get(symbol, 1.5)
        
        return volume_spike >= min_volume_ratio
    
    @staticmethod
    def get_volume_strength(df: pd.DataFrame) -> float:
        """Retourne la force du volume (0-1)"""
        if "volume" not in df.columns or len(df) < 20:
            return 0.5
            
        volume_avg = df["volume"].rolling(20).mean().iloc[-1]
        current_volume = df["volume"].iloc[-1]
        
        return min(current_volume / (volume_avg * 2), 1.0)

class DynamicLevelCalculator:
    """Calcul dynamique des TP/SL selon conditions de marché"""
    
    @staticmethod
    def calculate_dynamic_levels(entry: float, direction: str, symbol: str, 
                           volatility: float, session: str) -> Dict:
        """Calcule TP/SL adaptés à la volatilité et session"""
        
        # Base RR selon symbole
        base_rr = {
            "XAUUSD": 1.8,
            "EURUSD": 1.5,
            "GBPUSD": 1.6,
            "USDJPY": 1.4,
            "AUDUSD": 1.5,
            "USDCAD": 1.4
        }.get(symbol, 1.5)
        
        # Ajuster selon volatilité
        if volatility > 0.8:  # Haute volatilité
            base_rr *= 1.3  # Plus de potentiel
        elif volatility < 0.3:  # Faible volatilité
            base_rr *= 0.8  # Plus conservateur
        
        # Ajuster selon session
        session_multiplier = {
            "OVERLAP": 1.2,   # Meilleur potentiel
            "ASIE": 0.9,      # Plus conservateur
            "LONDRES": 1.1,    # Bon potentiel
            "NEW YORK": 1.0     # Standard
        }.get(session, 1.0)
        
        base_rr *= session_multiplier
        
        # Calcul des distances en pips
        pip_value = 0.01 if "JPY" in symbol else 0.0001
        if "XAU" in symbol:
            pip_value = 0.1
            
        # Distance de base selon symbole
        base_distance = {
            "XAUUSD": 200,  # 200 pips pour Gold
            "EURUSD": 20,   # 20 pips pour EUR
            "GBPUSD": 25,   # 25 pips pour GBP
            "USDJPY": 20    # 20 pips pour JPY
        }.get(symbol, 20)
        
        # Ajuster selon volatilité
        if volatility > 0.6:
            base_distance *= 1.5
        elif volatility < 0.4:
            base_distance *= 0.8
            
        tp_distance = base_distance * base_rr
        sl_distance = base_distance
        
        if direction == "HAUSSIER":
            tp = entry + (tp_distance * pip_value)
            sl = entry - (sl_distance * pip_value)
        else:
            tp = entry - (tp_distance * pip_value)
            sl = entry + (sl_distance * pip_value)
        
        return {
            "tp": round(tp, 5),
            "sl": round(sl, 5),
            "rr": round(base_rr, 2),
            "tp_pips": round(tp_distance),
            "sl_pips": round(sl_distance)
        }

class MarketRegimeDetector:
    """Détection du régime de marché (trend/range/volatile)"""
    
    @staticmethod
    def detect_market_regime(df: pd.DataFrame) -> str:
        """Détecte si marché est en trend, range ou volatile"""
        if len(df) < 50:
            return "UNKNOWN"
            
        # Calcul ATR pour la volatilité
        high_low = df["high"] - df["low"]
        atr = high_low.rolling(14).mean().iloc[-1]
        
        # Variation de prix sur 20 périodes
        price_change = abs(df["close"].iloc[-1] - df["close"].iloc[-20])
        current_price = df["close"].iloc[-1]
        
        # Normalisation
        volatility_ratio = atr / current_price if current_price > 0 else 0
        
        if volatility_ratio > 0.015:  # > 1.5% de volatilité
            return "VOLATILE"
        elif price_change < current_price * 0.005:  # < 0.5% de variation
            return "RANGE"
        else:
            return "TREND"
    
    @staticmethod
    def get_regime_adjustment(regime: str) -> int:
        """Retourne l'ajustement de score selon le régime"""
        adjustments = {
            "VOLATILE": -8,   # Plus permissif en volatile
            "RANGE": 12,       # Plus sélectif en range
            "TREND": 0,        # Neutre en trend
            "UNKNOWN": 5        # Légèrement sélectif si inconnu
        }
        return adjustments.get(regime, 0)

class CorrelationFilter:
    """Filtrage des corrélations pour éviter les trades sur-pesés"""
    
    # Groupes de corrélation (base devise)
    CORRELATION_GROUPS = {
        "EUR": ["EURUSD", "EURGBP", "EURJPY", "EURCAD", "EURAUD", "EURCHF"],
        "GBP": ["GBPUSD", "EURGBP", "GBPJPY", "GBPCAD", "GBPAUD", "GBPCHF"],
        "USD": ["EURUSD", "GBPUSD", "AUDUSD", "USDCAD", "USDJPY", "USDCHF"],
        "JPY": ["USDJPY", "EURJPY", "GBPJPY", "AUDJPY", "CADJPY", "CHFJPY"],
        "AUD": ["AUDUSD", "EURAUD", "GBPAUD", "AUDJPY", "AUDCAD", "AUDCHF"],
        "CAD": ["USDCAD", "EURCAD", "GBPCAD", "AUDCAD", "CADJPY", "CADCHF"]
    }
    
    @staticmethod
    def check_correlation_conflict(symbol: str, active_trades: Dict) -> bool:
        """Vérifie s'il y a conflit de corrélation"""
        for base_currency, correlated_symbols in CorrelationFilter.CORRELATION_GROUPS.items():
            if symbol in correlated_symbols:
                for active_symbol in active_trades:
                    if active_symbol in correlated_symbols and active_symbol != symbol:
                        return True  # Conflit de corrélation détecté
        return False
    
    @staticmethod
    def get_correlation_group(symbol: str) -> str:
        """Retourne le groupe de corrélation d'un symbole"""
        for base_currency, symbols in CorrelationFilter.CORRELATION_GROUPS.items():
            if symbol in symbols:
                return base_currency
        return "UNKNOWN"

class TimeOptimizer:
    """Optimisation temporelle - heures optimales par session"""
    
    # Heures optimales par session (UTC)
    OPTIMAL_HOURS = {
        "ASIE": [(0, 3), (5, 8)],        # Tokyo active
        "LONDRES": [(8, 11), (14, 16)],    # London morning + afternoon  
        "OVERLAP": [(13, 16)],               # Meilleur overlap
        "NEW YORK": [(16, 19), (20, 21)],    # NY active
        "OFF": []                              # Hors session
    }
    
    @staticmethod
    def is_optimal_time(session: str) -> bool:
        """Vérifie si l'heure actuelle est optimale"""
        current_hour = datetime.utcnow().hour
        optimal_hours = TimeOptimizer.OPTIMAL_HOURS.get(session, [])
        
        for start, end in optimal_hours:
            if start <= current_hour <= end:
                return True
        return False
    
    @staticmethod
    def get_time_adjustment(session: str) -> int:
        """Retourne l'ajustement de score selon l'heure"""
        if TimeOptimizer.is_optimal_time(session):
            return -5  # Plus permissif en heures optimales
        else:
            return 8   # Plus sélectif hors heures optimales

class AdvancedPerformanceTracker:
    """Tracking avancé des performances avec ML simple"""
    
    def __init__(self):
        self.daily_stats = {}
        self.symbol_performance = {}
        self.session_performance = {}
        self.features_history = []
        self.results_history = []
    
    def add_trade_result(self, symbol: str, session: str, features: Dict, 
                       pnl: float, was_profitable: bool):
        """Ajoute un résultat de trade pour l'apprentissage"""
        date = datetime.utcnow().date()
        
        # Stats quotidiennes
        if date not in self.daily_stats:
            self.daily_stats[date] = {"trades": 0, "wins": 0, "pnl": 0, "session": session}
        
        self.daily_stats[date]["trades"] += 1
        if was_profitable:
            self.daily_stats[date]["wins"] += 1
        self.daily_stats[date]["pnl"] += pnl
        
        # Performance par symbole
        if symbol not in self.symbol_performance:
            self.symbol_performance[symbol] = {"trades": 0, "wins": 0, "pnl": 0, "features": []}
        
        self.symbol_performance[symbol]["trades"] += 1
        if was_profitable:
            self.symbol_performance[symbol]["wins"] += 1
        self.symbol_performance[symbol]["pnl"] += pnl
        self.symbol_performance[symbol]["features"].append(features)
        
        # Performance par session
        if session not in self.session_performance:
            self.session_performance[session] = {"trades": 0, "wins": 0, "pnl": 0}
        
        self.session_performance[session]["trades"] += 1
        if was_profitable:
            self.session_performance[session]["wins"] += 1
        self.session_performance[session]["pnl"] += pnl
        
        # ML simple - stocker features et résultats
        self.features_history.append(features)
        self.results_history.append(was_profitable)
        
        # Garder seulement les 1000 derniers trades
        if len(self.features_history) > 1000:
            self.features_history = self.features_history[-1000:]
            self.results_history = self.results_history[-1000:]
    
    def predict_success_probability(self, current_features: Dict) -> float:
        """Prédit la probabilité de succès basée sur l'historique"""
        if len(self.results_history) < 50:
            return 0.5  # Par défaut si pas assez de données
        
        similar_trades = []
        for i, features in enumerate(self.features_history[-100:]):
            similarity = self._calculate_similarity(features, current_features)
            if similarity > 0.8:
                similar_trades.append(self.results_history[i])
        
        if not similar_trades:
            return 0.5
        
        return sum(similar_trades) / len(similar_trades)
    
    def _calculate_similarity(self, features1: Dict, features2: Dict) -> float:
        """Calcule la similarité entre deux sets de features"""
        similarity_score = 0
        total_features = 0
        
        # Features importantes pour la similarité
        important_features = ["score", "direction", "session", "volatility", "regime"]
        
        for feature in important_features:
            if feature in features1 and feature in features2:
                if feature == "direction":
                    similarity_score += (features1[feature] == features2[feature])
                elif isinstance(features1[feature], (int, float)):
                    diff = abs(features1[feature] - features2[feature])
                    similarity_score += max(0, 1 - diff / max(abs(features1[feature]), 1))
                total_features += 1
        
        return similarity_score / total_features if total_features > 0 else 0
    
    def get_best_symbols(self, limit: int = 5) -> List[str]:
        """Retourne les meilleurs symboles par winrate et profit"""
        symbol_stats = []
        for symbol, stats in self.symbol_performance.items():
            if stats["trades"] >= 5:  # Minimum 5 trades
                winrate = stats["wins"] / stats["trades"]
                avg_profit = stats["pnl"] / stats["trades"]
                score = (winrate * 0.6) + (min(avg_profit, 1) * 0.4)  # Score pondéré
                symbol_stats.append((symbol, score, winrate, stats["pnl"]))
        
        # Trier par score composite
        symbol_stats.sort(key=lambda x: x[1], reverse=True)
        return [symbol for symbol, _, _, _ in symbol_stats[:limit]]
    
    def get_session_adjustments(self) -> Dict[str, int]:
        """Retourne les ajustements de score par session"""
        adjustments = {}
        for session, stats in self.session_performance.items():
            if stats["trades"] >= 10:
                winrate = stats["wins"] / stats["trades"]
                if winrate > 0.65:
                    adjustments[session] = -5  # Plus permissif
                elif winrate < 0.45:
                    adjustments[session] = 8   # Plus sélectif
                else:
                    adjustments[session] = 0   # Neutre
            else:
                adjustments[session] = 0
        
        return adjustments
    
    def get_current_winrate(self, days: int = 30) -> float:
        """Calcule le winrate des N derniers jours"""
        cutoff_date = datetime.utcnow().date() - timedelta(days=days)
        recent_trades = 0
        recent_wins = 0
        
        for date, stats in self.daily_stats.items():
            if date >= cutoff_date:
                recent_trades += stats["trades"]
                recent_wins += stats["wins"]
        
        return recent_wins / recent_trades if recent_trades > 0 else 0.5

class PositionSizer:
    """Calculateur de taille de position adaptatif"""
    
    @staticmethod
    def calculate_adaptive_position_size(account_balance: float, base_risk: float, 
                                   winrate: float, volatility: float, 
                                   symbol: str) -> float:
        """Calcule la taille de position adaptée à plusieurs facteurs"""
        
        # Ajuster le risque selon winrate
        if winrate > 0.65:
            risk_multiplier = 1.3  # Augmenter si excellent winrate
        elif winrate > 0.55:
            risk_multiplier = 1.1  # Légère augmentation
        elif winrate < 0.45:
            risk_multiplier = 0.7  # Réduire si mauvais winrate
        else:
            risk_multiplier = 1.0  # Normal
        
        # Ajuster selon volatilité du symbole
        volatility_adjustment = {
            "XAUUSD": 0.6,  # Gold très volatile
            "GBPUSD": 0.8,  # GBP volatile
            "EURUSD": 1.0,  # EUR standard
            "USDJPY": 0.9   # JPY modéré
        }.get(symbol, 1.0)
        
        # Ajuster selon volatilité actuelle
        if volatility > 0.8:
            volatility_multiplier = 0.7  # Réduire en haute vol
        elif volatility < 0.3:
            volatility_multiplier = 0.9  # Légère réduction en basse vol
        else:
            volatility_multiplier = 1.0
        
        # Calcul final
        adjusted_risk = base_risk * risk_multiplier * volatility_adjustment * volatility_multiplier
        adjusted_risk = min(adjusted_risk, 0.05)  # Maximum 5% par trade
        
        return (account_balance * adjusted_risk) / 100
