# app/utils/news_channel_manager.py

import json
import os
from datetime import datetime
from typing import Optional, Dict, List

class NewsChannelManager:
    """
    Gestionnaire des canaux Telegram pour les news économiques
    Séparation des news et des signaux de trading
    """
    
    def __init__(self, config_path: str = "app/config/news_config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Charge la configuration des news"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Fichier de configuration {self.config_path} non trouvé")
            return self.get_default_config()
        except Exception as e:
            print(f"❌ Erreur chargement configuration news: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Retourne la configuration par défaut"""
        return {
            "news_service": {
                "enabled": True,
                "bot_token": "8543784444:AAGLiduK-VBy3tbuYYJTOFrckODtot4BnRE",
                "news_channel_id": "-1003795293095",  # Canal A.D.A.M temporaire
                "news_channel_name": "ADAM Economic News",
                "sharing_interval_hours": 1,
                "max_news_per_message": 5,
                "include_analysis": True,
                "include_market_impact": True,
                "filter_by_impact": ["HIGH", "MEDIUM"],
                "filter_by_currency": ["USD", "EUR", "GBP", "JPY"],
                "time_format": "UTC",
                "language": "FR",
                "auto_share": {
                    "enabled": True,
                    "share_immediately": True,
                    "share_summary_daily": True,
                    "summary_time_utc": "22:00"
                },
                "formatting": {
                    "use_emojis": True,
                    "use_markdown": True,
                    "include_source": True,
                    "include_timestamp": True,
                    "compact_mode": False
                },
                "filters": {
                    "min_impact_level": "MEDIUM",
                    "exclude_weekends": False,
                    "include_forex_only": False,
                    "include_crypto": True,
                    "include_metals": True
                }
            }
        }
    
    def save_config(self):
        """Sauvegarde la configuration"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"✅ Configuration news sauvegardée dans {self.config_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde configuration news: {e}")
            return False
    
    def get_news_channel_id(self) -> str:
        """Retourne l'ID du canal de news"""
        return self.config.get("news_service", {}).get("news_channel_id", "-1003795293095")
    
    def get_bot_token(self) -> str:
        """Retourne le token du bot"""
        return self.config.get("news_service", {}).get("bot_token", "8543784444:AAGLiduK-VBy3tbuYYJTOFrckODtot4BnRE")
    
    def is_enabled(self) -> bool:
        """Vérifie si le service de news est activé"""
        return self.config.get("news_service", {}).get("enabled", True)
    
    def get_sharing_interval(self) -> int:
        """Retourne l'intervalle de partage en heures"""
        return self.config.get("news_service", {}).get("sharing_interval_hours", 1)
    
    def get_max_news_per_message(self) -> int:
        """Retourne le nombre maximum de news par message"""
        return self.config.get("news_service", {}).get("max_news_per_message", 5)
    
    def get_filter_by_impact(self) -> List[str]:
        """Retourne la liste des niveaux d'impact à filtrer"""
        return self.config.get("news_service", {}).get("filter_by_impact", ["HIGH", "MEDIUM"])
    
    def get_filter_by_currency(self) -> List[str]:
        """Retourne la liste des devises à filtrer"""
        return self.config.get("news_service", {}).get("filter_by_currency", ["USD", "EUR", "GBP", "JPY"])
    
    def update_news_channel(self, channel_id: str, channel_name: str = None):
        """
        Met à jour l'ID du canal de news
        
        Args:
            channel_id: ID du nouveau canal (ex: "-1001234567890")
            channel_name: Nom du canal (optionnel)
        """
        if "news_service" not in self.config:
            self.config["news_service"] = {}
        
        self.config["news_service"]["news_channel_id"] = channel_id
        
        if channel_name:
            self.config["news_service"]["news_channel_name"] = channel_name
        
        # Sauvegarder la configuration
        if self.save_config():
            print(f"✅ Canal de news mis à jour: {channel_name or channel_id}")
            return True
        else:
            print(f"❌ Erreur mise à jour canal de news")
            return False
    
    def get_channel_info(self) -> Dict:
        """Retourne les informations du canal de news"""
        news_config = self.config.get("news_service", {})
        return {
            "channel_id": news_config.get("news_channel_id"),
            "channel_name": news_config.get("news_channel_name", "ADAM Economic News"),
            "enabled": news_config.get("enabled", True),
            "sharing_interval": news_config.get("sharing_interval_hours", 1),
            "max_news_per_message": news_config.get("max_news_per_message", 5),
            "auto_share": news_config.get("auto_share", {}).get("enabled", True),
            "summary_time": news_config.get("auto_share", {}).get("summary_time_utc", "22:00")
        }
    
    def should_share_now(self) -> bool:
        """Détermine si les news doivent être partagées maintenant"""
        if not self.is_enabled():
            return False
        
        auto_share = self.config.get("news_service", {}).get("auto_share", {})
        if not auto_share.get("enabled", True):
            return False
        
        if auto_share.get("share_immediately", True):
            return True
        
        # Vérifier si c'est l'heure du résumé quotidien
        summary_time = auto_share.get("summary_time_utc", "22:00")
        current_time = datetime.utcnow().strftime("%H:%M")
        
        return current_time == summary_time
    
    def get_formatting_options(self) -> Dict:
        """Retourne les options de formatage"""
        return self.config.get("news_service", {}).get("formatting", {})
    
    def get_filters(self) -> Dict:
        """Retourne les filtres de news"""
        return self.config.get("news_service", {}).get("filters", {})
    
    def print_config_summary(self):
        """Affiche un résumé de la configuration"""
        channel_info = self.get_channel_info()
        formatting = self.get_formatting_options()
        filters = self.get_filters()
        
        print(f"""
📰 CONFIGURATION CANAL NEWS ADAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📡 Canal: {channel_info['channel_name']} ({channel_info['channel_id']})
🔴 Actif: {'OUI' if channel_info['enabled'] else 'NON'}
⏰ Intervalle: {channel_info['sharing_interval']} heures
📊 Max news/message: {channel_info['max_news_per_message']}
🔄 Auto-partage: {'OUI' if channel_info['auto_share'] else 'NON'}
📋 Heure résumé: {channel_info['summary_time']} UTC
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨 Formatage: {'OUI' if formatting.get('use_emojis') else 'NON'} emojis
📝 Markdown: {'OUI' if formatting.get('use_markdown') else 'NON'}
🕐 Timestamp: {'OUI' if formatting.get('include_timestamp') else 'NON'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Impact minimum: {filters.get('min_impact_level', 'MEDIUM')}
💱 Devises: {', '.join(filters.get('filter_by_currency', ['USD', 'EUR']))}
🥇 Métaux: {'OUI' if filters.get('include_metals') else 'NON'}
₿ Crypto: {'OUI' if filters.get('include_crypto') else 'NON'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """.strip())


# Instance globale du gestionnaire
_news_channel_manager = None

def get_news_channel_manager():
    """Retourne l'instance globale du gestionnaire de canal de news"""
    global _news_channel_manager
    if _news_channel_manager is None:
        _news_channel_manager = NewsChannelManager()
    return _news_channel_manager


