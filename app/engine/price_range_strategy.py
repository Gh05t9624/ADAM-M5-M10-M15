# app/engine/price_range_strategy.py

import pandas as pd
import numpy as np
from datetime import datetime, timezone

# Import des modules avancés pour Phase 1
from app.engine.advanced_confirmation import advanced_direction_confirmation
from app.engine.advanced_entry import get_optimal_entry
from app.engine.dynamic_take_profit import dynamic_take_profit

def is_valid_price_range_time(symbol="EURUSD"):
    """
    Vérifie si l'heure actuelle est valide pour la stratégie Price Range.
    Heures optimisées selon la liquidité par symbole.
    
    Args:
        symbol: Symbole analysé pour ajuster les heures selon la liquidité
    
    Returns:
        tuple: (valid: bool, reason: str)
    """
    now = datetime.now(timezone.utc)
    hour = now.hour
    minute = now.minute
    
    # Heures optimisées selon la liquidité
    if "XAU" in symbol or "GOLD" in symbol:
        # Or : éviter 8h UTC (faible liquidité)
        valid_hours = [12, 16, 20]  # Londres/NYC overlap
        reason = "Heures optimisées pour l'or (éviter 8h UTC)"
    else:
        # Forex : toutes les heures
        valid_hours = [8, 12, 16, 20]
        reason = "Heures standard forex"
    
    # Vérifier si on est exactement à l'heure valide (±5 minutes max)
    for valid_hour in valid_hours:
        if hour == valid_hour and minute <= 5:
            return True, reason
    
    return False, f"Hors heures valides. Prochaines : {valid_hours}h UTC"


def get_next_valid_time():
    """
    Retourne la prochaine heure valide pour la stratégie Price Range
    """
    now = datetime.now(timezone.utc)
    hour = now.hour
    valid_hours = [8, 12, 16, 20]

    for h in valid_hours:
        if h > hour:
            return h

    # Si aucune heure valide aujourd'hui, retourne 8h demain
    return valid_hours[0]


def calculate_price_range(df, lookback=4):
    """
    Calcule la range (haut-bas) sur lookback bougies (4 par défaut = H4 sur H1)
    """
    if len(df) < lookback:
        return None, None, None

    # Prendre les 4 dernières bougies
    recent_candles = df.tail(lookback)

    # Calcul de la range
    range_high = recent_candles['high'].max()
    range_low = recent_candles['low'].min()
    range_size = range_high - range_low

    return range_high, range_low, range_size


def project_price_ranges(df, range_size, current_price, duplications=2):
    """
    Projette la range dupliquée vers l'avenir
    """
    if range_size is None:
        return []

    projections = []

    for i in range(1, duplications + 1):
        # Projection haute
        proj_high = current_price + (range_size * i)
        # Projection basse
        proj_low = current_price - (range_size * i)

        projections.append({
            'level': i,
            'high': proj_high,
            'low': proj_low,
            'size': range_size
        })

    return projections


def analyze_third_candle(df, projections):
    """
    Analyse la 3ème bougie pour déterminer la direction
    """
    if len(df) < 3:
        return None, None, None

    # 3ème bougie (index -3)
    third_candle = df.iloc[-3]
    third_open = third_candle['open']
    third_close = third_candle['close']

    # Détermination de la direction
    if third_open > third_close:
        direction = "BAISSIER"
        # Signal baissier : price range vers le bas
        entry_zone = projections[0]['low'] if projections else None
    else:
        direction = "HAUSSIER"
        # Signal haussier : price range vers le haut
        entry_zone = projections[0]['high'] if projections else None

    return direction, third_open, third_close, entry_zone


def get_entry_point(df, projections, bot_direction):
    """
    Détermine le point d'entrée selon la tendance du bot
    et la fermeture du premier price range projeté
    """
    if not projections:
        return df['close'].iloc[-1]

    # Point d'entrée = fermeture du premier price range projeté
    if bot_direction == "HAUSSIER":
        entry = projections[0]['high']
    elif bot_direction == "BAISSIER":
        entry = projections[0]['low']
    else:
        entry = df['close'].iloc[-1]

    return entry


def price_range_signal_advanced(df, bot_direction, symbol="EURUSD", lookback=4, duplications=2, check_time=True):
    """
    Signal Price Range avancé - Phase 1 complète avec toutes les améliorations
    
    Args:
        df: DataFrame OHLCV
        bot_direction: Direction déclarée par le bot (HAUSSIER/BAISSIER/NEUTRE)
        symbol: Symbole pour ajustements spécifiques
        lookback: Nombre de bougies pour calculer la range (4 par défaut)
        duplications: Nombre de duplications de la range (2 par défaut)
        check_time: Vérifier si l'heure est valide
    
    Returns:
        dict: Signal avancé complet avec toutes les optimisations Phase 1
    """
    # Vérification de l'heure (stratégie valide uniquement aux heures optimales)
    if check_time:
        time_valid, time_reason = is_valid_price_range_time(symbol)
        if not time_valid:
            next_time = get_next_valid_time()
            return {
                'valid': False,
                'reason': f'{time_reason}. Prochaine heure valide : {next_time}h UTC',
                'next_valid_time': next_time,
                'phase': '1',
                'version': 'advanced'
            }

    if df is None or len(df) < lookback + 3:
        return {
            'valid': False,
            'reason': 'Pas assez de données',
            'phase': '1',
            'version': 'advanced'
        }

    # 1. Calculer la range des 4 bougies
    range_high, range_low, range_size = calculate_price_range(df, lookback)

    if range_size is None:
        return {
            'valid': False,
            'reason': 'Impossible de calculer la range',
            'phase': '1',
            'version': 'advanced'
        }

    current_price = df['close'].iloc[-1]

    # 2. Projeter la range dupliquée
    projections = project_price_ranges(df, range_size, current_price, duplications)

    # 3. Analyser la 3ème bougie
    direction, third_open, third_close, entry_zone = analyze_third_candle(df, projections)

    # 4. CONFIRMATION MULTI-SIGNAUX (Phase 1.1)
    confirmed, score, confirmations = advanced_direction_confirmation(df, bot_direction)
    
    if not confirmed:
        return {
            'valid': False,
            'reason': f'Confirmation multi-signaux échouée ({score}/4)',
            'confirmations': confirmations,
            'confirmation_score': score,
            'phase': '1',
            'version': 'advanced'
        }

    # 5. ENTRÉE OPTIMISÉE 50% (Phase 1.2)
    base_signal = {
        'valid': True,
        'range_size': range_size,
        'range_high': range_high,
        'range_low': range_low,
        'projections': projections,
        'third_candle_direction': direction,
        'bot_direction': bot_direction
    }
    
    entry_result = get_optimal_entry(df, base_signal, bot_direction, symbol, 
                                   use_structure=True, use_volatility=True)
    
    if not entry_result['valid']:
        return {
            'valid': False,
            'reason': entry_result['reason'],
            'phase': '1',
            'version': 'advanced'
        }

    # 6. TP DYNAMIQUE (Phase 1.3)
    tp_result = dynamic_take_profit(df, entry_result['entry'], bot_direction, symbol)

    # 7. Assembler le résultat complet
    return {
        'valid': True,
        'phase': '1',
        'version': 'advanced',
        
        # Données de base
        'range_high': range_high,
        'range_low': range_low,
        'range_size': range_size,
        'current_price': current_price,
        'symbol': symbol,
        
        # Direction et confirmation
        'bot_direction': bot_direction,
        'third_candle_direction': direction,
        'confirmed': confirmed,
        'confirmation_score': score,
        'confirmations': confirmations,
        
        # Entrée optimisée
        'entry': entry_result['entry'],
        'entry_offset': entry_result['entry_offset'],
        'entry_offset_percentage': entry_result['entry_offset_percentage'],
        'stop_loss': entry_result['stop_loss'],
        'risk': entry_result['risk'],
        'rr_ratio': entry_result['rr_ratio'],
        'rr_improvement': entry_result['rr_improvement'],
        
        # TP dynamique
        'take_profit': tp_result['tp_price'],
        'tp_type': tp_result['tp_type'],
        'tp_distance': tp_result['tp_distance'],
        'session': tp_result['session'],
        'volatility_level': tp_result['volatility_level'],
        
        # Projections (pour référence)
        'projections': projections,
        
        # Métadonnées
        'calculation_time': datetime.now(timezone.utc).strftime('%H:%M:%S UTC'),
        'reason': 'Signal Price Range avancé - Phase 1 complète'
    }


def calculate_sl_tp_from_price_range(df, signal, symbol="EURUSD"):
    """
    Calcule SL et TP basés sur la stratégie Price Range
    """
    if not signal['valid']:
        return None, None, None

    range_size = signal['range_size']
    entry = signal['entry']
    direction = signal['bot_direction']

    # Pip selon symbole
    if "JPY" in symbol:
        pip = 0.01
    elif "XAU" in symbol or "GOLD" in symbol or "BTC" in symbol:
        pip = 0.1
    else:
        pip = 0.0001

    # SL basé sur la range (1x la range)
    sl_pips = range_size / pip

    # TP basé sur 2x la range (RR 1:2)
    tp_pips = sl_pips * 2

    if direction == "HAUSSIER":
        sl = entry - (range_size)
        tp = entry + (range_size * 2)
    elif direction == "BAISSIER":
        sl = entry + (range_size)
        tp = entry - (range_size * 2)
    else:
        sl = None
        tp = None

    # Calcul RR
    if sl is not None and tp is not None:
        rr = abs(tp - entry) / abs(sl - entry)
    else:
        rr = 0

    return sl, tp, rr


    print(f"RR: {rr}")
