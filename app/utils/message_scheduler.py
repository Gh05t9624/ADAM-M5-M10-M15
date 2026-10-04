# app/utils/message_scheduler.py

import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

class MessageScheduler:
    """Gestionnaire des intervalles de messages pour ADAM"""
    
    def __init__(self, config_path: str = "app/config/users_config.json"):
        self.config_path = config_path
        self.last_sent_times = {}  # {(user_id, symbol): datetime}
        self.load_config()
    
    def load_config(self):
        """Charge la configuration depuis users_config.json"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"Erreur chargement config: {e}")
            self.config = {"users": []}
    
    def get_user_config(self, user_id: str) -> Optional[Dict]:
        """Récupère la configuration d'un utilisateur"""
        for user in self.config.get("users", []):
            if user.get("id") == user_id:
                return user
        return None
    
    def should_send_message(self, user_id: str, symbol: str, score: int = 0) -> bool:
        """
        Détermine si un message doit être envoyé selon les règles
        
        Args:
            user_id: ID de l'utilisateur
            symbol: Symbole à analyser
            score: Score du signal (pour filtrage)
        
        Returns:
            bool: True si le message doit être envoyé
        """
        user_config = self.get_user_config(user_id)
        if not user_config:
            return False
        
        # Vérifier si l'utilisateur est activé
        if not user_config.get("enabled", False):
            return False
        
        # Vérifier le score minimum
        min_score = user_config.get("min_score_threshold", 0)
        if score < min_score:
            return False
        
        # Vérifier l'intervalle de temps
        interval_hours = user_config.get("message_interval_hours", 4)
        key = (user_id, symbol)
        
        if key not in self.last_sent_times:
            return True  # Premier message
        
        last_sent = self.last_sent_times[key]
        now = datetime.now(timezone.utc)
        
        # Vérifier si l'intervalle est écoulé
        time_diff = now - last_sent
        return time_diff >= timedelta(hours=interval_hours)
    
    def mark_message_sent(self, user_id: str, symbol: str):
        """Marque qu'un message a été envoyé"""
        key = (user_id, symbol)
        self.last_sent_times[key] = datetime.now(timezone.utc)
    
    def get_priority_symbols(self, user_id: str) -> List[str]:
        """Retourne les symboles prioritaires pour un utilisateur"""
        user_config = self.get_user_config(user_id)
        if not user_config:
            return []
        
        return user_config.get("priority_symbols", [])
    
    def get_all_symbols(self, user_id: str) -> List[str]:
        """Retourne tous les symboles pour un utilisateur"""
        user_config = self.get_user_config(user_id)
        if not user_config:
            return []
        
        return user_config.get("symbols", [])
    
    def should_prioritize_symbol(self, user_id: str, symbol: str) -> bool:
        """Vérifie si un symbole est prioritaire"""
        priority_symbols = self.get_priority_symbols(user_id)
        return symbol in priority_symbols
    
    def get_next_send_time(self, user_id: str, symbol: str) -> Optional[datetime]:
        """Retourne la prochaine heure d'envoi possible"""
        user_config = self.get_user_config(user_id)
        if not user_config:
            return None
        
        interval_hours = user_config.get("message_interval_hours", 4)
        key = (user_id, symbol)
        
        if key not in self.last_sent_times:
            return datetime.now(timezone.utc)
        
        last_sent = self.last_sent_times[key]
        return last_sent + timedelta(hours=interval_hours)
    
    def get_users_for_symbol(self, symbol: str) -> List[Dict]:
        """Retourne tous les utilisateurs configurés pour un symbole"""
        users = []
        for user in self.config.get("users", []):
            if symbol in user.get("symbols", []):
                users.append(user)
        return users
    
    def cleanup_old_records(self, days_old: int = 7):
        """Nettoie les anciens enregistrements (plus de X jours)"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=days_old)
        
        keys_to_remove = []
        for key, last_sent in self.last_sent_times.items():
            if last_sent < cutoff_time:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.last_sent_times[key]
        
        if keys_to_remove:
            print(f"Nettoyé {len(keys_to_remove)} anciens enregistrements")

# Instance globale du scheduler
_message_scheduler = None

def get_message_scheduler() -> MessageScheduler:
    """Retourne l'instance globale du scheduler"""
    global _message_scheduler
    if _message_scheduler is None:
        _message_scheduler = MessageScheduler()
    return _message_scheduler

def should_send_telegram_message(user_id: str, symbol: str, score: int = 0) -> bool:
    """
    Fonction utilitaire pour vérifier si un message Telegram doit être envoyé
    
    Args:
        user_id: ID de l'utilisateur
        symbol: Symbole à analyser
        score: Score du signal
    
    Returns:
        bool: True si le message doit être envoyé
    """
    scheduler = get_message_scheduler()
    return scheduler.should_send_message(user_id, symbol, score)

def mark_telegram_sent(user_id: str, symbol: str):
    """Marque qu'un message Telegram a été envoyé"""
    scheduler = get_message_scheduler()
    scheduler.mark_message_sent(user_id, symbol)
