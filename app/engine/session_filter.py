# app/engine/session_filter.py

from datetime import datetime

# Import du détecteur dynamique
try:
    from app.engine.dynamic_session_detector import is_market_active_dynamic, get_dynamic_session_info
    DYNAMIC_DETECTION_AVAILABLE = True
except ImportError:
    DYNAMIC_DETECTION_AVAILABLE = False

# Import du détecteur de news dynamique
try:
    from app.engine.dynamic_news_detector import is_dynamic_news_time, get_dynamic_news_analysis
    DYNAMIC_NEWS_AVAILABLE = True
except ImportError:
    DYNAMIC_NEWS_AVAILABLE = False

def get_active_session(hour):
    """
    Session basée sur heure UTC pure
    """
    if 22 <= hour or hour < 9:
        return "ASIE"
    elif 9 <= hour < 13:
        return "LONDRES"
    elif 13 <= hour < 17:
        return "OVERLAP"
    elif 17 <= hour < 22:
        return "NEW YORK"
    else:
        return "OFF"


def get_session_info(symbol=None):
    """
    Retourne (session, is_active) selon le symbole
    """
    now     = datetime.utcnow()
    weekday = now.weekday()  # 0=Lundi, 6=Dimanche
    hour    = now.hour

    # ✅ Bitcoin et Crypto : OUVERT 24/7
    if symbol and ("BTC" in symbol or "ETH" in symbol or "crypto" in symbol.lower()):
        session = get_active_session(hour)
        return session, True  # Toujours actif

    # ✅ Forex et Métaux : Weekend fermé
    # Samedi toute la journée = fermé
    # Dimanche avant 22h00 = fermé
    if weekday == 5:  # Samedi
        return "OFF", False

    if weekday == 6 and hour < 22:  # Dimanche avant 22h
        return "OFF", False

    # ✅ Vendredi après 22h = fermé
    if weekday == 4 and hour >= 22:
        return "OFF", False

    session = get_active_session(hour)
    return session, session != "OFF"


def is_trading_session(symbol=None, df=None):
    """
    ✅ Détection dynamique ou fixe selon disponibilité
    Priorité : Détection dynamique > Fixe
    """
    # Essayer la détection dynamique d'abord
    if DYNAMIC_DETECTION_AVAILABLE and df is not None:
        try:
            return is_market_active_dynamic(df, symbol)
        except:
            pass  # Fallback vers méthode fixe
    
    # Fallback vers méthode fixe
    _, is_active = get_session_info(symbol)
    return is_active


def get_session_info_dynamic(symbol=None, df=None):
    """
    ✅ Retourne les infos de session avec détection dynamique si disponible
    """
    # Essayer la détection dynamique d'abord
    if DYNAMIC_DETECTION_AVAILABLE and df is not None:
        try:
            dynamic_info = get_dynamic_session_info(df, symbol)
            return dynamic_info['probable_session'], dynamic_info['is_active']
        except:
            pass  # Fallback vers méthode fixe
    
    # Fallback vers méthode fixe
    return get_session_info(symbol)


def is_news_time(symbol=None, df=None):
    """
    Détection dynamique des news économiques avec fallback horaire fixe
    Priorité : Dynamique > Fixe
    """
    # Essayer la détection dynamique d'abord
    if DYNAMIC_NEWS_AVAILABLE and df is not None and symbol:
        try:
            return is_dynamic_news_time(df, symbol)
        except:
            pass  # Fallback vers méthode fixe
    
    # Fallback vers méthode fixe (original)
    now  = datetime.utcnow()
    hour = now.hour
    min_ = now.minute

    # Heures de news majeures UTC
    news_hours = [
        (8, 30),   # CPI Europe
        (12, 30),  # NFP / CPI US
        (13, 30),  # Données US
        (14, 0),   # Fed
        (15, 0),   # PMI US
        (18, 0),   # Fed speeches
    ]

    for n_hour, n_min in news_hours:
        news_total  = n_hour * 60 + n_min
        current_total = hour * 60 + min_

        # ✅ Bloque 15 min avant et 15 min après
        if abs(current_total - news_total) <= 15:
            return True

    return False


def get_comprehensive_market_analysis(df, symbol):
    """
    Analyse complète du marché : sessions + news + activité
    
    Args:
        df: DataFrame OHLCV
        symbol: Symbole à analyser
    
    Returns:
        dict: Analyse complète du marché
    """
    analysis = {
        'symbol': symbol,
        'timestamp': datetime.utcnow(),
        'session_active': False,
        'news_blocking': False,
        'market_activity': 'UNKNOWN'
    }
    
    # 1. Analyse de session
    if DYNAMIC_DETECTION_AVAILABLE and df is not None:
        try:
            session_info, session_ok = get_dynamic_session_info(symbol, df)
            analysis['session_active'] = session_ok
            analysis['session_info'] = session_info
        except:
            session_info, session_ok = get_session_info(symbol)
            analysis['session_active'] = session_ok
            analysis['session_info'] = session_info
    else:
        session_info, session_ok = get_session_info(symbol)
        analysis['session_active'] = session_ok
        analysis['session_info'] = session_info
    
    # 2. Analyse de news
    if DYNAMIC_NEWS_AVAILABLE and df is not None:
        try:
            news_analysis = get_dynamic_news_analysis(df, symbol)
            analysis['news_blocking'] = news_analysis.get('should_block_trading', False)
            analysis['news_analysis'] = news_analysis
        except:
            analysis['news_blocking'] = is_news_time(symbol, df)
            analysis['news_analysis'] = {'fallback': True}
    else:
        analysis['news_blocking'] = is_news_time(symbol, df)
        analysis['news_analysis'] = {'fallback': True}
    
    # 3. Statut final du marché
    if analysis['session_active'] and not analysis['news_blocking']:
        analysis['market_status'] = 'OPEN_FOR_TRADING'
        analysis['market_activity'] = 'ACTIVE'
    elif analysis['news_blocking']:
        analysis['market_status'] = 'BLOCKED_BY_NEWS'
        analysis['market_activity'] = 'BLOCKED'
    elif not analysis['session_active']:
        analysis['market_status'] = 'SESSION_CLOSED'
        analysis['market_activity'] = 'LOW'
    else:
        analysis['market_status'] = 'CONDITIONAL'
        analysis['market_activity'] = 'LIMITED'
    
    # 4. Recommandations
    analysis['recommendations'] = []
    
    if analysis['market_status'] == 'OPEN_FOR_TRADING':
        analysis['recommendations'].append('✅ Market conditions favorable for trading')
    elif analysis['market_status'] == 'BLOCKED_BY_NEWS':
        analysis['recommendations'].append('🚨 High impact news detected - Avoid trading')
        analysis['recommendations'].append('⏰ Wait for market stabilization')
    elif analysis['market_status'] == 'SESSION_CLOSED':
        analysis['recommendations'].append('🔴 Market session closed')
        analysis['recommendations'].append('⏳ Wait for session opening')
    else:
        analysis['recommendations'].append('⚠️ Trading conditions require caution')
    
    return analysis