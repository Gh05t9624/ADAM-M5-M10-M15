# app/config/users_manager.py
import json
import os
from typing import List, Dict, Optional

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "users_config.json")

class UsersManager:
    """Gère la configuration des utilisateurs et leurs abonnements"""
    
    def __init__(self):
        self.users = []
        self.load_config()
    
    def load_config(self):
        """Charge la configuration depuis le fichier JSON"""
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.users = data.get("users", [])
            else:
                self.users = []
                self.save_config()
        except Exception as e:
            print(f"Erreur chargement config utilisateurs: {e}")
            self.users = []
    
    def save_config(self):
        """Sauvegarde la configuration dans le fichier JSON"""
        try:
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump({"users": self.users}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur sauvegarde config utilisateurs: {e}")
    
    def get_users_for_symbol(self, symbol: str) -> List[Dict]:
        """Retourne la liste des utilisateurs abonnés à un symbole"""
        matching_users = []
        
        # Retirer le suffixe 'c' pour le matching (symboles USC)
        symbol_clean = symbol.rstrip('c')
        
        for user in self.users:
            if not user.get("enabled", True):
                continue
            
            user_symbols = user.get("symbols", [])
            
            # Vérifier si l'utilisateur a ce symbole spécifique (avec ou sans 'c')
            if symbol in user_symbols or symbol_clean in user_symbols:
                matching_users.append(user)
                continue
            
            # Vérifier les wildcards (avec symbole nettoyé)
            if "FOREX" in user_symbols and not ("XAU" in symbol_clean or "GOLD" in symbol_clean):
                # L'utilisateur veut tous les Forex (pas Gold)
                matching_users.append(user)
                continue
            
            if "GOLD" in user_symbols and ("XAU" in symbol_clean or "GOLD" in symbol_clean):
                # L'utilisateur veut tous les Gold
                matching_users.append(user)
                continue
        
        return matching_users
    
    def get_all_chat_ids(self) -> List[str]:
        """Retourne tous les chat_ids actifs"""
        return [user["chat_id"] for user in self.users if user.get("enabled", True)]
    
    def add_user(self, name: str, chat_id: str, symbols: List[str], timeframes: List[str] = None) -> bool:
        """Ajoute un nouvel utilisateur"""
        if timeframes is None:
            timeframes = ["M5", "M10", "M15"]
        user_id = f"user_{len(self.users) + 1}"
        new_user = {
            "id": user_id,
            "name": name,
            "chat_id": chat_id,
            "symbols": symbols,
            "timeframes": timeframes,
            "enabled": True
        }
        self.users.append(new_user)
        self.save_config()
        return True
    
    def remove_user(self, user_id: str) -> bool:
        """Supprime un utilisateur"""
        self.users = [u for u in self.users if u["id"] != user_id]
        self.save_config()
        return True
    
    def update_user(self, user_id: str, name: str = None, chat_id: str = None, symbols: List[str] = None, timeframes: List[str] = None) -> bool:
        """Met à jour un utilisateur"""
        for user in self.users:
            if user["id"] == user_id:
                if name is not None:
                    user["name"] = name
                if chat_id is not None:
                    user["chat_id"] = chat_id
                if symbols is not None:
                    user["symbols"] = symbols
                if timeframes is not None:
                    user["timeframes"] = timeframes
                self.save_config()
                return True
        return False
    
    def update_user_symbols(self, user_id: str, symbols: List[str]) -> bool:
        """Met à jour les symboles d'un utilisateur"""
        for user in self.users:
            if user["id"] == user_id:
                user["symbols"] = symbols
                self.save_config()
                return True
        return False
    
    def enable_user(self, user_id: str, enabled: bool) -> bool:
        """Active ou désactive un utilisateur"""
        for user in self.users:
            if user["id"] == user_id:
                user["enabled"] = enabled
                self.save_config()
                return True
        return False
    
    def get_users(self) -> List[Dict]:
        """Retourne tous les utilisateurs"""
        return self.users

# Instance globale
_users_manager = None

def get_users_manager() -> UsersManager:
    """Retourne l'instance singleton du gestionnaire d'utilisateurs"""
    global _users_manager
    if _users_manager is None:
        _users_manager = UsersManager()
    return _users_manager
