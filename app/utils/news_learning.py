# app/utils/news_learning.py
# Système d'apprentissage automatique des patterns de news

import json
import os
import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import MetaTrader5 as mt5

class NewsLearningSystem:
    """
    Système d'apprentissage automatique qui détecte et apprend les patterns de news
    en analysant la volatilité et le comportement du marché
    """
    
    def __init__(self):
        self.learning_file = "news_learning.json"
        self.learning_data = self._load_learning_data()
        self.patterns = self._initialize_patterns()
        self.confidence_threshold = 0.7  # Seuil de confiance pour les patterns
    
    def _load_learning_data(self) -> Dict:
        """Charge les données d'apprentissage"""
        if os.path.exists(self.learning_file):
            try:
                with open(self.learning_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Erreur chargement apprentissage: {e}")
                return {}
        return {}
    
    def _save_learning_data(self):
        """Sauvegarde les données d'apprentissage"""
        try:
            with open(self.learning_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erreur sauvegarde apprentissage: {e}")
    
    def _initialize_patterns(self) -> Dict:
        """Initialise les structures de pattern"""
        return {
            'hourly_patterns': defaultdict(int),      # Patterns par heure
            'daily_patterns': defaultdict(int),       # Patterns par jour
            'session_patterns': defaultdict(int),     # Patterns par session
            'currency_patterns': defaultdict(int),    # Patterns par devise
            'volatility_profiles': {},                # Profils de volatilité
            'learned_events': [],                     # Événements appris
            'confidence_scores': {}                   # Scores de confiance
        }
    
    def analyze_market_for_news(self, symbol: str, df: pd.DataFrame,
                              timeframe: str = "M5") -> List[Dict]:
        """
        Analyse les données de marché pour détecter automatiquement les périodes de news
        
        Args:
            symbol: Symbole du marché
            df: DataFrame OHLCV
            timeframe: Timeframe des données
        
        Returns:
            List[Dict]: Liste des événements de news détectés
        """
        if df is None or len(df) < 50:
            return []
        
        detected_events = []
        
        # Calculer les métriques de volatilité
        df['range'] = df['high'] - df['low']
        df['range_pct'] = (df['range'] / df['close']) * 100
        df['body_size'] = abs(df['close'] - df['open'])
        df['body_pct'] = (df['body_size'] / df['close']) * 100
        
        # Calculer les moyennes mobiles de volatilité
        df['volatility_ma20'] = df['range_pct'].rolling(window=20).mean()
        df['volatility_ma50'] = df['range_pct'].rolling(window=50).mean()
        
        # Détecter les spikes de volatilité (indicateurs de news)
        volatility_threshold = df['volatility_ma20'].mean() + (2 * df['volatility_ma20'].std())
        
        for i in range(50, len(df)):
            current_vol = df['range_pct'].iloc[i]
            avg_vol = df['volatility_ma20'].iloc[i]
            
            # Spike de volatilité significatif
            if current_vol > volatility_threshold * 1.5:
                candle_time = pd.to_datetime(df['time'].iloc[i], unit='s')
                
                # Analyse du contexte
                event = self._analyze_volatility_spike(
                    symbol, df, i, candle_time, current_vol, avg_vol
                )
                
                if event and event['confidence'] > self.confidence_threshold:
                    detected_events.append(event)
                    self._learn_from_event(event)
        
        return detected_events
    
    def _analyze_volatility_spike(self, symbol: str, df: pd.DataFrame, 
                                 index: int, candle_time: datetime,
                                 current_vol: float, avg_vol: float) -> Optional[Dict]:
        """
        Analyse un spike de volatilité pour déterminer si c'est une news
        
        Args:
            symbol: Symbole du marché
            df: DataFrame OHLCV
            index: Index de la bougie
            candle_time: Heure de la bougie
            current_vol: Volatilité actuelle
            avg_vol: Volatilité moyenne
        
        Returns:
            Dict: Informations sur l'événement détecté ou None
        """
        # Extraire la devise du symbole
        currency = self._extract_currency(symbol)
        
        # Analyser le contexte temporel
        hour = candle_time.hour
        day_of_week = candle_time.strftime('%A')
        session = self._get_session_at_time(candle_time)
        
        # Analyser le comportement des bougies
        current_candle = df.iloc[index]
        prev_candles = df.iloc[index-5:index]  # 5 bougies précédentes
        
        # Volume analysis
        current_volume = current_candle.get('volume', 0)
        avg_volume = prev_candles['volume'].mean() if len(prev_candles) > 0 else 0
        volume_spike = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Price movement analysis
        price_change = abs(current_candle['close'] - current_candle['open']) / current_candle['open'] * 100
        
        # Calculer le score de confiance
        confidence = self._calculate_confidence_score(
            current_vol, avg_vol, volume_spike, price_change, 
            hour, day_of_week, session
        )
        
        if confidence > self.confidence_threshold:
            return {
                'symbol': symbol,
                'currency': currency,
                'datetime': candle_time.isoformat(),
                'time_utc': candle_time.strftime('%H:%M'),
                'day_of_week': day_of_week,
                'hour': hour,
                'session': session,
                'volatility_spike': current_vol,
                'volatility_ratio': current_vol / avg_vol if avg_vol > 0 else 1,
                'volume_spike': volume_spike,
                'price_change': price_change,
                'confidence': confidence,
                'event_type': self._classify_event_type(current_vol, price_change, session),
                'detected_at': datetime.now(timezone.utc).isoformat()
            }
        
        return None
    
    def _calculate_confidence_score(self, current_vol: float, avg_vol: float,
                                   volume_spike: float, price_change: float,
                                   hour: int, day: str, session: str) -> float:
        """
        Calcule un score de confiance que c'est une news
        
        Args:
            current_vol: Volatilité actuelle
            avg_vol: Volatilité moyenne
            volume_spike: Spike de volume
            price_change: Changement de prix
            hour: Heure
            day: Jour de la semaine
            session: Session de trading
        
        Returns:
            float: Score de confiance (0-1)
        """
        score = 0.0
        
        # Volatilité (40% du score)
        vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1
        if vol_ratio > 3.0:
            score += 0.40
        elif vol_ratio > 2.0:
            score += 0.30
        elif vol_ratio > 1.5:
            score += 0.20
        elif vol_ratio > 1.2:
            score += 0.10
        
        # Volume (25% du score)
        if volume_spike > 2.5:
            score += 0.25
        elif volume_spike > 2.0:
            score += 0.20
        elif volume_spike > 1.5:
            score += 0.15
        elif volume_spike > 1.2:
            score += 0.10
        
        # Mouvement de prix (20% du score)
        if price_change > 0.5:
            score += 0.20
        elif price_change > 0.3:
            score += 0.15
        elif price_change > 0.2:
            score += 0.10
        elif price_change > 0.1:
            score += 0.05
        
        # Contexte temporel (15% du score)
        # Heures typiques de news (13:00-14:00 UTC pour USD, 12:00-13:00 pour EUR/GBP)
        if 12 <= hour <= 14:
            score += 0.15
        elif 8 <= hour <= 10:  # Session asiatique
            score += 0.10
        elif 17 <= hour <= 19:  # Overlap
            score += 0.10
        
        # Session active
        if session in ['LONDRES', 'NEW_YORK', 'OVERLAP']:
            score += 0.05
        
        return min(score, 1.0)
    
    def _classify_event_type(self, volatility: float, price_change: float, 
                            session: str) -> str:
        """Classifie le type d'événement détecté"""
        if volatility > 0.5 and price_change > 0.3:
            return "HIGH_IMPACT_NEWS"
        elif volatility > 0.3 and price_change > 0.2:
            return "MEDIUM_IMPACT_NEWS"
        elif volatility > 0.2:
            return "LOW_IMPACT_NEWS"
        else:
            return "MARKET_NOISE"
    
    def _extract_currency(self, symbol: str) -> str:
        """Extrait la devise principale du symbole"""
        if 'USD' in symbol:
            return 'USD'
        elif 'EUR' in symbol:
            return 'EUR'
        elif 'GBP' in symbol:
            return 'GBP'
        elif 'JPY' in symbol:
            return 'JPY'
        elif 'AUD' in symbol:
            return 'AUD'
        elif 'CAD' in symbol:
            return 'CAD'
        elif 'CHF' in symbol:
            return 'CHF'
        else:
            return 'OTHER'
    
    def _get_session_at_time(self, datetime_obj: datetime) -> str:
        """Détermine la session de trading"""
        hour = datetime_obj.hour
        
        if 0 <= hour < 8:
            return "ASIE"
        elif 8 <= hour < 13:
            return "LONDRES"
        elif 13 <= hour < 17:
            return "NEW_YORK"
        elif 17 <= hour < 22:
            return "OVERLAP"
        else:
            return "WEEKEND"
    
    def _learn_from_event(self, event: Dict):
        """Apprend d'un événement détecté"""
        # Mettre à jour les patterns
        hour = event['hour']
        day = event['day_of_week']
        session = event['session']
        currency = event['currency']
        
        self.patterns['hourly_patterns'][hour] += 1
        self.patterns['daily_patterns'][day] += 1
        self.patterns['session_patterns'][session] += 1
        self.patterns['currency_patterns'][currency] += 1
        
        # Ajouter à l'historique des événements appris
        self.patterns['learned_events'].append(event)
        
        # Mettre à jour les scores de confiance
        pattern_key = f"{hour}_{day}_{session}_{currency}"
        if pattern_key not in self.patterns['confidence_scores']:
            self.patterns['confidence_scores'][pattern_key] = {
                'count': 0,
                'total_confidence': 0,
                'avg_confidence': 0
            }
        
        self.patterns['confidence_scores'][pattern_key]['count'] += 1
        self.patterns['confidence_scores'][pattern_key]['total_confidence'] += event['confidence']
        self.patterns['confidence_scores'][pattern_key]['avg_confidence'] = (
            self.patterns['confidence_scores'][pattern_key]['total_confidence'] / 
            self.patterns['confidence_scores'][pattern_key]['count']
        )
        
        # Sauvegarder les apprentissages
        self._save_learning_data()
        
        print(f"🧠 Apprentissage: {event['currency']} à {event['time_utc']} UTC (Confiance: {event['confidence']:.2f})")
    
    def predict_news_probability(self, symbol: str, check_time: datetime = None) -> Dict:
        """
        Prédit la probabilité de news pour un moment donné
        
        Args:
            symbol: Symbole du marché
            check_time: Heure à vérifier (défaut: maintenant)
        
        Returns:
            Dict: Probabilité et détails
        """
        if check_time is None:
            check_time = datetime.now(timezone.utc)
        
        currency = self._extract_currency(symbol)
        hour = check_time.hour
        day = check_time.strftime('%A')
        session = self._get_session_at_time(check_time)
        
        # Calculer la probabilité basée sur les patterns appris
        total_events = len(self.patterns['learned_events'])
        
        if total_events == 0:
            return {
                'probability': 0.0,
                'confidence': 0.0,
                'reason': 'Pas assez de données pour prédire'
            }
        
        # Probabilité basée sur l'heure
        hour_events = self.patterns['hourly_patterns'].get(hour, 0)
        hour_prob = hour_events / total_events
        
        # Probabilité basée sur le jour
        day_events = self.patterns['daily_patterns'].get(day, 0)
        day_prob = day_events / total_events
        
        # Probabilité basée sur la session
        session_events = self.patterns['session_patterns'].get(session, 0)
        session_prob = session_events / total_events
        
        # Probabilité basée sur la devise
        currency_events = self.patterns['currency_patterns'].get(currency, 0)
        currency_prob = currency_events / total_events
        
        # Score de confiance du pattern
        pattern_key = f"{hour}_{day}_{session}_{currency}"
        pattern_confidence = 0.0
        if pattern_key in self.patterns['confidence_scores']:
            pattern_confidence = self.patterns['confidence_scores'][pattern_key]['avg_confidence']
        
        # Probabilité combinée
        combined_prob = (hour_prob * 0.3 + day_prob * 0.2 + 
                        session_prob * 0.3 + currency_prob * 0.2)
        
        return {
            'probability': combined_prob,
            'confidence': pattern_confidence,
            'hour_probability': hour_prob,
            'day_probability': day_prob,
            'session_probability': session_prob,
            'currency_probability': currency_prob,
            'total_events_learned': total_events,
            'reason': 'Basé sur ' + str(total_events) + ' événements appris'
        }
    
    def get_learned_patterns(self) -> Dict:
        """Retourne les patterns appris"""
        total_events = len(self.patterns['learned_events'])
        
        if total_events == 0:
            return {'error': 'Aucun pattern appris'}
        
        # Trouver les heures les plus fréquentes
        top_hours = sorted(self.patterns['hourly_patterns'].items(), 
                          key=lambda x: x[1], reverse=True)[:5]
        
        # Trouver les jours les plus fréquentes
        top_days = sorted(self.patterns['daily_patterns'].items(), 
                         key=lambda x: x[1], reverse=True)[:5]
        
        # Trouver les sessions les plus fréquentes
        top_sessions = sorted(self.patterns['session_patterns'].items(), 
                             key=lambda x: x[1], reverse=True)
        
        # Trouver les devises les plus fréquentes
        top_currencies = sorted(self.patterns['currency_patterns'].items(), 
                               key=lambda x: x[1], reverse=True)
        
        return {
            'total_events_learned': total_events,
            'top_hours': top_hours,
            'top_days': top_days,
            'top_sessions': top_sessions,
            'top_currencies': top_currencies,
            'confidence_scores': dict(self.patterns['confidence_scores'])
        }
    
    def print_learning_summary(self):
        """Affiche un résumé de l'apprentissage"""
        patterns = self.get_learned_patterns()
        
        if 'error' in patterns:
            print("❌ Aucun pattern appris - Lancez l'analyse de marché pour commencer l'apprentissage")
            return
        
        print("\n🧠 RÉSUMÉ DE L'APPRENTISSAGE AUTONOME")
        print("=" * 70)
        print(f"📊 Événements appris: {patterns['total_events_learned']}")
        
        print(f"\n⏰ HEURES LES PLUS FRÉQUENTES:")
        for hour, count in patterns['top_hours']:
            print(f"  {hour:02d}:00 UTC: {count} événements ({count/patterns['total_events_learned']*100:.1f}%)")
        
        print(f"\n📅 JOURS LES PLUS FRÉQUENTS:")
        for day, count in patterns['top_days']:
            print(f"  {day}: {count} événements ({count/patterns['total_events_learned']*100:.1f}%)")
        
        print(f"\n🌍 SESSIONS LES PLUS FRÉQUENTES:")
        for session, count in patterns['top_sessions']:
            print(f"  {session}: {count} événements ({count/patterns['total_events_learned']*100:.1f}%)")
        
        print(f"\n💱 DEVISES LES PLUS FRÉQUENTES:")
        for currency, count in patterns['top_currencies']:
            print(f"  {currency}: {count} événements ({count/patterns['total_events_learned']*100:.1f}%)")
        
        print(f"\n📈 SCORES DE CONFIANCE DES PATTERNS:")
        for pattern, scores in patterns['confidence_scores'].items():
            if scores['count'] >= 3:  # Afficher seulement les patterns avec assez de données
                print(f"  {pattern}: {scores['avg_confidence']:.2f} ({scores['count']} occurrences)")
    
    def is_high_news_probability(self, symbol: str, threshold: float = 0.3, 
                                check_time: datetime = None) -> bool:
        """
        Vérifie si la probabilité de news est élevée
        
        Args:
            symbol: Symbole du marché
            threshold: Seuil de probabilité
            check_time: Heure à vérifier
        
        Returns:
            bool: True si probabilité élevée
        """
        prediction = self.predict_news_probability(symbol, check_time)
        return prediction['probability'] > threshold

# Instance globale
_news_learning = None

def get_news_learning_system():
    """Retourne l'instance globale du système d'apprentissage"""
    global _news_learning
    if _news_learning is None:
        _news_learning = NewsLearningSystem()
    return _news_learning

# Fonctions utilitaires
def analyze_market_for_news(symbol: str, df: pd.DataFrame, timeframe: str = "M5"):
    """Analyse le marché pour détecter les news"""
    system = get_news_learning_system()
    return system.analyze_market_for_news(symbol, df, timeframe)

def predict_news_probability(symbol: str, check_time: datetime = None) -> Dict:
    """Prédit la probabilité de news"""
    system = get_news_learning_system()
    return system.predict_news_probability(symbol, check_time)

def is_high_news_probability(symbol: str, threshold: float = 0.3, check_time: datetime = None) -> bool:
    """Vérifie si probabilité élevée de news"""
    system = get_news_learning_system()
    return system.is_high_news_probability(symbol, threshold, check_time)

def print_learning_summary():
    """Affiche le résumé de l'apprentissage"""
    system = get_news_learning_system()
    system.print_learning_summary()
