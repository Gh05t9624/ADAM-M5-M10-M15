# app/engine/dynamic_news_detector.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json

# Import du provider MT5
try:
    from app.engine.mt5_news_provider import get_mt5_news_provider
    MT5_NEWS_AVAILABLE = True
except ImportError:
    MT5_NEWS_AVAILABLE = False

class DynamicNewsDetector:
    """
    Détecte dynamiquement l'impact des news économiques sur le marché
    Basé sur l'analyse de l'activité avant/après les publications
    """
    
    def __init__(self):
        self.news_events = []
        self.market_reactions = {}
        self.impact_history = {}
        
        # News majeures avec leur importance attendue
        self.news_categories = {
            'HIGH': ['CPI', 'NFP', 'FOMC', 'FED', 'ECB', 'BOE', 'BOJ'],
            'MEDIUM': ['PMI', 'ISM', 'RETAIL_SALES', 'DURABLE_GOODS', 'GDP', 'INFLATION'],
            'LOW': ['UNEMPLOYMENT', 'CONSUMER_CONFIDENCE', 'HOUSING_STARTS', 'TRADE_BALANCE']
        }
    
    def detect_news_impact(self, df, symbol, lookback_periods=10, use_mt5_data=True):
        """
        Détecte l'impact des news récentes sur un symbole
        
        Args:
            df: DataFrame OHLCV
            symbol: Symbole à analyser
            lookback_periods: Périodes à analyser avant/après
            use_mt5_data: Utiliser les données MT5 si disponibles
        
        Returns:
            dict: Analyse complète d'impact de news
        """
        # 1. Essayer d'obtenir les news depuis MT5 d'abord
        mt5_news = []
        if use_mt5_data and MT5_NEWS_AVAILABLE:
            try:
                mt5_provider = get_mt5_news_provider()
                mt5_news = mt5_provider.get_news_events(symbol, hours_back=48)
                print(f"📰 MT5 News: {len(mt5_news)} événements trouvés pour {symbol}")
            except Exception as e:
                print(f"⚠️ Erreur MT5 news: {e}")
        
        # 2. Analyser les changements de comportement (méthode originale)
        if len(df) < lookback_periods * 2:
            return self._get_default_news_analysis(symbol)
        
        volatility_analysis = self._analyze_volatility_spike(df, lookback_periods)
        volume_analysis = self._analyze_volume_spike(df, lookback_periods)
        price_analysis = self._analyze_price_reaction(df, lookback_periods)
        
        # 3. Calculer le score d'impact de news
        impact_score = self._calculate_news_impact_score(
            volatility_analysis, volume_analysis, price_analysis
        )
        
        # 4. Identifier si c'est probablement une news
        news_detected = self._detect_news_event(impact_score, symbol)
        
        # 5. Ajuster l'impact si on a des news MT5
        if mt5_news:
            # Augmenter le score si des news MT5 sont présentes
            impact_score = min(1.0, impact_score + 0.2)  # Bonus de +20%
            news_detected = True
            print(f"📈 Impact score ajusté avec MT5: {impact_score:.3f}")
        
        # 6. Classifier l'impact
        impact_level = self._classify_impact_level(impact_score)
        
        # 7. Recommandations
        recommendations = self._get_news_recommendations(impact_level, symbol)
        
        # 8. Ajouter les news MT5 aux recommandations
        if mt5_news:
            mt5_recommendations = []
            for news in mt5_news[:3]:  # Top 3 news
                if hasattr(news, '__dict__'):
                    news_info = news.__dict__
                    time_str = str(news_info.get('time', 'N/A'))
                    event_name = str(news_info.get('event', 'N/A'))
                    impact = str(news_info.get('impact', 'N/A'))
                    mt5_recommendations.append(f"📋 {time_str}: {event_name} ({impact})")
            
            recommendations.extend(mt5_recommendations)
        
        result = {
            'symbol': symbol,
            'news_detected': news_detected,
            'impact_score': impact_score,
            'impact_level': impact_level,
            'volatility_analysis': volatility_analysis,
            'volume_analysis': volume_analysis,
            'price_analysis': price_analysis,
            'mt5_news': mt5_news,
            'mt5_news_count': len(mt5_news),
            'recommendations': recommendations,
            'analysis_time': datetime.utcnow(),
            'should_block_trading': impact_score > 0.7,
            'data_source': 'MT5+Market' if mt5_news else 'Market'
        }
        
        # Mettre en cache
        self.market_reactions[symbol] = result
        
        return result
    
    def _analyze_volatility_spike(self, df, lookback_periods):
        """Analyse les pics de volatilité (signe de news)"""
        # Calculer l'ATR sur différentes périodes
        df['tr'] = df['high'] - df['low']
        atr_short = df['tr'].rolling(window=5).mean()
        atr_long = df['tr'].rolling(window=lookback_periods).mean()
        
        # Ratio de volatilité (court terme vs long terme)
        volatility_ratio = atr_short.iloc[-1] / atr_long.iloc[-1] if atr_long.iloc[-1] > 0 else 1.0
        
        # Détecter les pics soudains
        volatility_change = atr_short.pct_change().tail(5)
        max_spike = volatility_change.max()
        
        # Score de volatilité (0-1)
        volatility_score = min(1.0, volatility_ratio * 0.6 + max_spike * 0.4)
        
        return {
            'current_atr': atr_short.iloc[-1],
            'average_atr': atr_long.iloc[-1],
            'volatility_ratio': volatility_ratio,
            'max_spike': max_spike,
            'score': volatility_score
        }
    
    def _analyze_volume_spike(self, df, lookback_periods):
        """Analyse les pics de volume (signe de news)"""
        if 'volume' not in df.columns:
            return {'score': 0.5, 'status': 'No volume data'}
        
        # Volume moyen vs volume récent
        avg_volume = df['volume'].rolling(window=lookback_periods).mean().iloc[-1]
        current_volume = df['volume'].iloc[-1]
        recent_max = df['volume'].tail(5).max()
        
        # Ratios de volume
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        spike_ratio = recent_max / avg_volume if avg_volume > 0 else 1.0
        
        # Score de volume (0-1)
        volume_score = min(1.0, volume_ratio * 0.5 + spike_ratio * 0.5)
        
        return {
            'current_volume': current_volume,
            'average_volume': avg_volume,
            'volume_ratio': volume_ratio,
            'spike_ratio': spike_ratio,
            'score': volume_score
        }
    
    def _analyze_price_reaction(self, df, lookback_periods):
        """Analyse la réaction des prix (gaps, mouvements brusques)"""
        # Gaps (ouverture vs clôture précédente)
        df['gap'] = (df['open'] - df['close'].shift()).abs()
        
        # Mouvements anormaux
        df['price_change'] = df['close'].pct_change()
        df['abs_change'] = df['price_change'].abs()
        
        # Statistiques récentes
        recent_gaps = df['gap'].tail(5)
        recent_changes = df['abs_change'].tail(5)
        
        # Moyennes
        avg_gap = recent_gaps.mean()
        max_gap = recent_gaps.max()
        avg_change = recent_changes.mean()
        max_change = recent_changes.max()
        
        # Comparer avec l'historique
        historical_avg_change = df['abs_change'].rolling(window=lookback_periods).mean().iloc[-1]
        
        # Score de réaction de prix (0-1)
        gap_score = min(1.0, max_gap / (historical_avg_change * 2) if historical_avg_change > 0 else 0)
        movement_score = min(1.0, max_change / historical_avg_change if historical_avg_change > 0 else 0)
        
        price_score = (gap_score + movement_score) / 2
        
        return {
            'avg_gap': avg_gap,
            'max_gap': max_gap,
            'avg_change': avg_change,
            'max_change': max_change,
            'historical_avg': historical_avg_change,
            'score': price_score
        }
    
    def _calculate_news_impact_score(self, volatility_analysis, volume_analysis, price_analysis):
        """Calcule un score composite d'impact de news"""
        
        # Pondérations selon la fiabilité
        weights = {
            'volatility': 0.40,    # Très fiable pour détecter les news
            'volume': 0.35,        # Très fiable aussi
            'price': 0.25           # Moins fiable (peut être du bruit)
        }
        
        # Score pondéré
        impact_score = (
            volatility_analysis['score'] * weights['volatility'] +
            volume_analysis['score'] * weights['volume'] +
            price_analysis['score'] * weights['price']
        )
        
        return round(impact_score, 3)
    
    def _detect_news_event(self, impact_score, symbol):
        """Détecte si c'est probablement un événement de news"""
        
        # Seuils différents par type d'actif
        thresholds = {
            'BTC': 0.25,     # Bitcoin : moins sensible aux news traditionnelles
            'XAU': 0.35,     # Or : sensible aux news économiques
            'default': 0.30    # Forex : standard
        }
        
        for key, threshold in thresholds.items():
            if key in symbol.upper():
                return impact_score > threshold
        
        return impact_score > thresholds['default']
    
    def _classify_impact_level(self, impact_score):
        """Classifie le niveau d'impact"""
        if impact_score >= 0.8:
            return "HIGH_IMPACT"
        elif impact_score >= 0.6:
            return "MEDIUM_IMPACT"
        elif impact_score >= 0.4:
            return "LOW_IMPACT"
        else:
            return "NO_IMPACT"
    
    def _get_news_recommendations(self, impact_level, symbol):
        """Génère des recommandations selon l'impact"""
        recommendations = []
        
        if impact_level == "HIGH_IMPACT":
            recommendations.extend([
                "🚨 HIGH IMPACT DETECTED",
                "⛔ Consider blocking trades",
                "⏰ Wait for market stabilization",
                "📊 Monitor volatility closely"
            ])
        elif impact_level == "MEDIUM_IMPACT":
            recommendations.extend([
                "⚠️ MEDIUM IMPACT DETECTED",
                "🔍 Reduce position sizes",
                "⚖️ Wider stops recommended",
                "📈 Watch for trend changes"
            ])
        elif impact_level == "LOW_IMPACT":
            recommendations.extend([
                "ℹ️ LOW IMPACT DETECTED",
                "🎯 Normal trading with caution",
                "📊 Monitor for follow-up"
            ])
        else:
            recommendations.extend([
                "✅ No significant news impact",
                "🔄 Normal market conditions",
                "📈 Standard trading rules apply"
            ])
        
        # Recommandations spécifiques par symbole
        if "XAU" in symbol:
            recommendations.append("🥇 Gold: Watch USD strength")
        elif "BTC" in symbol:
            recommendations.append("₿ Bitcoin: Watch crypto sentiment")
        
        return recommendations
    
    def _get_default_news_analysis(self, symbol):
        """Retourne une analyse par défaut si pas assez de données"""
        return {
            'symbol': symbol,
            'news_detected': False,
            'impact_score': 0.0,
            'impact_level': 'NO_IMPACT',
            'volatility_analysis': {'score': 0.5},
            'volume_analysis': {'score': 0.5},
            'price_analysis': {'score': 0.5},
            'recommendations': ['Insufficient data for news analysis'],
            'analysis_time': datetime.utcnow(),
            'should_block_trading': False
        }
    
    def is_high_impact_news_time(self, symbol):
        """
        Vérifie si on est dans une période de news à haut impact
        
        Args:
            symbol: Symbole à vérifier
        
        Returns:
            bool: True si news à haut impact détectée
        """
        if symbol in self.market_reactions:
            analysis = self.market_reactions[symbol]
            return analysis.get('should_block_trading', False)
        
        return False
    
    def get_news_summary(self, symbol):
        """Retourne un résumé de l'analyse de news"""
        if symbol in self.market_reactions:
            analysis = self.market_reactions[symbol]
            return f"""
📰 News Impact Analysis for {symbol}
├─ News Detected: {'🚨 YES' if analysis['news_detected'] else '✅ NO'}
├─ Impact Level: {analysis['impact_level']}
├─ Impact Score: {analysis['impact_score']:.3f}/1.000
├─ Volatility Spike: {analysis['volatility_analysis']['score']:.2f}
├─ Volume Spike: {analysis['volume_analysis']['score']:.2f}
├─ Price Reaction: {analysis['price_analysis']['score']:.2f}
├─ Should Block: {'🚫 YES' if analysis['should_block_trading'] else '✅ NO'}
└─ Top Recommendation: {analysis['recommendations'][0] if analysis['recommendations'] else 'None'}
            """.strip()
        else:
            return f"No news analysis available for {symbol}"


# Instance globale du détecteur de news
_news_detector = None

def get_news_detector():
    """Retourne l'instance globale du détecteur de news"""
    global _news_detector
    if _news_detector is None:
        _news_detector = DynamicNewsDetector()
    return _news_detector

def is_dynamic_news_time(df, symbol):
    """
    Fonction utilitaire pour vérifier si on est dans une période de news à impact
    
    Args:
        df: DataFrame OHLCV
        symbol: Symbole à analyser
    
    Returns:
        bool: True si news à impact détectée
    """
    detector = get_news_detector()
    analysis = detector.detect_news_impact(df, symbol)
    return analysis.get('should_block_trading', False)

def get_dynamic_news_analysis(df, symbol):
    """
    Fonction utilitaire pour obtenir l'analyse complète des news
    
    Args:
        df: DataFrame OHLCV
        symbol: Symbole à analyser
    
    Returns:
        dict: Analyse complète des news
    """
    detector = get_news_detector()
    return detector.detect_news_impact(df, symbol)
    detector = DynamicNewsDetector()
    analysis = detector.detect_news_impact(df, "XAUUSD")
    
    print(detector.get_news_summary("XAUUSD"))
