# app/engine/advanced_entry.py

import pandas as pd
import numpy as np

def calculate_entry_50_percent(df, signal, direction):
    """
    Calcule le point d'entrée à 50% de la range pour un meilleur Risk/Reward
    
    Args:
        df: DataFrame OHLCV
        signal: Signal Price Range avec range_size
        direction: Direction du trade (HAUSSIER/BAISSIER)
    
    Returns:
        dict: Informations d'entrée optimisées
    """
    if not signal or not signal.get('valid'):
        return {
            'valid': False,
            'reason': 'Signal invalide'
        }
    
    range_size = signal['range_size']
    current_price = df['close'].iloc[-1]
    
    # Entry à 50% de la range
    if direction == "HAUSSIER":
        entry = current_price + (range_size * 0.5)
    else:  # BAISSIER
        entry = current_price - (range_size * 0.5)
    
    # Vérifier si l'entrée est réaliste
    if direction == "HAUSSIER":
        entry_realistic = entry > current_price
    else:
        entry_realistic = entry < current_price
    
    return {
        'valid': entry_realistic,
        'entry': entry,
        'current_price': current_price,
        'range_size': range_size,
        'entry_offset': abs(entry - current_price),
        'entry_offset_percentage': 50.0,
        'reason': 'Entry à 50% de range optimisée'
    }


def calculate_entry_with_market_structure(df, signal, direction):
    """
    Calcule l'entrée en tenant compte de la structure du marché
    
    Args:
        df: DataFrame OHLCV
        signal: Signal Price Range
        direction: Direction du trade
    
    Returns:
        dict: Entry optimisée avec structure
    """
    base_entry = calculate_entry_50_percent(df, signal, direction)
    
    if not base_entry['valid']:
        return base_entry
    
    # Analyser la structure pour ajuster l'entrée
    entry = base_entry['entry']
    
    # Niveaux de support/résistance proches
    recent_highs = df['high'].tail(10).values
    recent_lows = df['low'].tail(10).values
    
    # Ajuster l'entrée pour éviter les niveaux clés
    if direction == "HAUSSIER":
        # Éviter les résistances proches
        nearby_resistance = max([h for h in recent_highs if h > entry - 0.0010], default=None)
        if nearby_resistance and abs(nearby_resistance - entry) < 0.0005:
            entry = nearby_resistance + 0.0002  # Entrer après la résistance
    else:  # BAISSIER
        # Éviter les supports proches
        nearby_support = min([l for l in recent_lows if l < entry + 0.0010], default=None)
        if nearby_support and abs(nearby_support - entry) < 0.0005:
            entry = nearby_support - 0.0002  # Entrer après le support
    
    return {
        'valid': True,
        'entry': entry,
        'current_price': base_entry['current_price'],
        'range_size': base_entry['range_size'],
        'entry_offset': abs(entry - base_entry['current_price']),
        'entry_offset_percentage': 50.0,
        'structure_adjusted': True,
        'adjustment_reason': 'Évitement des niveaux clés',
        'reason': 'Entry optimisée avec structure du marché'
    }


def calculate_entry_with_volatility_adjustment(df, signal, direction, symbol="EURUSD"):
    """
    Calcule l'entrée avec ajustement selon la volatilité
    
    Args:
        df: DataFrame OHLCV
        signal: Signal Price Range
        direction: Direction du trade
        symbol: Symbole pour ajustements spécifiques
    
    Returns:
        dict: Entry avec ajustement volatilité
    """
    base_entry = calculate_entry_50_percent(df, signal, direction)
    
    if not base_entry['valid']:
        return base_entry
    
    # Calculer l'ATR pour ajuster selon la volatilité
    atr = calculate_atr(df, 14)
    range_size = base_entry['range_size']
    
    # Ajustement selon la volatilité
    volatility_ratio = range_size / atr
    
    if volatility_ratio > 2.0:
        # Très volatil - réduire l'offset à 40%
        entry_offset_percentage = 40.0
    elif volatility_ratio < 0.5:
        # Peu volatil - augmenter l'offset à 60%
        entry_offset_percentage = 60.0
    else:
        # Volatilité normale - 50%
        entry_offset_percentage = 50.0
    
    # Recalculer l'entrée avec le nouvel offset
    current_price = base_entry['current_price']
    if direction == "HAUSSIER":
        entry = current_price + (range_size * entry_offset_percentage / 100)
    else:
        entry = current_price - (range_size * entry_offset_percentage / 100)
    
    return {
        'valid': True,
        'entry': entry,
        'current_price': current_price,
        'range_size': range_size,
        'entry_offset': abs(entry - current_price),
        'entry_offset_percentage': entry_offset_percentage,
        'atr': atr,
        'volatility_ratio': volatility_ratio,
        'volatility_adjusted': True,
        'reason': f'Entry ajustée selon volatilité ({entry_offset_percentage}% de range)'
    }


def calculate_atr(df, period=14):
    """
    Calcule l'Average True Range
    
    Args:
        df: DataFrame OHLCV
        period: Période ATR
    
    Returns:
        float: ATR calculé
    """
    if len(df) < period + 1:
        return 0.0010  # Valeur par défaut
    
    high = df['high']
    low = df['low']
    close = df['close']
    
    # True Range
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # ATR (moyenne mobile simple)
    atr = tr.rolling(window=period).mean().iloc[-1]
    
    return atr if not pd.isna(atr) else 0.0010


def get_optimal_entry(df, signal, direction, symbol="EURUSD", use_structure=True, use_volatility=True):
    """
    Calcule le point d'entrée optimal avec toutes les optimisations
    
    Args:
        df: DataFrame OHLCV
        signal: Signal Price Range
        direction: Direction du trade
        symbol: Symbole pour ajustements
        use_structure: Utiliser l'ajustement structurel
        use_volatility: Utiliser l'ajustement volatilité
    
    Returns:
        dict: Entry optimale complète
    """
    # Entry de base à 50%
    entry_result = calculate_entry_50_percent(df, signal, direction)
    
    if not entry_result['valid']:
        return entry_result
    
    # Appliquer les ajustements
    if use_volatility:
        entry_result = calculate_entry_with_volatility_adjustment(df, signal, direction, symbol)
    
    if use_structure:
        entry_result = calculate_entry_with_market_structure(df, signal, direction)
    
    # Calculer le Risk/Reward amélioré
    range_size = entry_result['range_size']
    entry = entry_result['entry']
    
    if direction == "HAUSSIER":
        sl = entry - range_size
        tp = entry + (range_size * 2)
    else:
        sl = entry + range_size
        tp = entry - (range_size * 2)
    
    # RR amélioré grâce à l'entrée à 50%
    risk = abs(entry - sl)
    reward = abs(tp - entry)
    rr_ratio = reward / risk
    
    entry_result.update({
        'stop_loss': sl,
        'take_profit': tp,
        'risk': risk,
        'reward': reward,
        'rr_ratio': rr_ratio,
        'rr_improvement': f"+{(rr_ratio - 2.0) / 2.0 * 100:.1f}%" if rr_ratio > 2.0 else "Standard"
    })
    
    return entry_result


def print_entry_results(entry_result):
    """
    Affiche les résultats d'entrée de manière lisible
    """
    print("🎯 CALCUL D'ENTRÉE OPTIMISÉE")
    print("=" * 50)
    
    if not entry_result['valid']:
        print(f"❌ {entry_result['reason']}")
        return
    
    print(f"📍 Prix actuel: {entry_result['current_price']:.5f}")
    print(f"🎯 Point d'entrée: {entry_result['entry']:.5f}")
    print(f"📏 Offset d'entrée: {entry_result['entry_offset']:.5f} ({entry_result['entry_offset_percentage']:.1f}% de range)")
    print(f"🛡️ Stop Loss: {entry_result.get('stop_loss', 'N/A'):.5f}")
    print(f"🎯 Take Profit: {entry_result.get('take_profit', 'N/A'):.5f}")
    print(f"⚖️ Risk/Reward: {entry_result.get('rr_ratio', 'N/A'):.2f}")
    print(f"📈 Amélioration RR: {entry_result.get('rr_improvement', 'N/A')}")
    
    if entry_result.get('volatility_adjusted'):
        print(f"🌊 Ajustement volatilité: Ratio {entry_result.get('volatility_ratio', 'N/A'):.2f}")
    
    if entry_result.get('structure_adjusted'):
        print(f"🏗️ Ajustement structurel: {entry_result.get('adjustment_reason', 'N/A')}")
    
    print(f"\n✅ {entry_result['reason']}")


