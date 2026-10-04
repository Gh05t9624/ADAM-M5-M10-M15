# app/engine/dynamic_take_profit.py

import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta

def get_current_session():
    """
    Détermine la session de trading actuelle
    
    Returns:
        str: Session actuelle (Asian, London, NYC, Sydney)
    """
    now = datetime.now(timezone.utc)
    hour = now.hour
    
    # Sessions en UTC
    if 0 <= hour < 6:
        return "Sydney"
    elif 6 <= hour < 13:
        return "Asian"
    elif 13 <= hour < 20:
        return "London"
    else:
        return "NYC"


def get_session_multiplier(session, symbol="EURUSD"):
    """
    Multiplicateur de TP selon la session et le symbole
    
    Args:
        session: Session de trading
        symbol: Symbole tradé
    
    Returns:
        dict: Multiplicateurs pour différentes conditions
    """
    # Multiplicateurs de base par session
    session_multipliers = {
        "Sydney": {"low": 0.8, "normal": 1.0, "high": 1.2},
        "Asian": {"low": 0.9, "normal": 1.1, "high": 1.3},
        "London": {"low": 1.0, "normal": 1.2, "high": 1.5},
        "NYC": {"low": 1.1, "normal": 1.3, "high": 1.6}
    }
    
    # Ajustements spécifiques par symbole
    symbol_adjustments = {
        "XAUUSD": {"multiplier": 1.2, "volatility_factor": 1.5},
        "GOLD": {"multiplier": 1.2, "volatility_factor": 1.5},
        "BTCUSD": {"multiplier": 1.5, "volatility_factor": 2.0},
        "EURUSD": {"multiplier": 1.0, "volatility_factor": 1.0},
        "GBPUSD": {"multiplier": 1.1, "volatility_factor": 1.1},
        "USDJPY": {"multiplier": 1.0, "volatility_factor": 1.0}
    }
    
    # Obtenir les ajustements pour le symbole
    symbol_adj = symbol_adjustments.get("EURUSD", {"multiplier": 1.0, "volatility_factor": 1.0})
    for key, adj in symbol_adjustments.items():
        if key in symbol:
            symbol_adj = adj
            break
    
    # Appliquer les ajustements
    base_multipliers = session_multipliers.get(session, session_multipliers["London"])
    
    return {
        "low": base_multipliers["low"] * symbol_adj["multiplier"],
        "normal": base_multipliers["normal"] * symbol_adj["multiplier"],
        "high": base_multipliers["high"] * symbol_adj["multiplier"],
        "volatility_factor": symbol_adj["volatility_factor"]
    }


def calculate_session_atr(df, symbol="EURUSD"):
    """
    Calcule l'ATR adapté selon la session
    
    Args:
        df: DataFrame OHLCV
        symbol: Symbole tradé
    
    Returns:
        float: ATR ajusté selon session
    """
    # ATR standard
    if len(df) < 14:
        return 0.0010
    
    high = df['high']
    low = df['low']
    close = df['close']
    
    # True Range
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=14).mean().iloc[-1]
    
    # Ajustement selon session
    session = get_current_session()
    session_multipliers = get_session_multiplier(session, symbol)
    
    # ATR ajusté selon la volatilité de la session
    adjusted_atr = atr * session_multipliers["volatility_factor"]
    
    return adjusted_atr if not pd.isna(adjusted_atr) else 0.0010


def get_volatility_multiplier(df):
    """
    Détermine le multiplicateur selon la volatilité actuelle
    
    Args:
        df: DataFrame OHLCV
    
    Returns:
        str: Niveau de volatilité (low/normal/high)
    """
    if len(df) < 20:
        return "normal"
    
    # Calculer la volatilité récente vs historique
    recent_volatility = (df['high'].tail(10) - df['low'].tail(10)).mean()
    historical_volatility = (df['high'].tail(50) - df['low'].tail(50)).mean()
    
    if historical_volatility == 0:
        return "normal"
    
    volatility_ratio = recent_volatility / historical_volatility
    
    if volatility_ratio < 0.8:
        return "low"
    elif volatility_ratio > 1.3:
        return "high"
    else:
        return "normal"


def get_structure_levels(df, direction):
    """
    Identifie les niveaux de structure importants pour TP
    
    Args:
        df: DataFrame OHLCV
        direction: Direction du trade
    
    Returns:
        list: Niveaux de structure importants
    """
    if len(df) < 20:
        return []
    
    levels = []
    
    # Identifier les swing highs et swing lows récents
    highs = df['high'].tail(20)
    lows = df['low'].tail(20)
    
    # Swing highs (pour les trades haussiers)
    if direction == "HAUSSIER":
        # Chercher les résistances importantes
        for i in range(2, len(highs)):
            if highs.iloc[i] > highs.iloc[i-1] and highs.iloc[i] > highs.iloc[i-2]:
                if highs.iloc[i] > highs.iloc[i+1] if i+1 < len(highs) else True:
                    levels.append(highs.iloc[i])
    
    # Swing lows (pour les trades baissiers)
    else:
        # Chercher les supports importants
        for i in range(2, len(lows)):
            if lows.iloc[i] < lows.iloc[i-1] and lows.iloc[i] < lows.iloc[i-2]:
                if lows.iloc[i] < lows.iloc[i+1] if i+1 < len(lows) else True:
                    levels.append(lows.iloc[i])
    
    # Retourner les 3 niveaux les plus pertinents
    return sorted(levels)[:3]


def calculate_smart_tp(entry, direction, atr, volatility_multiplier, structure_levels, symbol="EURUSD"):
    """
    Calcule le TP intelligent en combinant ATR et structure
    
    Args:
        entry: Prix d'entrée
        direction: Direction du trade
        atr: ATR ajusté
        volatility_multiplier: Multiplicateur de volatilité
        structure_levels: Niveaux de structure
        symbol: Symbole tradé
    
    Returns:
        dict: Informations TP complètes
    """
    session = get_current_session()
    session_multipliers = get_session_multiplier(session, symbol)
    
    # TP basé sur ATR selon la volatilité
    volatility_level = get_volatility_multiplier(pd.DataFrame())
    atr_multiplier = session_multipliers[volatility_level]
    
    tp_atr = atr * atr_multiplier
    
    if direction == "HAUSSIER":
        tp_atr_price = entry + tp_atr
    else:
        tp_atr_price = entry - tp_atr
    
    # TP basé sur la structure
    tp_structure = None
    if structure_levels:
        if direction == "HAUSSIER":
            # Prendre la résistance la plus proche au-dessus
            valid_levels = [level for level in structure_levels if level > entry]
            if valid_levels:
                tp_structure = min(valid_levels)
        else:
            # Prendre le support le plus proche en dessous
            valid_levels = [level for level in structure_levels if level < entry]
            if valid_levels:
                tp_structure = max(valid_levels)
    
    # TP final = le plus proche entre ATR et structure
    if tp_structure:
        if direction == "HAUSSIER":
            final_tp = min(tp_atr_price, tp_structure)
        else:
            final_tp = max(tp_atr_price, tp_structure)
        tp_type = "Structure+ATR"
    else:
        final_tp = tp_atr_price
        tp_type = "ATR"
    
    # Calculer le Risk/Reward
    tp_distance = abs(final_tp - entry)
    
    return {
        'tp_price': final_tp,
        'tp_type': tp_type,
        'tp_atr': tp_atr_price,
        'tp_structure': tp_structure,
        'tp_distance': tp_distance,
        'session': session,
        'volatility_level': volatility_level,
        'atr_multiplier': atr_multiplier,
        'atr_used': atr
    }


def dynamic_take_profit(df, entry, direction, symbol="EURUSD"):
    """
    Calcule le TP dynamique complet selon ATR, session et structure
    
    Args:
        df: DataFrame OHLCV
        entry: Prix d'entrée
        direction: Direction du trade
        symbol: Symbole tradé
    
    Returns:
        dict: TP dynamique complet
    """
    # Calculer l'ATR adapté
    atr = calculate_session_atr(df, symbol)
    
    # Obtenir le multiplicateur de volatilité
    volatility_level = get_volatility_multiplier(df)
    
    # Identifier les niveaux de structure
    structure_levels = get_structure_levels(df, direction)
    
    # Calculer le TP intelligent
    tp_result = calculate_smart_tp(entry, direction, atr, volatility_level, structure_levels, symbol)
    
    # Ajouter des informations supplémentaires
    tp_result.update({
        'symbol': symbol,
        'entry': entry,
        'direction': direction,
        'structure_levels': structure_levels,
        'calculation_time': datetime.now(timezone.utc).strftime('%H:%M:%S UTC')
    })
    
    return tp_result


def print_tp_results(tp_result):
    """
    Affiche les résultats TP de manière lisible
    """
    print("🎯 CALCUL DE TAKE PROFIT DYNAMIQUE")
    print("=" * 50)
    
    print(f"💰 Entrée: {tp_result['entry']:.5f}")
    print(f"📍 Direction: {tp_result['direction']}")
    print(f"🌍 Session: {tp_result['session']}")
    print(f"🌊 Volatilité: {tp_result['volatility_level']}")
    
    print(f"\n📊 ANALYSE ATR:")
    print(f"   ATR utilisé: {tp_result['atr_used']:.5f}")
    print(f"   Multiplicateur: {tp_result['atr_multiplier']:.2f}")
    print(f"   TP ATR: {tp_result['tp_atr']:.5f}")
    
    if tp_result['tp_structure']:
        print(f"\n🏗️ ANALYSE STRUCTURE:")
        print(f"   TP Structure: {tp_result['tp_structure']:.5f}")
        print(f"   Type: {tp_result['tp_type']}")
    
    print(f"\n🎯 RÉSULTAT FINAL:")
    print(f"   TP Dynamique: {tp_result['tp_price']:.5f}")
    print(f"   Distance TP: {tp_result['tp_distance']:.5f}")
    print(f"   Heure calcul: {tp_result['calculation_time']}")
    
    # Calculer le RR si SL disponible
    if 'stop_loss' in tp_result:
        risk = abs(tp_result['entry'] - tp_result['stop_loss'])
        reward = tp_result['tp_distance']
        rr_ratio = reward / risk
        print(f"\n⚖️ RISK/REWARD: {rr_ratio:.2f}")


# Exemple d'utilisation
    
    tp_result = dynamic_take_profit(df, entry, direction, "EURUSD")
    print_tp_results(tp_result)
