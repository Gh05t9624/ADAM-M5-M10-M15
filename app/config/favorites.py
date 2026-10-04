"""
Configuration des favoris et marchés ciblés pour ADAM
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class PriorityLevel(Enum):
    """Niveaux de priorité pour les marchés"""
    CRITICAL = "critical"    # Priorité maximale, toujours analysé
    HIGH = "high"           # Haute priorité, analysé fréquemment  
    MEDIUM = "medium"       # Priorité moyenne, analysé normalement
    LOW = "low"            # Basse priorité, analysé si temps disponible
    WATCH = "watch"        # En surveillance, pas d'analyse automatique

@dataclass
class MarketFavorite:
    """Configuration d'un marché favori"""
    symbol: str
    priority: PriorityLevel
    session_focus: List[str]  # Sessions de trading optimales
    min_score: int           # Score minimum pour générer un signal
    custom_settings: Dict    # Paramètres personnalisés
    description: str         # Description du marché
    active: bool = True     # Actif/désactivé

class FavoritesManager:
    """Gestionnaire des favoris et marchés ciblés"""
    
    def __init__(self):
        self.favorites: Dict[str, MarketFavorite] = {}
        self.load_default_favorites()
    
    def load_default_favorites(self):
        """Charger les favoris par défaut"""
        
        # Marchés critiques - toujours analysés
        self.favorites["EURUSD"] = MarketFavorite(
            symbol="EURUSD",
            priority=PriorityLevel.CRITICAL,
            session_focus=["London", "New York"],
            min_score=75,
            custom_settings={
                "timeframes": ["M5", "M15", "M10"],
                "volume_threshold": 1.2,
                "spread_limit": 3,
                "volatility_filter": True
            },
            description="Euro/Dollar - Le plus liquide"
        )
        
        self.favorites["GBPUSD"] = MarketFavorite(
            symbol="GBPUSD", 
            priority=PriorityLevel.CRITICAL,
            session_focus=["London", "New York"],
            min_score=70,
            custom_settings={
                "timeframes": ["M5", "M15", "M10"],
                "volume_threshold": 1.3,
                "spread_limit": 4,
                "volatility_filter": True,
                "news_sensitivity": "high"
            },
            description="Livre/Dollar - Volatile et réactif"
        )
        
        self.favorites["USDJPY"] = MarketFavorite(
            symbol="USDJPY",
            priority=PriorityLevel.HIGH,
            session_focus=["Tokyo", "London", "New York"], 
            min_score=70,
            custom_settings={
                "timeframes": ["M15", "M5", "M10"],
                "volume_threshold": 1.1,
                "spread_limit": 2,
                "safe_haven_mode": True
            },
            description="Dollar/Yen - Valeur refuge"
        )
        
        # Marchés exotiques - haute priorité
        self.favorites["EURJPY"] = MarketFavorite(
            symbol="EURJPY",
            priority=PriorityLevel.HIGH,
            session_focus=["Tokyo", "London"],
            min_score=72,
            custom_settings={
                "timeframes": ["M15", "M5", "M10"],
                "volume_threshold": 1.25,
                "spread_limit": 5,
                "cross_pair_optimization": True
            },
            description="Euro/Yen - Croisé populaire"
        )
        
        self.favorites["GBPJPY"] = MarketFavorite(
            symbol="GBPJPY",
            priority=PriorityLevel.HIGH,
            session_focus=["London", "Tokyo"],
            min_score=68,
            custom_settings={
                "timeframes": ["M5", "M15", "M10"],
                "volume_threshold": 1.4,
                "spread_limit": 8,
                "high_volatility_mode": True,
                "extended_hours": True
            },
            description="Livre/Yen - Très volatile"
        )
        
        # Matières premières - haute priorité
        self.favorites["XAUUSD"] = MarketFavorite(
            symbol="XAUUSD",
            priority=PriorityLevel.HIGH,
            session_focus=["New York", "London", "Tokyo"],
            min_score=75,
            custom_settings={
                "timeframes": ["M15", "M5", "M10"],
                "commodity_mode": True,
                "safe_haven_mode": True,
                "volume_threshold": 1.3,
                "spread_limit": 50,
                "news_sensitivity": "very_high"
            },
            description="Or - Valeur refuge par excellence"
        )
        
        self.favorites["US30"] = MarketFavorite(
            symbol="US30",
            priority=PriorityLevel.MEDIUM,
            session_focus=["New York"],
            min_score=70,
            custom_settings={
                "timeframes": ["M15", "M5", "M10"],
                "index_mode": True,
                "market_hours": "US",
                "volume_threshold": 1.2,
                "spread_limit": 5
            },
            description="Dow Jones - Indice américain"
        )
        
        # Marchés secondaires
        self.favorites["AUDUSD"] = MarketFavorite(
            symbol="AUDUSD",
            priority=PriorityLevel.MEDIUM,
            session_focus=["Tokyo", "Sydney"],
            min_score=65,
            custom_settings={
                "timeframes": ["M15", "M5"],
                "commodity_currency": True,
                "volume_threshold": 1.1,
                "spread_limit": 3
            },
            description="Dollar Australien - Devise commodity"
        )
        
        self.favorites["USDCAD"] = MarketFavorite(
            symbol="USDCAD",
            priority=PriorityLevel.MEDIUM,
            session_focus=["New York", "Toronto"],
            min_score=65,
            custom_settings={
                "timeframes": ["M15", "M5"],
                "commodity_currency": True,
                "volume_threshold": 1.0,
                "spread_limit": 4
            },
            description="Dollar Canadien - Pétro-dollar"
        )
        
        # Marchés en surveillance
        self.favorites["NZDUSD"] = MarketFavorite(
            symbol="NZDUSD",
            priority=PriorityLevel.WATCH,
            session_focus=["Sydney", "Tokyo"],
            min_score=60,
            custom_settings={
                "timeframes": ["M5", "M10"],
                "volume_threshold": 0.9,
                "spread_limit": 5
            },
            description="Dollar Néo-Zélandais - En surveillance"
        )
    
    def get_active_favorites(self) -> List[MarketFavorite]:
        """Récupérer les favoris actifs triés par priorité"""
        active = [fav for fav in self.favorites.values() if fav.active]
        
        # Trier par priorité
        priority_order = {
            PriorityLevel.CRITICAL: 0,
            PriorityLevel.HIGH: 1, 
            PriorityLevel.MEDIUM: 2,
            PriorityLevel.LOW: 3,
            PriorityLevel.WATCH: 4
        }
        
        return sorted(active, key=lambda x: priority_order[x.priority])
    
    def get_symbols_by_priority(self, priority: PriorityLevel) -> List[str]:
        """Récupérer les symboles par niveau de priorité"""
        return [fav.symbol for fav in self.favorites.values() 
                if fav.priority == priority and fav.active]
    
    def get_favorite(self, symbol: str) -> Optional[MarketFavorite]:
        """Récupérer un favori par symbole"""
        return self.favorites.get(symbol)
    
    def add_favorite(self, favorite: MarketFavorite):
        """Ajouter un nouveau favori"""
        self.favorites[favorite.symbol] = favorite
    
    def update_favorite(self, symbol: str, **kwargs):
        """Mettre à jour un favori"""
        if symbol in self.favorites:
            favorite = self.favorites[symbol]
            for key, value in kwargs.items():
                if hasattr(favorite, key):
                    setattr(favorite, key, value)
    
    def toggle_favorite(self, symbol: str) -> bool:
        """Activer/désactiver un favori"""
        if symbol in self.favorites:
            self.favorites[symbol].active = not self.favorites[symbol].active
            return self.favorites[symbol].active
        return False
    
    def get_session_favorites(self, current_session: str) -> List[MarketFavorite]:
        """Récupérer les favoris optimisés pour la session actuelle"""
        return [fav for fav in self.get_active_favorites() 
                if current_session in fav.session_focus]
    
    def get_critical_symbols(self) -> List[str]:
        """Symboles critiques toujours analysés"""
        return self.get_symbols_by_priority(PriorityLevel.CRITICAL)
    
    def should_analyze_symbol(self, symbol: str, current_session: str, 
                            available_time: bool = True) -> bool:
        """Déterminer si un symbole doit être analysé maintenant"""
        favorite = self.get_favorite(symbol)
        if not favorite or not favorite.active:
            return False
        
        # Vérifier la session
        if current_session not in favorite.session_focus:
            return False
        
        # Priorité critique = toujours
        if favorite.priority == PriorityLevel.CRITICAL:
            return True
        
        # Priorité haute = si temps disponible
        if favorite.priority == PriorityLevel.HIGH:
            return available_time
        
        # Autres priorités = selon disponibilité
        return available_time and favorite.priority in [PriorityLevel.MEDIUM, PriorityLevel.LOW]
    
    def get_custom_settings(self, symbol: str) -> Dict:
        """Récupérer les paramètres personnalisés pour un symbole"""
        favorite = self.get_favorite(symbol)
        return favorite.custom_settings if favorite else {}
    
    def export_favorites(self) -> Dict:
        """Exporter la configuration des favoris"""
        return {
            symbol: {
                "priority": fav.priority.value,
                "session_focus": fav.session_focus,
                "min_score": fav.min_score,
                "custom_settings": fav.custom_settings,
                "description": fav.description,
                "active": fav.active
            }
            for symbol, fav in self.favorites.items()
        }
    
    def import_favorites(self, favorites_data: Dict):
        """Importer une configuration de favoris"""
        for symbol, data in favorites_data.items():
            try:
                favorite = MarketFavorite(
                    symbol=symbol,
                    priority=PriorityLevel(data["priority"]),
                    session_focus=data["session_focus"],
                    min_score=data["min_score"],
                    custom_settings=data["custom_settings"],
                    description=data["description"],
                    active=data.get("active", True)
                )
                self.favorites[symbol] = favorite
            except (KeyError, ValueError) as e:
                print(f"Erreur import favori {symbol}: {e}")

# Instance globale du gestionnaire de favoris
favorites_manager = FavoritesManager()
