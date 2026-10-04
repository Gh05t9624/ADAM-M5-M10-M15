# app/utils/market_notes.py
# Système de notes détaillées pour chaque marché

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

class MarketNotes:
    """
    Système de notes pour suivre l'analyse technique de chaque marché
    """
    
    def __init__(self):
        self.notes_file = "market_notes.json"
        self.notes = self._load_notes()
    
    def _load_notes(self) -> Dict:
        """Charge les notes depuis le fichier"""
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Erreur chargement notes: {e}")
                return {}
        return {}
    
    def _save_notes(self):
        """Sauvegarde les notes dans le fichier"""
        try:
            with open(self.notes_file, 'w', encoding='utf-8') as f:
                json.dump(self.notes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erreur sauvegarde notes: {e}")
    
    def add_note(self, symbol: str, note_type: str, content: str, impact_level: int = 1):
        """
        Ajoute une note pour un marché
        
        Args:
            symbol: Symbole du marché (ex: EURUSD)
            note_type: Type de note (NEWS, TECHNICAL, IMPACT, OBSERVATION)
            content: Contenu de la note
            impact_level: Niveau d'impact (1-5)
        """
        if symbol not in self.notes:
            self.notes[symbol] = {
                'symbol': symbol,
                'notes': [],
                'created_at': datetime.now(timezone.utc).isoformat(),
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
        
        note = {
            'id': len(self.notes[symbol]['notes']) + 1,
            'type': note_type,
            'content': content,
            'impact_level': impact_level,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'session': self._get_current_session()
        }
        
        self.notes[symbol]['notes'].append(note)
        self.notes[symbol]['last_updated'] = datetime.now(timezone.utc).isoformat()
        self._save_notes()
        
        print(f"✅ Note ajoutée pour {symbol}: {note_type} - {content[:50]}...")
    
    def add_news_impact(self, symbol: str, news_event: str, impact_description: str, candle_data: Dict):
        """
        Ajoute une note d'impact de news sur les bougies
        
        Args:
            symbol: Symbole du marché
            news_event: Événement de news
            impact_description: Description de l'impact
            candle_data: Données de la bougie impactée
        """
        content = f"NEWS IMPACT: {news_event}\nImpact: {impact_description}\n"
        content += f"Bougie: Open={candle_data.get('open', 'N/A')}, "
        content += f"High={candle_data.get('high', 'N/A')}, "
        content += f"Low={candle_data.get('low', 'N/A')}, "
        content += f"Close={candle_data.get('close', 'N/A')}, "
        content += f"Volume={candle_data.get('volume', 'N/A')}"
        
        self.add_note(symbol, "NEWS_IMPACT", content, 4)
    
    def add_technical_observation(self, symbol: str, observation: str, timeframe: str, price_level: float = None):
        """
        Ajoute une observation technique
        
        Args:
            symbol: Symbole du marché
            observation: Description de l'observation
            timeframe: Timeframe (M15, H1, H4, etc.)
            price_level: Niveau de prix important
        """
        content = f"OBSERVATION ({timeframe}): {observation}"
        if price_level:
            content += f"\nNiveau de prix: {price_level}"
        
        self.add_note(symbol, "TECHNICAL", content, 3)
    
    def add_session_note(self, symbol: str, session_name: str, behavior: str, volatility_level: str):
        """
        Ajoute une note de session de trading
        
        Args:
            symbol: Symbole du marché
            session_name: Nom de la session (ASIE, LONDRES, OVERLAP)
            behavior: Comportement du marché
            volatility_level: Niveau de volatilité
        """
        content = f"SESSION {session_name}: {behavior}\nVolatilité: {volatility_level}"
        self.add_note(symbol, "SESSION", content, 2)
    
    def get_notes(self, symbol: str, note_type: str = None, limit: int = 10) -> List[Dict]:
        """
        Récupère les notes pour un marché
        
        Args:
            symbol: Symbole du marché
            note_type: Type de note à filtrer (optionnel)
            limit: Nombre maximum de notes à retourner
        
        Returns:
            List[Dict]: Liste des notes
        """
        if symbol not in self.notes:
            return []
        
        notes = self.notes[symbol]['notes']
        
        if note_type:
            notes = [n for n in notes if n['type'] == note_type]
        
        # Trier par date (plus récentes d'abord)
        notes.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return notes[:limit]
    
    def get_market_summary(self, symbol: str) -> Dict:
        """
        Retourne un résumé des notes pour un marché
        
        Args:
            symbol: Symbole du marché
        
        Returns:
            Dict: Résumé des notes
        """
        if symbol not in self.notes:
            return {'symbol': symbol, 'total_notes': 0, 'last_updated': None}
        
        symbol_notes = self.notes[symbol]['notes']
        
        summary = {
            'symbol': symbol,
            'total_notes': len(symbol_notes),
            'last_updated': self.notes[symbol]['last_updated'],
            'news_impacts': len([n for n in symbol_notes if n['type'] == 'NEWS_IMPACT']),
            'technical_observations': len([n for n in symbol_notes if n['type'] == 'TECHNICAL']),
            'session_notes': len([n for n in symbol_notes if n['type'] == 'SESSION']),
            'high_impact_notes': len([n for n in symbol_notes if n['impact_level'] >= 4]),
            'recent_notes': [n for n in symbol_notes if n['timestamp'] > (datetime.now(timezone.utc).timestamp() * 1000 - 86400000)]  # 24h
        }
        
        return summary
    
    def print_market_notes(self, symbol: str):
        """Affiche les notes d'un marché de manière lisible"""
        summary = self.get_market_summary(symbol)
        
        print(f"\n📊 NOTES POUR {symbol}")
        print("=" * 50)
        print(f"Total notes: {summary['total_notes']}")
        print(f"Dernière mise à jour: {summary['last_updated']}")
        print(f"Impacts news: {summary['news_impacts']}")
        print(f"Observations techniques: {summary['technical_observations']}")
        print(f"Notes de session: {summary['session_notes']}")
        print(f"Notes à fort impact: {summary['high_impact_notes']}")
        
        if summary['total_notes'] > 0:
            print(f"\n📋 Notes récentes (24h):")
            notes = self.get_notes(symbol, limit=5)
            for note in notes:
                impact_emoji = "🔴" if note['impact_level'] >= 4 else "🟡" if note['impact_level'] >= 3 else "🟢"
                print(f"  {impact_emoji} [{note['type']}] {note['content'][:80]}...")
    
    def _get_current_session(self) -> str:
        """Détermine la session de trading actuelle"""
        now = datetime.now(timezone.utc)
        hour = now.hour
        
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
    
    def export_notes(self, symbol: str = None, filename: str = None):
        """
        Exporte les notes au format JSON
        
        Args:
            symbol: Symbole à exporter (optionnel)
            filename: Nom du fichier (optionnel)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"market_notes_{timestamp}.json"
        
        data_to_export = self.notes if not symbol else {symbol: self.notes.get(symbol, {})}
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data_to_export, f, indent=2, ensure_ascii=False)
            print(f"✅ Notes exportées dans {filename}")
        except Exception as e:
            print(f"❌ Erreur export notes: {e}")

# Instance globale
_market_notes = None

def get_market_notes():
    """Retourne l'instance globale des notes de marché"""
    global _market_notes
    if _market_notes is None:
        _market_notes = MarketNotes()
    return _market_notes

# Fonctions utilitaires pour faciliter l'utilisation
def add_news_impact(symbol: str, news_event: str, impact_description: str, candle_data: Dict):
    """Ajoute une note d'impact de news"""
    notes = get_market_notes()
    notes.add_news_impact(symbol, news_event, impact_description, candle_data)

def add_technical_observation(symbol: str, observation: str, timeframe: str, price_level: float = None):
    """Ajoute une observation technique"""
    notes = get_market_notes()
    notes.add_technical_observation(symbol, observation, timeframe, price_level)

def add_session_note(symbol: str, session_name: str, behavior: str, volatility_level: str):
    """Ajoute une note de session"""
    notes = get_market_notes()
    notes.add_session_note(symbol, session_name, behavior, volatility_level)

def print_market_notes(symbol: str):
    """Affiche les notes d'un marché"""
    notes = get_market_notes()
    notes.print_market_notes(symbol)
