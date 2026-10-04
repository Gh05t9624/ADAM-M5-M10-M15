# app/utils/news_tracker.py
# Suivi détaillé des news et leur impact sur les marchés

import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd

class NewsTracker:
    """
    Suivi des news économiques et leur impact sur les bougies
    """
    
    def __init__(self):
        self.news_file = "news_tracker.json"
        self.news_data = self._load_news_data()
    
    def _load_news_data(self) -> Dict:
        """Charge les données de news depuis le fichier"""
        if os.path.exists(self.news_file):
            try:
                with open(self.news_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Erreur chargement news tracker: {e}")
                return {}
        return {}
    
    def _save_news_data(self):
        """Sauvegarde les données de news dans le fichier"""
        try:
            with open(self.news_file, 'w', encoding='utf-8') as f:
                json.dump(self.news_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erreur sauvegarde news tracker: {e}")
    
    def add_news_event(self, symbol: str, event_data: Dict, impact_analysis: Dict = None):
        """
        Ajoute un événement de news avec son impact
        
        Args:
            symbol: Symbole du marché
            event_data: Données de l'événement
            impact_analysis: Analyse de l'impact sur les bougies
        """
        date_key = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        if date_key not in self.news_data:
            self.news_data[date_key] = []
        
        news_event = {
            'id': len(self.news_data[date_key]) + 1,
            'symbol': symbol,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_time': event_data.get('time', 'N/A'),
            'event': event_data.get('event', 'N/A'),
            'currency': event_data.get('currency', 'N/A'),
            'impact': event_data.get('impact', 'N/A'),
            'actual': event_data.get('actual', 'N/A'),
            'forecast': event_data.get('forecast', 'N/A'),
            'previous': event_data.get('previous', 'N/A'),
            'session': self._get_session_at_time(event_data.get('time')),
            'day_of_week': self._get_day_of_week(event_data.get('time')),
            'impact_analysis': impact_analysis or {}
        }
        
        self.news_data[date_key].append(news_event)
        self._save_news_data()
        
        print(f"📰 News ajoutée: {symbol} - {event_data.get('event', 'N/A')}")
    
    def add_candle_impact(self, symbol: str, news_id: int, candle_data: Dict, time_before: int, time_after: int):
        """
        Ajoute l'analyse d'impact d'une news sur les bougies
        
        Args:
            symbol: Symbole du marché
            news_id: ID de la news
            candle_data: Données de la bougie impactée
            time_before: Minutes avant la news
            time_after: Minutes après la news
        """
        # Trouver la news correspondante
        date_key = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        if date_key in self.news_data:
            for news_event in self.news_data[date_key]:
                if news_event['id'] == news_id:
                    impact_analysis = {
                        'candle_before_news': {
                            'time_before': time_before,
                            'open': candle_data.get('open'),
                            'high': candle_data.get('high'),
                            'low': candle_data.get('low'),
                            'close': candle_data.get('close'),
                            'volume': candle_data.get('volume'),
                            'range': candle_data.get('high', 0) - candle_data.get('low', 0)
                        },
                        'candle_after_news': {
                            'time_after': time_after,
                            'reaction': self._analyze_price_reaction(candle_data),
                            'volatility_spike': self._calculate_volatility_spike(candle_data),
                            'volume_increase': self._calculate_volume_increase(candle_data)
                        },
                        'impact_score': self._calculate_impact_score(candle_data),
                        'session_behavior': self._analyze_session_behavior(symbol, candle_data)
                    }
                    
                    news_event['impact_analysis'] = impact_analysis
                    self._save_news_data()
                    
                    print(f"📊 Impact analysé pour {symbol}: Score {impact_analysis['impact_score']}")
                    break
    
    def _analyze_price_reaction(self, candle_data: Dict) -> str:
        """Analyse la réaction du prix à la news"""
        open_price = candle_data.get('open', 0)
        close_price = candle_data.get('close', 0)
        high_price = candle_data.get('high', 0)
        low_price = candle_data.get('low', 0)
        
        price_change = (close_price - open_price) / open_price * 100
        range_size = (high_price - low_price) / open_price * 100
        
        if abs(price_change) > 0.5:  # > 0.5%
            return f"FORTE MOUVEMENT: {price_change:+.2f}%"
        elif abs(price_change) > 0.2:  # > 0.2%
            return f"MOUVEMENT MODÉRÉ: {price_change:+.2f}%"
        elif range_size > 0.3:  # > 0.3% range
            return f"VOLATILITÉ ÉLEVÉE: {range_size:.2f}%"
        else:
            return "RÉACTION FAIBLE"
    
    def _calculate_volatility_spike(self, candle_data: Dict) -> float:
        """Calcule le spike de volatilité"""
        high = candle_data.get('high', 0)
        low = candle_data.get('low', 0)
        open_price = candle_data.get('open', 0)
        
        if open_price == 0:
            return 0
        
        max_range = max(abs(high - open_price), abs(open_price - low))
        return (max_range / open_price) * 100
    
    def _calculate_volume_increase(self, candle_data: Dict) -> float:
        """Calcule l'augmentation du volume"""
        current_volume = candle_data.get('volume', 0)
        # Note: Pour un calcul précis, il faudrait comparer avec la moyenne précédente
        return current_volume  # Simplifié pour l'instant
    
    def _calculate_impact_score(self, candle_data: Dict) -> int:
        """Calcule un score d'impact (1-10)"""
        score = 0
        
        # Réaction de prix
        price_change = abs((candle_data.get('close', 0) - candle_data.get('open', 0)) / candle_data.get('open', 1) * 100)
        if price_change > 1.0:
            score += 4
        elif price_change > 0.5:
            score += 2
        elif price_change > 0.2:
            score += 1
        
        # Volatilité
        volatility_spike = self._calculate_volatility_spike(candle_data)
        if volatility_spike > 1.0:
            score += 3
        elif volatility_spike > 0.5:
            score += 2
        elif volatility_spike > 0.2:
            score += 1
        
        # Volume
        volume = candle_data.get('volume', 0)
        if volume > 10000:  # Seuil arbitraire
            score += 3
        elif volume > 5000:
            score += 2
        elif volume > 2000:
            score += 1
        
        return min(score, 10)
    
    def _analyze_session_behavior(self, symbol: str, candle_data: Dict) -> str:
        """Analyse le comportement du marché en session"""
        current_hour = datetime.now(timezone.utc).hour
        
        if 8 <= current_hour < 13:  # Session de Londres
            return "RÉACTION SESSION LONDRES"
        elif 13 <= current_hour < 17:  # Session de New York
            return "RÉACTION SESSION NEW YORK"
        elif 17 <= current_hour < 22:  # Session de chevauchement
            return "RÉACTION SESSION OVERLAP"
        else:
            return "HORS SESSION PRINCIPALE"
    
    def _get_session_at_time(self, event_time) -> str:
        """Détermine la session de trading à l'heure de la news"""
        if not event_time:
            return "INCONNUE"
        
        if isinstance(event_time, str):
            try:
                event_time = datetime.fromisoformat(event_time.replace('Z', '+00:00'))
            except:
                return "INCONNUE"
        
        hour = event_time.hour
        
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
    
    def _get_day_of_week(self, event_time) -> str:
        """Retourne le jour de la semaine"""
        if not event_time:
            return "INCONNU"
        
        days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        
        if isinstance(event_time, str):
            try:
                event_time = datetime.fromisoformat(event_time.replace('Z', '+00:00'))
            except:
                return "INCONNU"
        
        return days[event_time.weekday()]
    
    def get_news_summary(self, symbol: str = None, days_back: int = 7) -> Dict:
        """
        Retourne un résumé des news
        
        Args:
            symbol: Symbole à filtrer (optionnel)
            days_back: Nombre de jours à regarder en arrière
        
        Returns:
            Dict: Résumé des news
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        cutoff_key = cutoff_date.strftime('%Y-%m-%d')
        
        total_news = 0
        high_impact_news = 0
        symbol_news = {}
        
        for date_key, events in self.news_data.items():
            if date_key >= cutoff_key:
                for event in events:
                    total_news += 1
                    
                    if event.get('impact') == 'HIGH':
                        high_impact_news += 1
                    
                    event_symbol = event.get('symbol')
                    if event_symbol:
                        if event_symbol not in symbol_news:
                            symbol_news[event_symbol] = 0
                        symbol_news[event_symbol] += 1
        
        return {
            'period': f'Derniers {days_back} jours',
            'total_news': total_news,
            'high_impact_news': high_impact_news,
            'news_by_symbol': symbol_news,
            'most_active_symbol': max(symbol_news.items(), key=lambda x: x[1])[0] if symbol_news else None
        }
    
    def print_news_report(self, symbol: str = None):
        """Affiche un rapport détaillé des news"""
        summary = self.get_news_summary(symbol)
        
        print(f"\n📰 RAPPORT NEWS - {summary['period']}")
        print("=" * 60)
        print(f"Total news: {summary['total_news']}")
        print(f"News à fort impact: {summary['high_impact_news']}")
        
        if summary['news_by_symbol']:
            print(f"\n📊 News par symbole:")
            for sym, count in sorted(summary['news_by_symbol'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {sym}: {count} news")
            
            if summary['most_active_symbol']:
                print(f"\n🏆 Symbole le plus actif: {summary['most_active_symbol']}")
        
        # Détail des news récentes avec impact
        print(f"\n📋 Détail des news récentes:")
        recent_news = []
        
        for date_key, events in self.news_data.items():
            for event in events:
                if not symbol or event.get('symbol') == symbol:
                    recent_news.append(event)
        
        # Trier par impact score
        recent_news.sort(key=lambda x: x.get('impact_analysis', {}).get('impact_score', 0), reverse=True)
        
        for i, event in enumerate(recent_news[:10]):  # Top 10
            impact_score = event.get('impact_analysis', {}).get('impact_score', 0)
            impact_emoji = "🔴" if impact_score >= 7 else "🟡" if impact_score >= 4 else "🟢"
            
            print(f"\n  {i+1}. {impact_emoji} {event.get('symbol', 'N/A')} - {event.get('event', 'N/A')}")
            print(f"     Heure: {event.get('event_time', 'N/A')}")
            print(f"     Session: {event.get('session', 'N/A')}")
            print(f"     Jour: {event.get('day_of_week', 'N/A')}")
            print(f"     Impact: {event.get('impact', 'N/A')}")
            print(f"     Score: {impact_score}/10")
            
            if 'impact_analysis' in event:
                analysis = event['impact_analysis']
                print(f"     Réaction: {analysis.get('candle_after_news', {}).get('reaction', 'N/A')}")
                print(f"     Volatilité: {analysis.get('candle_after_news', {}).get('volatility_spike', 0):.2f}%")
    
    def export_to_csv(self, symbol: str = None, filename: str = None):
        """Exporte les données de news en CSV pour analyse"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"news_report_{timestamp}.csv"
        
        csv_data = []
        for date_key, events in self.news_data.items():
            for event in events:
                if not symbol or event.get('symbol') == symbol:
                    row = {
                        'Date': date_key,
                        'Symbol': event.get('symbol'),
                        'Event_Time': event.get('event_time'),
                        'Event': event.get('event'),
                        'Currency': event.get('currency'),
                        'Impact': event.get('impact'),
                        'Actual': event.get('actual'),
                        'Forecast': event.get('forecast'),
                        'Previous': event.get('previous'),
                        'Session': event.get('session'),
                        'Day_of_Week': event.get('day_of_week'),
                        'Impact_Score': event.get('impact_analysis', {}).get('impact_score', 0),
                        'Price_Reaction': event.get('impact_analysis', {}).get('candle_after_news', {}).get('reaction', 'N/A')
                    }
                    csv_data.append(row)
        
        if csv_data:
            df = pd.DataFrame(csv_data)
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"✅ Données news exportées dans {filename}")
        else:
            print("❌ Aucune donnée à exporter")

# Instance globale
_news_tracker = None

def get_news_tracker():
    """Retourne l'instance globale du tracker de news"""
    global _news_tracker
    if _news_tracker is None:
        _news_tracker = NewsTracker()
    return _news_tracker

# Fonctions utilitaires
def add_news_event(symbol: str, event_data: Dict, impact_analysis: Dict = None):
    """Ajoute un événement de news"""
    tracker = get_news_tracker()
    tracker.add_news_event(symbol, event_data, impact_analysis)

def add_candle_impact(symbol: str, news_id: int, candle_data: Dict, time_before: int, time_after: int):
    """Ajoute l'impact d'une news sur les bougies"""
    tracker = get_news_tracker()
    tracker.add_candle_impact(symbol, news_id, candle_data, time_before, time_after)

def print_news_report(symbol: str = None):
    """Affiche le rapport des news"""
    tracker = get_news_tracker()
    tracker.print_news_report(symbol)
