# app/utils/news_sharing.py

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class NewsSharingService:
    """
    Service de partage des news économiques sur Telegram
    Formatage professionnel et envoi automatisé
    """
    
    def __init__(self, bot_token: str, news_channel_id: str):
        self.bot_token = bot_token
        self.news_channel_id = news_channel_id
        self.shared_news = {}
        
    def format_news_message(self, news_event, symbol=None):
        """
        Formate un événement de news en message Telegram professionnel
        
        Args:
            news_event: Événement de news (dict ou objet MT5)
            symbol: Symbole optionnel pour personnalisation
        
        Returns:
            str: Message formaté pour Telegram
        """
        # Charger la configuration de branding
        try:
            from app.utils.news_channel_manager import get_news_channel_manager
            manager = get_news_channel_manager()
            formatting_config = manager.get_formatting_options()
            source_name = formatting_config.get('source_name', 'ADAM Intelligence Network')
            hide_technical = formatting_config.get('hide_technical_source', True)
        except:
            source_name = 'ADAM Intelligence Network'
            hide_technical = True
        
        # Extraire les informations de l'événement
        if hasattr(news_event, '__dict__'):
            event_data = news_event.__dict__
        else:
            event_data = news_event
        
        # Informations essentielles
        event_time = event_data.get('time', 'N/A')
        event_name = event_data.get('event', 'N/A')
        event_currency = event_data.get('currency', 'N/A')
        event_impact = event_data.get('impact', 'N/A')
        event_actual = event_data.get('actual', 'N/A')
        event_forecast = event_data.get('forecast', 'N/A')
        event_previous = event_data.get('previous', 'N/A')
        
        # Formater l'heure
        if isinstance(event_time, datetime):
            time_str = event_time.strftime('%H:%M UTC')
            date_str = event_time.strftime('%d/%m/%Y')
        else:
            time_str = str(event_time)
            date_str = 'N/A'
        
        # Déterminer l'emoji d'impact
        impact_emoji = self._get_impact_emoji(event_impact)
        
        # Déterminer l'emoji de devise
        currency_emoji = self._get_currency_emoji(event_currency)
        
        # Formater les valeurs numériques
        actual_str = self._format_number(event_actual)
        forecast_str = self._format_number(event_forecast)
        previous_str = self._format_number(event_previous)
        
        # Construire le message
        message = f"""
📰 *ADAM — ECONOMIC NEWS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 *{date_str}* | *{time_str}* | {currency_emoji}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 *ÉVÉNEMENT*
{impact_emoji} **{event_name}**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 *DONNÉES*
• **Réel** : {actual_str}
• **Prévision** : {forecast_str}
• **Précédent** : {previous_str}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 *IMPACT* : {event_impact}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ *ANALYSE ADAM*
{self._get_market_analysis(event_name, event_currency)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 *Source*: {source_name}
⏰ *Généré*: {datetime.utcnow().strftime('%H:%M:%S UTC')}
        """.strip()
        
        return message
    
    def _get_impact_emoji(self, impact):
        """Retourne l'emoji approprié pour l'impact"""
        impact_map = {
            'HIGH': '🔴',
            'MEDIUM': '🟡', 
            'LOW': '🟢',
            'HIGH_IMPACT': '🔴',
            'MEDIUM_IMPACT': '🟡',
            'LOW_IMPACT': '🟢'
        }
        return impact_map.get(impact.upper(), '⚪')
    
    def _get_currency_emoji(self, currency):
        """Retourne l'emoji approprié pour la devise"""
        currency_map = {
            'USD': '🇺🇸',
            'EUR': '🇪🇺',
            'GBP': '🇬🇧',
            'JPY': '🇯🇵',
            'CHF': '🇨🇭',
            'CAD': '🇨🇦',
            'AUD': '🇦🇺',
            'NZD': '🇳🇿',
            'CNY': '🇨🇳',
            'GOLD': '🥇',
            'XAU': '🥇',
            'BTC': '₿',
            'ETH': 'Ξ'
        }
        return currency_map.get(currency.upper(), '💱')
    
    def _format_number(self, value):
        """Formate un nombre pour l'affichage"""
        if value == 'N/A' or value is None:
            return 'N/A'
        
        try:
            # Si c'est un nombre décimal
            if isinstance(value, (int, float)):
                if isinstance(value, float):
                    return f"{value:.2f}"
                else:
                    return f"{value:,}"
            else:
                return str(value)
        except:
            return str(value)
    
    def _get_market_analysis(self, event_name, currency):
        """Génère une analyse de marché pour l'événement"""
        analyses = []
        
        # Analyse selon le type d'événement
        if 'NFP' in event_name.upper():
            analyses.extend([
                "📊 Impact attendu sur USDJPY, GBPUSD, EURUSD",
                "📈 Volatilité accrue sur les paires USD",
                "⚠️ Éviter les trades 30min avant/après",
                "🎯 Opportunités sur les breakouts de range"
            ])
        elif 'CPI' in event_name.upper():
            analyses.extend([
                "📊 Impact sur toutes les paires USD",
                "📈 Tendance inflationiste possible",
                "⚠️ Volatilité sur les métaux précieux",
                "🎯 Surveiller XAUUSD et XAGUSD"
            ])
        elif 'FOMC' in event_name.upper():
            analyses.extend([
                "📊 Impact majeur sur USD",
                "📈 Décisions de taux direct",
                "⚠️ Forte volatilité attendue",
                "🎯 Positionnement sur les indices US"
            ])
        elif 'GDP' in event_name.upper():
            analyses.extend([
                "📊 Indicateur de santé économique",
                "📈 Impact sur la devise nationale",
                "⚠️ Mouvements tendanciels possibles",
                "🎯 Confirmation des tendances en cours"
            ])
        else:
            analyses.extend([
                "📊 Surveillance des réactions de marché",
                "📈 Analyse de l'impact sur les paires concernées",
                "⚠️ Adaptation de la stratégie selon impact",
                "🎯 Opportunités sur les corrections techniques"
            ])
        
        # Ajouter des analyses spécifiques à la devise
        if currency:
            if 'USD' in currency.upper():
                analyses.append("💵 Focus particulier sur les paires USD")
            elif 'EUR' in currency.upper():
                analyses.append("💶 Impact potentiel sur EUR/USD")
            elif 'GOLD' in currency.upper() or 'XAU' in currency.upper():
                analyses.append("🥇 Réaction attendue sur l'or")
        
        return '\n'.join(f"• {analysis}" for analysis in analyses[:5])
    
    def send_news_to_channel(self, news_events, symbol=None):
        """
        Envoie les news formatées au canal Telegram
        
        Args:
            news_events: Liste des événements de news
            symbol: Symbole optionnel pour filtrage
        
        Returns:
            int: Nombre de messages envoyés avec succès
        """
        if not news_events:
            print("⚠️ Aucune news à partager")
            return 0
        
        success_count = 0
        
        for event in news_events:
            try:
                # Formater le message
                message = self.format_news_message(event, symbol)
                
                # Envoyer à Telegram
                url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                data = {
                    'chat_id': self.news_channel_id,
                    'text': message,
                    'parse_mode': 'Markdown',
                    'disable_web_page_preview': True
                }
                
                response = requests.post(url, data=data, timeout=10)
                
                if response.status_code == 200:
                    success_count += 1
                    print(f"✅ News envoyée: {event.get('event', 'N/A')}")
                else:
                    print(f"❌ Erreur envoi news: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Erreur formatage/envoi news: {e}")
        
        return success_count
    
    def send_news_summary(self, symbol=None, hours_back=24):
        """
        Envoie un résumé des news récentes
        
        Args:
            symbol: Symbole optionnel pour filtrage
            hours_back: Nombre d'heures à regarder en arrière
        
        Returns:
            bool: Succès de l'envoi
        """
        try:
            # Import du provider MT5
            from app.engine.mt5_news_provider import get_mt5_news_provider
            
            provider = get_mt5_news_provider()
            if provider.initialize():
                # Obtenir les news récentes
                news_events = provider.get_news_events(symbol, hours_back=hours_back)
                
                if news_events:
                    # Créer un message de résumé
                    summary_message = self._create_summary_message(news_events, symbol, hours_back)
                    
                    # Envoyer le résumé
                    url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                    data = {
                        'chat_id': self.news_channel_id,
                        'text': summary_message,
                        'parse_mode': 'Markdown',
                        'disable_web_page_preview': True
                    }
                    
                    response = requests.post(url, data=data, timeout=10)
                    
                    if response.status_code == 200:
                        print(f"✅ Résumé news envoyé: {len(news_events)} événements")
                        return True
                    else:
                        print(f"❌ Erreur envoi résumé: {response.status_code}")
                        return False
                else:
                    print("ℹ️ Aucune news récente à résumer")
                    return True
            else:
                print("❌ Impossible d'initialiser le provider MT5")
                return False
                
        except Exception as e:
            print(f"❌ Erreur envoi résumé news: {e}")
            return False
    
    def _create_summary_message(self, news_events, symbol=None, hours_back=24):
        """Crée un message de résumé des news"""
        if not news_events:
            return "ℹ️ Aucune news économique récente"
        
        # Grouper par impact
        high_impact = [e for e in news_events if str(e.get('impact', '')).upper() in ['HIGH', 'HIGH_IMPACT']]
        medium_impact = [e for e in news_events if str(e.get('impact', '')).upper() in ['MEDIUM', 'MEDIUM_IMPACT']]
        low_impact = [e for e in news_events if str(e.get('impact', '')).upper() in ['LOW', 'LOW_IMPACT']]
        
        # Créer le résumé
        summary = f"""
📊 *ADAM — NEWS SUMMARY*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 *Période*: {hours_back} dernières heures
📈 *Total*: {len(news_events)} événements
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 *HAUT IMPACT*: {len(high_impact)} événements
🟡 *MOYEN IMPACT*: {len(medium_impact)} événements
🟢 *FAIBLE IMPACT*: {len(low_impact)} événements
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        # Ajouter les détails des événements importants
        important_events = high_impact + medium_impact[:2]  # Top 5
        
        if important_events:
            summary += "\n📋 *ÉVÉNEMENTS IMPORTANTS*:\n"
            for i, event in enumerate(important_events, 1):
                if hasattr(event, '__dict__'):
                    event_data = event.__dict__
                else:
                    event_data = event
                
                event_time = event_data.get('time', 'N/A')
                event_name = event_data.get('event', 'N/A')
                event_impact = event_data.get('impact', 'N/A')
                
                if isinstance(event_time, datetime):
                    time_str = event_time.strftime('%H:%M')
                else:
                    time_str = str(event_time)
                
                impact_emoji = self._get_impact_emoji(event_impact)
                
                summary += f"{i}. **{time_str}** - {impact_emoji} {event_name}\n"
        
        summary += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 *Source*: {source_name}
⏰ *Généré*: {datetime.utcnow().strftime('%H:%M:%S UTC')}
        """.strip()
        
        return summary


# Instance globale du service
_news_sharing_service = None

def get_news_sharing_service(bot_token=None, news_channel_id=None):
    """Retourne l'instance globale du service de partage de news"""
    global _news_sharing_service
    if _news_sharing_service is None:
        # Essayer de charger depuis le gestionnaire de canal
        try:
            from app.utils.news_channel_manager import get_news_channel_manager
            channel_manager = get_news_channel_manager()
            
            if bot_token is None:
                bot_token = channel_manager.get_bot_token()
            
            if news_channel_id is None:
                news_channel_id = channel_manager.get_news_channel_id()
                
            print(f"📰 Service news initialisé avec canal: {news_channel_id}")
            
        except ImportError:
            # Fallback vers valeurs par défaut
            if bot_token is None:
                bot_token = "8543784444:AAGLiduK-VBy3tbuYYJTOFrckODtot4BnRE"  # Token ADAM
            
            if news_channel_id is None:
                news_channel_id = "-1003795293095"  # Canal A.D.A.M (temporaire)
            
            print("⚠️ Utilisation configuration par défaut pour le service news")
        
        _news_sharing_service = NewsSharingService(bot_token, news_channel_id)
    
    return _news_sharing_service
