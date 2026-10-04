# app/engine/mt5_news_provider.py

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import time

class MT5NewsProvider:
    """
    Fournisseur de données de news économiques depuis MT5
    Explore les API disponibles pour les événements économiques
    """
    
    def __init__(self):
        self.is_connected = False
        self.available_symbols = []
        self.news_cache = {}
        
    def initialize(self):
        """Initialise la connexion MT5 et explore les capacités de news"""
        try:
            # Vérifier si MT5 est connecté
            if not mt5.initialize():
                print("❌ MT5NewsProvider: Échec d'initialisation MT5")
                return False
            
            self.is_connected = True
            print("✅ MT5NewsProvider: Connexion MT5 établie")
            
            # Explorer les symboles disponibles
            self._explore_available_symbols()
            
            # Explorer les fonctions de news disponibles
            self._explore_news_functions()
            
            return True
            
        except Exception as e:
            print(f"❌ MT5NewsProvider: Erreur d'initialisation: {e}")
            return False
    
    def _explore_available_symbols(self):
        """Explore les symboles disponibles sur MT5"""
        try:
            # Obtenir tous les symboles
            symbols = mt5.symbols_get()
            
            if symbols:
                self.available_symbols = [s.name for s in symbols if s.name]
                print(f"📊 MT5NewsProvider: {len(self.available_symbols)} symboles trouvés")
                
                # Afficher quelques exemples
                sample_symbols = self.available_symbols[:10]
                print(f"   Exemples: {sample_symbols}")
            else:
                print("⚠️ MT5NewsProvider: Aucun symbole trouvé")
                
        except Exception as e:
            print(f"❌ MT5NewsProvider: Erreur exploration symboles: {e}")
    
    def _explore_news_functions(self):
        """Explore les fonctions de news disponibles dans MT5"""
        try:
            print("🔍 MT5NewsProvider: Exploration des fonctions de news...")
            
            # Vérifier si les fonctions de calendar/news existent
            news_functions = []
            
            # Fonctions potentielles à explorer
            potential_functions = [
                'calendar_get',
                'calendar_get_by_event', 
                'calendar_get_by_symbol',
                'calendar_get_by_timerange',
                'economic_calendar_get',
                'economic_calendar_get_by_symbol',
                'news_get',
                'news_get_by_symbol',
                'news_get_by_timerange'
            ]
            
            for func_name in potential_functions:
                if hasattr(mt5, func_name):
                    news_functions.append(func_name)
                    print(f"   ✅ {func_name}: Disponible")
                else:
                    print(f"   ❌ {func_name}: Non disponible")
            
            if news_functions:
                print(f"📰 MT5NewsProvider: {len(news_functions)} fonctions de news trouvées")
            else:
                print("⚠️ MT5NewsProvider: Aucune fonction de news trouvée")
                
        except Exception as e:
            print(f"❌ MT5NewsProvider: Erreur exploration fonctions: {e}")
    
    
    def _analyze_function_result(self, result, func_name):
        """Analyse le résultat d'une fonction de news"""
        try:
            if isinstance(result, list):
                print(f"   📊 {func_name}: {len(result)} événements trouvés")
                
                if result:
                    # Analyser le premier événement
                    first_event = result[0]
                    if hasattr(first_event, '__dict__'):
                        event_dict = first_event.__dict__
                        print(f"   📋 Premier événement: {event_dict}")
                        
                        # Extraire les champs importants
                        important_fields = ['time', 'event', 'impact', 'currency', 'actual', 'forecast', 'previous']
                        for field in important_fields:
                            if field in event_dict:
                                print(f"      {field}: {event_dict[field]}")
                    
            elif isinstance(result, dict):
                print(f"   📋 {func_name}: Dictionnaire retourné")
                for key, value in result.items():
                    print(f"      {key}: {value}")
                    
            elif result is not None:
                print(f"   ✅ {func_name}: Résultat de type {type(result)}")
                print(f"   📄 Contenu: {result}")
                
        except Exception as e:
            print(f"   ❌ Erreur analyse résultat: {e}")
    
    def get_economic_calendar(self, symbol=None, days_back=7):
        """
        Récupère le calendrier économique depuis MT5
        
        Args:
            symbol: Symbole spécifique (optionnel)
            days_back: Nombre de jours à regarder en arrière
            
        Returns:
            list: Événements économiques
        """
        if not self.is_connected:
            if not self.initialize():
                return []
        
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days_back)
            
            print(f"📅 Récupération calendrier économique: {start_time} à {end_time}")
            
            # Essayer différentes fonctions de calendar
            calendar_events = []
            
            # Méthode 1: calendar_get_by_timerange
            if hasattr(mt5, 'calendar_get_by_timerange'):
                try:
                    events = mt5.calendar_get_by_timerange(start_time, end_time)
                    if events:
                        calendar_events.extend(events)
                        print(f"   ✅ {len(events)} événements via calendar_get_by_timerange")
                except Exception as e:
                    print(f"   ❌ Erreur calendar_get_by_timerange: {e}")
            
            # Méthode 2: economic_calendar_get
            if hasattr(mt5, 'economic_calendar_get'):
                try:
                    events = mt5.economic_calendar_get()
                    if events:
                        # Filtrer par date
                        filtered_events = [e for e in events if hasattr(e, 'time') and start_time <= e.time <= end_time]
                        calendar_events.extend(filtered_events)
                        print(f"   ✅ {len(filtered_events)} événements via economic_calendar_get")
                except Exception as e:
                    print(f"   ❌ Erreur economic_calendar_get: {e}")
            
            # Filtrer par symbole si spécifié
            if symbol and calendar_events:
                filtered_by_symbol = []
                for event in calendar_events:
                    if hasattr(event, 'currency') and symbol:
                        # Extraire la devise du symbole
                        if 'USD' in symbol and hasattr(event, 'currency'):
                            if 'USD' in str(event.currency):
                                filtered_by_symbol.append(event)
                        elif 'EUR' in symbol and hasattr(event, 'currency'):
                            if 'EUR' in str(event.currency):
                                filtered_by_symbol.append(event)
                        else:
                            filtered_by_symbol.append(event)
                
                calendar_events = filtered_by_symbol
                print(f"   📊 {len(calendar_events)} événements pour {symbol}")
            
            # Mettre en cache
            cache_key = f"{symbol or 'ALL'}_{start_time.date()}_{end_time.date()}"
            self.news_cache[cache_key] = calendar_events
            
            return calendar_events
            
        except Exception as e:
            print(f"❌ Erreur récupération calendrier: {e}")
            return []
    
    def get_news_events(self, symbol=None, hours_back=24):
        """
        Récupère les news depuis MT5
        
        Args:
            symbol: Symbole spécifique (optionnel)
            hours_back: Nombre d'heures à regarder en arrière
            
        Returns:
            list: Événements de news
        """
        if not self.is_connected:
            if not self.initialize():
                return []
        
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours_back)
            
            print(f"📰 Récupération news: {start_time} à {end_time}")
            
            news_events = []
            
            # Essayer différentes fonctions de news
            if hasattr(mt5, 'news_get_by_timerange'):
                try:
                    events = mt5.news_get_by_timerange(start_time, end_time)
                    if events:
                        news_events.extend(events)
                        print(f"   ✅ {len(events)} news via news_get_by_timerange")
                except Exception as e:
                    print(f"   ❌ Erreur news_get_by_timerange: {e}")
            
            # Filtrer par symbole si spécifié
            if symbol and news_events:
                filtered_by_symbol = []
                for event in news_events:
                    if hasattr(event, 'currency') and symbol:
                        # Même logique de filtrage que pour calendar
                        if 'USD' in symbol and hasattr(event, 'currency'):
                            if 'USD' in str(event.currency):
                                filtered_by_symbol.append(event)
                        elif 'EUR' in symbol and hasattr(event, 'currency'):
                            if 'EUR' in str(event.currency):
                                filtered_by_symbol.append(event)
                        else:
                            filtered_by_symbol.append(event)
                
                news_events = filtered_by_symbol
                print(f"   📊 {len(news_events)} news pour {symbol}")
            
            return news_events
            
        except Exception as e:
            print(f"❌ Erreur récupération news: {e}")
            return []
    
    def get_news_summary(self, symbol=None):
        """Retourne un résumé des news disponibles"""
        if not self.is_connected:
            return "❌ MT5 non connecté"
        
        # Essayer de récupérer les news récentes
        news_events = self.get_news_events(symbol, hours_back=24)
        calendar_events = self.get_economic_calendar(symbol, days_back=7)
        
        summary = f"""
📰 MT5 News Provider Summary
├─ Connexion: {'✅ Connecté' if self.is_connected else '❌ Déconnecté'}
├─ Symboles: {len(self.available_symbols)} disponibles
├─ News récentes: {len(news_events)} événements
├─ Calendrier: {len(calendar_events)} événements
└─ Dernière mise à jour: {datetime.now().strftime('%H:%M:%S UTC')}
        """.strip()
        
        if news_events:
            summary += f"\n\n📋 Dernières news pour {symbol or 'TOUS'}:"
            for i, event in enumerate(news_events[:5]):  # Top 5
                if hasattr(event, '__dict__'):
                    event_info = event.__dict__
                    time_str = str(event_info.get('time', 'N/A'))
                    event_name = str(event_info.get('event', 'N/A'))
                    impact = str(event_info.get('impact', 'N/A'))
                    summary += f"\n   {i+1}. {time_str} - {event_name} ({impact})"
        
        return summary
    
    def shutdown(self):
        """Ferme la connexion MT5"""
        if self.is_connected:
            mt5.shutdown()
            self.is_connected = False
            print("✅ MT5NewsProvider: Connexion fermée")


# Instance globale du provider
_mt5_news_provider = None

def get_mt5_news_provider():
    """Retourne l'instance globale du provider MT5"""
    global _mt5_news_provider
    if _mt5_news_provider is None:
        _mt5_news_provider = MT5NewsProvider()
    return _mt5_news_provider


# Exemple d'utilisation
