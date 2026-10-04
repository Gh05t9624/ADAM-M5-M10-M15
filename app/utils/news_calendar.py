# app/utils/news_calendar.py
# Calendrier des moments de news pour l'analyse technique

import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

class NewsCalendar:
    """
    Calendrier des moments de news économiques importantes
    Enregistre heures et jours pour anticiper l'impact sur l'analyse technique
    """
    
    def __init__(self):
        self.calendar_file = "news_calendar.json"
        self.calendar_data = self._load_calendar()
        self.standard_events = self._get_standard_events()
    
    def _load_calendar(self) -> Dict:
        """Charge le calendrier depuis le fichier"""
        if os.path.exists(self.calendar_file):
            try:
                with open(self.calendar_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Erreur chargement calendrier: {e}")
                return {}
        return {}
    
    def _save_calendar(self):
        """Sauvegarde le calendrier dans le fichier"""
        try:
            with open(self.calendar_file, 'w', encoding='utf-8') as f:
                json.dump(self.calendar_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erreur sauvegarde calendrier: {e}")
    
    def _get_standard_events(self) -> Dict:
        """Retourne les événements économiques standards avec leurs horaires typiques"""
        return {
            'NFP': {
                'name': 'Non-Farm Payrolls',
                'typical_time': '13:30 UTC',
                'day': 'First Friday',
                'currency': 'USD',
                'impact': 'HIGH',
                'duration_minutes': 60
            },
            'FOMC': {
                'name': 'FOMC Interest Rate Decision',
                'typical_time': '18:00 UTC',
                'day': 'Wednesday',
                'currency': 'USD',
                'impact': 'HIGH',
                'duration_minutes': 90
            },
            'CPI': {
                'name': 'Consumer Price Index',
                'typical_time': '13:30 UTC',
                'day': 'Monthly',
                'currency': 'USD',
                'impact': 'HIGH',
                'duration_minutes': 45
            },
            'GDP': {
                'name': 'GDP Growth Rate',
                'typical_time': '12:30 UTC',
                'day': 'Quarterly',
                'currency': 'USD',
                'impact': 'HIGH',
                'duration_minutes': 60
            },
            'ECB': {
                'name': 'ECB Interest Rate Decision',
                'typical_time': '12:15 UTC',
                'day': 'Thursday',
                'currency': 'EUR',
                'impact': 'HIGH',
                'duration_minutes': 90
            },
            'BOE': {
                'name': 'Bank of England Rate Decision',
                'typical_time': '12:00 UTC',
                'day': 'Thursday',
                'currency': 'GBP',
                'impact': 'HIGH',
                'duration_minutes': 90
            },
            'BOJ': {
                'name': 'Bank of Japan Rate Decision',
                'typical_time': '03:00 UTC',
                'day': 'Friday',
                'currency': 'JPY',
                'impact': 'HIGH',
                'duration_minutes': 90
            },
            'ISM_Manufacturing': {
                'name': 'ISM Manufacturing PMI',
                'typical_time': '14:00 UTC',
                'day': 'First Business Day',
                'currency': 'USD',
                'impact': 'MEDIUM',
                'duration_minutes': 30
            },
            'ADP': {
                'name': 'ADP Employment Report',
                'typical_time': '12:15 UTC',
                'day': 'Wednesday before NFP',
                'currency': 'USD',
                'impact': 'MEDIUM',
                'duration_minutes': 30
            },
            'Retail_Sales': {
                'name': 'Retail Sales',
                'typical_time': '12:30 UTC',
                'day': 'Monthly',
                'currency': 'USD',
                'impact': 'MEDIUM',
                'duration_minutes': 30
            }
        }
    
    def add_news_event(self, event_code: str, actual_datetime: datetime, 
                      currency: str = None, impact_level: str = 'MEDIUM'):
        """
        Ajoute un événement de news avec son moment exact
        
        Args:
            event_code: Code de l'événement (NFP, FOMC, etc.)
            actual_datetime: Date et heure réelle de la news
            currency: Devise concernée
            impact_level: Niveau d'impact (HIGH, MEDIUM, LOW)
        """
        if event_code not in self.standard_events:
            print(f"⚠️ Événement inconnu: {event_code}")
            return
        
        event_info = self.standard_events[event_code]
        
        # Formater la date clé
        date_key = actual_datetime.strftime('%Y-%m-%d')
        
        if date_key not in self.calendar_data:
            self.calendar_data[date_key] = []
        
        event_record = {
            'code': event_code,
            'name': event_info['name'],
            'datetime': actual_datetime.isoformat(),
            'time_utc': actual_datetime.strftime('%H:%M'),
            'day_of_week': actual_datetime.strftime('%A'),
            'currency': currency or event_info['currency'],
            'impact': impact_level,
            'duration_minutes': event_info['duration_minutes'],
            'session': self._get_session_at_time(actual_datetime),
            'added_at': datetime.now(timezone.utc).isoformat()
        }
        
        self.calendar_data[date_key].append(event_record)
        self._save_calendar()
        
        print(f"✅ News ajoutée: {event_code} à {actual_datetime.strftime('%Y-%m-%d %H:%M UTC')}")
    
    def get_upcoming_news(self, hours_ahead: int = 24) -> List[Dict]:
        """
        Retourne les news à venir dans les X prochaines heures
        
        Args:
            hours_ahead: Nombre d'heures à regarder en avant
        
        Returns:
            List[Dict]: Liste des news à venir
        """
        now = datetime.now(timezone.utc)
        cutoff_time = now + timedelta(hours=hours_ahead)
        
        upcoming_news = []
        
        # Chercher dans les dates futures
        date_keys = sorted(self.calendar_data.keys())
        
        for date_key in date_keys:
            try:
                event_date = datetime.strptime(date_key, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            except:
                continue
            
            # Si la date est dans la fenêtre de temps
            if now.date() <= event_date.date() <= cutoff_time.date():
                for event in self.calendar_data[date_key]:
                    event_time = datetime.fromisoformat(event['datetime'])
                    
                    if now < event_time <= cutoff_time:
                        upcoming_news.append(event)
        
        return upcoming_news
    
    def get_news_by_time_slot(self, hour: int, day: str = None) -> List[Dict]:
        """
        Retourne les news qui surviennent typiquement à une heure donnée
        
        Args:
            hour: Heure UTC (0-23)
            day: Jour de la semaine (optionnel)
        
        Returns:
            List[Dict]: News à cette heure
        """
        matching_events = []
        
        for event_code, event_info in self.standard_events.items():
            try:
                typical_time = event_info['typical_time']
                event_hour = int(typical_time.split(':')[0])
                
                if event_hour == hour:
                    if day is None or event_info.get('day', '').lower() in day.lower():
                        matching_events.append({
                            'code': event_code,
                            'name': event_info['name'],
                            'typical_time': typical_time,
                            'day': event_info.get('day', 'Various'),
                            'currency': event_info['currency'],
                            'impact': event_info['impact'],
                            'duration_minutes': event_info['duration_minutes']
                        })
            except:
                continue
        
        return matching_events
    
    def get_news_by_currency(self, currency: str) -> List[Dict]:
        """
        Retourne toutes les news pour une devise
        
        Args:
            currency: Devise (USD, EUR, GBP, JPY)
        
        Returns:
            List[Dict]: News pour cette devise
        """
        matching_events = []
        
        for event_code, event_info in self.standard_events.items():
            if event_info['currency'] == currency:
                matching_events.append({
                    'code': event_code,
                    'name': event_info['name'],
                    'typical_time': event_info['typical_time'],
                    'day': event_info.get('day', 'Various'),
                    'impact': event_info['impact'],
                    'duration_minutes': event_info['duration_minutes']
                })
        
        return matching_events
    
    def get_news_schedule(self, date: datetime = None) -> Dict:
        """
        Retourne le calendrier des news pour une date spécifique
        
        Args:
            date: Date à analyser (défaut: aujourd'hui)
        
        Returns:
            Dict: Calendrier des news
        """
        if date is None:
            date = datetime.now(timezone.utc)
        
        date_key = date.strftime('%Y-%m-%d')
        day_of_week = date.strftime('%A')
        
        schedule = {
            'date': date_key,
            'day_of_week': day_of_week,
            'scheduled_news': [],
            'time_slots': {}
        }
        
        # News enregistrées pour cette date
        if date_key in self.calendar_data:
            schedule['scheduled_news'] = self.calendar_data[date_key]
        
        # News typiques pour ce jour de la semaine
        typical_news = []
        for event_code, event_info in self.standard_events.items():
            event_day = event_info.get('day', '').lower()
            if day_of_week.lower() in event_day or 'monthly' in event_day or 'quarterly' in event_day:
                typical_news.append({
                    'code': event_code,
                    'name': event_info['name'],
                    'typical_time': event_info['typical_time'],
                    'currency': event_info['currency'],
                    'impact': event_info['impact']
                })
        
        schedule['typical_news'] = typical_news
        
        # Organiser par créneaux horaires
        for event in typical_news:
            try:
                hour = int(event['typical_time'].split(':')[0])
                if hour not in schedule['time_slots']:
                    schedule['time_slots'][hour] = []
                schedule['time_slots'][hour].append(event)
            except:
                continue
        
        return schedule
    
    def is_news_time(self, check_datetime: datetime = None, buffer_minutes: int = 30) -> bool:
        """
        Vérifie si un moment donné est proche d'une news
        
        Args:
            check_datetime: Date/heure à vérifier
            buffer_minutes: Minutes avant/après la news
        
        Returns:
            bool: True si proche d'une news
        """
        if check_datetime is None:
            check_datetime = datetime.now(timezone.utc)
        
        # Vérifier les news enregistrées
        date_key = check_datetime.strftime('%Y-%m-%d')
        
        if date_key in self.calendar_data:
            for event in self.calendar_data[date_key]:
                event_time = datetime.fromisoformat(event['datetime'])
                duration = event.get('duration_minutes', 30)
                
                # Vérifier si dans la fenêtre de temps
                time_diff = abs((check_datetime - event_time).total_seconds()) / 60
                
                if time_diff <= buffer_minutes + duration:
                    return True
        
        return False
    
    def get_news_impact_window(self, datetime_utc: datetime) -> Dict:
        """
        Retourne la fenêtre d'impact de news pour un moment donné
        
        Args:
            datetime_utc: Date/heure UTC
        
        Returns:
            Dict: Informations sur la fenêtre d'impact
        """
        date_key = datetime_utc.strftime('%Y-%m-%d')
        
        for event in self.calendar_data.get(date_key, []):
            event_time = datetime.fromisoformat(event['datetime'])
            duration = event.get('duration_minutes', 30)
            
            # Vérifier si dans la fenêtre d'impact
            time_diff = (datetime_utc - event_time).total_seconds() / 60
            
            if -30 <= time_diff <= duration:  # 30 min avant jusqu'à la fin de l'impact
                return {
                    'in_news_window': True,
                    'event_code': event['code'],
                    'event_name': event['name'],
                    'event_time': event['time_utc'],
                    'currency': event['currency'],
                    'impact': event['impact'],
                    'minutes_since_news': time_diff,
                    'window_end': duration
                }
        
        return {
            'in_news_window': False,
            'event_code': None,
            'event_name': None,
            'minutes_since_news': None
        }
    
    def _get_session_at_time(self, datetime_obj: datetime) -> str:
        """Détermine la session de trading à un moment donné"""
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
    
    def print_news_calendar(self, date: datetime = None):
        """Affiche le calendrier des news pour une date"""
        if date is None:
            date = datetime.now(timezone.utc)
        
        schedule = self.get_news_schedule(date)
        
        print(f"\n📅 CALENDRIER NEWS - {schedule['date']} ({schedule['day_of_week']})")
        print("=" * 70)
        
        print(f"\n📰 NEWS ENREGISTRÉES: {len(schedule['scheduled_news'])}")
        for event in schedule['scheduled_news']:
            impact_emoji = "🔴" if event['impact'] == 'HIGH' else "🟡" if event['impact'] == 'MEDIUM' else "🟢"
            print(f"  {impact_emoji} {event['time_utc']} - {event['code']}: {event['name']} ({event['currency']})")
        
        print(f"\n⏰ NEWS TYPIQUES: {len(schedule['typical_news'])}")
        for event in schedule['typical_news']:
            impact_emoji = "🔴" if event['impact'] == 'HIGH' else "🟡" if event['impact'] == 'MEDIUM' else "🟢"
            print(f"  {impact_emoji} {event['typical_time']} - {event['code']}: {event['name']} ({event['currency']})")
        
        print(f"\n🕐 PAR CRÉNEAUX HORAIRES:")
        for hour in sorted(schedule['time_slots'].keys()):
            events = schedule['time_slots'][hour]
            print(f"  {hour:02d}:00 UTC: {len(events)} news")
            for event in events:
                print(f"    • {event['code']}: {event['name']}")
    
    def print_upcoming_news(self, hours_ahead: int = 24):
        """Affiche les news à venir"""
        upcoming = self.get_upcoming_news(hours_ahead)
        
        print(f"\n📰 NEWS À VENIR - Prochaines {hours_ahead} heures")
        print("=" * 70)
        
        if not upcoming:
            print("ℹ️ Aucune news à venir dans cette période")
        else:
            for event in upcoming:
                impact_emoji = "🔴" if event['impact'] == 'HIGH' else "🟡" if event['impact'] == 'MEDIUM' else "🟢"
                event_time = datetime.fromisoformat(event['datetime'])
                time_until = (event_time - datetime.now(timezone.utc)).total_seconds() / 60
                
                print(f"{impact_emoji} {event['time_utc']} - {event['code']}: {event['name']}")
                print(f"    Devise: {event['currency']} | Session: {event['session']}")
                print(f"    Dans: {int(time_until)} minutes")
    
    def print_news_by_hour(self, hour: int):
        """Affiche les news pour une heure spécifique"""
        events = self.get_news_by_time_slot(hour)
        
        print(f"\n⏰ NEWS À {hour:02d}:00 UTC")
        print("=" * 70)
        
        if not events:
            print("ℹ️ Aucune news typique à cette heure")
        else:
            for event in events:
                impact_emoji = "🔴" if event['impact'] == 'HIGH' else "🟡" if event['impact'] == 'MEDIUM' else "🟢"
                print(f"{impact_emoji} {event['code']}: {event['name']}")
                print(f"    Jour: {event['day']} | Devise: {event['currency']} | Durée: {event['duration_minutes']} min")

# Instance globale
_news_calendar = None

def get_news_calendar():
    """Retourne l'instance globale du calendrier de news"""
    global _news_calendar
    if _news_calendar is None:
        _news_calendar = NewsCalendar()
    return _news_calendar

# Fonctions utilitaires
def add_news_event(event_code: str, actual_datetime: datetime, currency: str = None, impact_level: str = 'MEDIUM'):
    """Ajoute un événement de news"""
    calendar = get_news_calendar()
    calendar.add_news_event(event_code, actual_datetime, currency, impact_level)

def is_news_time(check_datetime: datetime = None, buffer_minutes: int = 30) -> bool:
    """Vérifie si c'est l'heure d'une news"""
    calendar = get_news_calendar()
    return calendar.is_news_time(check_datetime, buffer_minutes)

def get_news_impact_window(datetime_utc: datetime) -> Dict:
    """Retourne la fenêtre d'impact de news"""
    calendar = get_news_calendar()
    return calendar.get_news_impact_window(datetime_utc)

def print_news_calendar(date: datetime = None):
    """Affiche le calendrier des news"""
    calendar = get_news_calendar()
    calendar.print_news_calendar(date)

def print_upcoming_news(hours_ahead: int = 24):
    """Affiche les news à venir"""
    calendar = get_news_calendar()
    calendar.print_upcoming_news(hours_ahead)
