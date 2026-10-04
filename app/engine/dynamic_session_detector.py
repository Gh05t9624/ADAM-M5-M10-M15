# app/engine/dynamic_session_detector.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DynamicSessionDetector:
    """
    Détecte dynamiquement les sessions de trading actives
    basées sur le volume, le mouvement et la volatilité
    """
    
    def __init__(self):
        self.volume_history = {}
        self.movement_history = {}
        self.last_analysis = {}
    
    def analyze_market_activity(self, df, symbol, lookback_periods=20):
        """
        Analyse l'activité du marché pour déterminer si la session est active
        
        Args:
            df: DataFrame OHLCV
            symbol: Symbole à analyser
            lookback_periods: Nombre de périodes pour l'analyse
        
        Returns:
            dict: Analyse complète d'activité
        """
        if df is None or len(df) < lookback_periods:
            return self._get_default_activity(symbol)
        
        # Extraire les données récentes
        recent_df = df.tail(lookback_periods)
        
        # 1. Analyse du volume
        volume_analysis = self._analyze_volume(recent_df, symbol)
        
        # 2. Analyse du mouvement/prix
        movement_analysis = self._analyze_price_movement(recent_df, symbol)
        
        # 3. Analyse de la volatilité
        volatility_analysis = self._analyze_volatility(recent_df, symbol)
        
        # 4. Analyse du spread (si disponible)
        spread_analysis = self._analyze_spread(recent_df, symbol)
        
        # 5. Score composite d'activité
        activity_score = self._calculate_activity_score(
            volume_analysis, movement_analysis, 
            volatility_analysis, spread_analysis
        )
        
        # 6. Déterminer si le marché est actif
        is_active = self._is_market_active(activity_score, symbol)
        
        # 7. Identifier la session probable
        probable_session = self._identify_session(recent_df, is_active)
        
        result = {
            'symbol': symbol,
            'is_active': is_active,
            'activity_score': activity_score,
            'volume_analysis': volume_analysis,
            'movement_analysis': movement_analysis,
            'volatility_analysis': volatility_analysis,
            'spread_analysis': spread_analysis,
            'probable_session': probable_session,
            'analysis_time': datetime.utcnow(),
            'recommendation': self._get_recommendation(activity_score, symbol)
        }
        
        # Mettre en cache
        self.last_analysis[symbol] = result
        
        return result
    
    def _analyze_volume(self, df, symbol):
        """Analyse le volume de trading"""
        if 'volume' not in df.columns:
            return {'score': 0.5, 'status': 'No volume data'}
        
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].mean()
        max_volume = df['volume'].max()
        
        # Ratios de volume
        current_vs_avg = current_volume / avg_volume if avg_volume > 0 else 1.0
        current_vs_max = current_volume / max_volume if max_volume > 0 else 1.0
        
        # Tendance du volume (dernières 5 périodes)
        recent_trend = df['volume'].tail(5).pct_change().mean()
        
        # Score de volume (0-1)
        volume_score = min(1.0, current_vs_avg * 0.6 + current_vs_max * 0.4)
        
        # Classification
        if volume_score >= 0.7:
            status = "High Volume"
        elif volume_score >= 0.4:
            status = "Normal Volume"
        else:
            status = "Low Volume"
        
        return {
            'current': current_volume,
            'average': avg_volume,
            'maximum': max_volume,
            'current_vs_avg': current_vs_avg,
            'current_vs_max': current_vs_max,
            'trend': recent_trend,
            'score': volume_score,
            'status': status
        }
    
    def _analyze_price_movement(self, df, symbol):
        """Analyse le mouvement des prix"""
        # Mouvement absolu par période
        df['movement'] = abs(df['close'] - df['open'])
        df['range'] = df['high'] - df['low']
        
        # Statistiques récentes
        current_movement = df['movement'].iloc[-1]
        avg_movement = df['movement'].mean()
        current_range = df['range'].iloc[-1]
        avg_range = df['range'].mean()
        
        # Tendance des mouvements
        movement_trend = df['movement'].tail(5).pct_change().mean()
        
        # Score de mouvement (0-1)
        movement_score = min(1.0, (current_movement / avg_movement) if avg_movement > 0 else 0.5)
        
        # Classification
        if movement_score >= 0.6:
            status = "High Movement"
        elif movement_score >= 0.3:
            status = "Normal Movement"
        else:
            status = "Low Movement"
        
        return {
            'current_movement': current_movement,
            'average_movement': avg_movement,
            'current_range': current_range,
            'average_range': avg_range,
            'trend': movement_trend,
            'score': movement_score,
            'status': status
        }
    
    def _analyze_volatility(self, df, symbol):
        """Analyse la volatilité du marché"""
        # ATR (Average True Range)
        df['tr1'] = df['high'] - df['low']
        df['tr2'] = abs(df['high'] - df['close'].shift())
        df['tr3'] = abs(df['low'] - df['close'].shift())
        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
        
        atr = df['tr'].rolling(window=14).mean()
        current_atr = atr.iloc[-1]
        avg_atr = atr.mean()
        
        # Écart-type des rendements
        returns = df['close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)  # Annualisé
        
        # Score de volatilité (0-1)
        volatility_score = min(1.0, (current_atr / avg_atr) if avg_atr > 0 else 0.5)
        
        # Classification
        if volatility_score >= 0.7:
            status = "High Volatility"
        elif volatility_score >= 0.4:
            status = "Normal Volatility"
        else:
            status = "Low Volatility"
        
        return {
            'current_atr': current_atr,
            'average_atr': avg_atr,
            'volatility': volatility,
            'score': volatility_score,
            'status': status
        }
    
    def _analyze_spread(self, df, symbol):
        """Analyse le spread (si données disponibles)"""
        # Pour MT5, le spread n'est généralement pas dans OHLCV
        # On peut l'estimer par la différence high-low sur petites périodes
        if len(df) < 5:
            return {'score': 0.5, 'status': 'Insufficient data'}
        
        # Spread moyen récent (estimation)
        recent_spreads = (df['high'] - df['low']).tail(5)
        current_spread = recent_spreads.iloc[-1]
        avg_spread = recent_spreads.mean()
        
        # Score de spread (plus bas = meilleur)
        spread_score = max(0.1, min(1.0, avg_spread / current_spread))
        
        return {
            'current_spread': current_spread,
            'average_spread': avg_spread,
            'score': spread_score,
            'status': 'Estimated'
        }
    
    def _calculate_activity_score(self, volume_analysis, movement_analysis, 
                              volatility_analysis, spread_analysis):
        """Calcule un score composite d'activité de marché"""
        
        # Pondérations selon la fiabilité de chaque indicateur
        weights = {
            'volume': 0.35,      # Le volume est très fiable
            'movement': 0.30,    # Le mouvement est fiable
            'volatility': 0.25,   # La volatilité est modérément fiable
            'spread': 0.10         # Le spread est moins fiable (estimé)
        }
        
        # Score pondéré
        activity_score = (
            volume_analysis['score'] * weights['volume'] +
            movement_analysis['score'] * weights['movement'] +
            volatility_analysis['score'] * weights['volatility'] +
            spread_analysis['score'] * weights['spread']
        )
        
        return round(activity_score, 3)
    
    def _is_market_active(self, activity_score, symbol):
        """Détermine si le marché est actif selon le score et le symbole"""
        
        # Seuils différents selon le type d'actif
        thresholds = {
            'BTC': 0.15,     # Bitcoin : toujours un peu d'activité
            'ETH': 0.15,     # Ethereum : similaire à BTC
            'XAU': 0.25,     # Or : besoin d'activité modérée
            'default': 0.30    # Forex : besoin d'activité claire
        }
        
        # Trouver le bon seuil
        for key, threshold in thresholds.items():
            if key in symbol.upper():
                return activity_score >= threshold
        
        return activity_score >= thresholds['default']
    
    def _identify_session(self, df, is_active):
        """Identifie la session de trading probable"""
        if not is_active:
            return "CLOSED"
        
        # Heure UTC actuelle
        current_hour = datetime.utcnow().hour
        
        # Sessions traditionnelles (pour référence)
        if 22 <= current_hour or current_hour < 2:
            return "ASIA_LATE"
        elif 2 <= current_hour < 6:
            return "ASIA_EARLY"
        elif 6 <= current_hour < 9:
            return "ASIA_PEAK"
        elif 9 <= current_hour < 13:
            return "LONDON_OPEN"
        elif 13 <= current_hour < 17:
            return "LONDON_PEAK"
        elif 17 <= current_hour < 20:
            return "NYC_OPEN"
        else:  # 20-22
            return "NYC_CLOSE"
    
    def _get_recommendation(self, activity_score, symbol):
        """Génère une recommandation basée sur l'activité"""
        if activity_score >= 0.7:
            return "High activity - Good for trading"
        elif activity_score >= 0.4:
            return "Moderate activity - Caution advised"
        else:
            return "Low activity - Consider waiting"
    
    def _get_default_activity(self, symbol):
        """Retourne une activité par défaut si pas de données"""
        return {
            'symbol': symbol,
            'is_active': True,  # Optimiste par défaut
            'activity_score': 0.5,
            'volume_analysis': {'score': 0.5, 'status': 'Default'},
            'movement_analysis': {'score': 0.5, 'status': 'Default'},
            'volatility_analysis': {'score': 0.5, 'status': 'Default'},
            'spread_analysis': {'score': 0.5, 'status': 'Default'},
            'probable_session': 'UNKNOWN',
            'analysis_time': datetime.utcnow(),
            'recommendation': 'Default - Need more data'
        }
    
    def get_session_summary(self, symbol):
        """Retourne un résumé de la session actuelle"""
        if symbol in self.last_analysis:
            analysis = self.last_analysis[symbol]
            return f"""
📊 Session Analysis for {symbol}
├─ Status: {'🟢 ACTIVE' if analysis['is_active'] else '🔴 FAIBLE ACTIVITÉ'}
├─ Activity Score: {analysis['activity_score']:.2f}/1.00
├─ Volume: {analysis['volume_analysis']['status']} ({analysis['volume_analysis']['score']:.2f})
├─ Movement: {analysis['movement_analysis']['status']} ({analysis['movement_analysis']['score']:.2f})
├─ Volatility: {analysis['volatility_analysis']['status']} ({analysis['volatility_analysis']['score']:.2f})
├─ Session: {analysis['probable_session']}
└─ Recommendation: {analysis['recommendation']}
            """.strip()
        else:
            return f"No analysis available for {symbol}"


# Instance globale du détecteur
_session_detector = None

def get_session_detector():
    """Retourne l'instance globale du détecteur de session"""
    global _session_detector
    if _session_detector is None:
        _session_detector = DynamicSessionDetector()
    return _session_detector

def is_market_active_dynamic(df, symbol):
    """
    Fonction utilitaire pour vérifier si le marché est actif dynamiquement
    
    Args:
        df: DataFrame OHLCV
        symbol: Symbole à analyser
    
    Returns:
        bool: True si le marché est actif
    """
    detector = get_session_detector()
    analysis = detector.analyze_market_activity(df, symbol)
    return analysis['is_active']

def get_dynamic_session_info(df, symbol):
    """
    Fonction utilitaire pour obtenir les informations de session dynamiques
    
    Args:
        df: DataFrame OHLCV
        symbol: Symbole à analyser
    
    Returns:
        dict: Informations complètes de session
    """
    detector = get_session_detector()
    return detector.analyze_market_activity(df, symbol)


    
