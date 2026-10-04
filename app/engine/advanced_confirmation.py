# app/engine/advanced_confirmation.py

import pandas as pd
import numpy as np

def check_structure_confirmation(df, direction):
    """
    Confirmation structurelle basée sur les Higher Highs/Higher Lows ou Lower Highs/Lower Lows
    
    Args:
        df: DataFrame OHLCV
        direction: Direction à confirmer (HAUSSIER/BAISSIER)
    
    Returns:
        bool: True si la structure confirme la direction
    """
    if len(df) < 10:
        return False
    
    # Analyser les 10 dernières bougies
    recent = df.tail(10)
    
    if direction == "HAUSSIER":
        # Chercher HH et HL
        highs = recent['high'].values
        lows = recent['low'].values
        
        # Vérifier si on a des Higher Highs
        hh_count = 0
        for i in range(2, len(highs)):
            if highs[i] > highs[i-1] and highs[i-1] > highs[i-2]:
                hh_count += 1
        
        # Vérifier si on a des Higher Lows
        hl_count = 0
        for i in range(2, len(lows)):
            if lows[i] > lows[i-1] and lows[i-1] > lows[i-2]:
                hl_count += 1
        
        # Structure haussière confirmée si on a au moins 2 HH ou HL
        return hh_count >= 2 or hl_count >= 2
    
    else:  # BAISSIER
        # Chercher LH et LL
        highs = recent['high'].values
        lows = recent['low'].values
        
        # Vérifier si on a des Lower Highs
        lh_count = 0
        for i in range(2, len(highs)):
            if highs[i] < highs[i-1] and highs[i-1] < highs[i-2]:
                lh_count += 1
        
        # Vérifier si on a des Lower Lows
        ll_count = 0
        for i in range(2, len(lows)):
            if lows[i] < lows[i-1] and lows[i-1] < lows[i-2]:
                ll_count += 1
        
        # Structure baissière confirmée si on a au moins 2 LH ou LL
        return lh_count >= 2 or ll_count >= 2


def check_momentum_confirmation(df, direction):
    """
    Confirmation basée sur le momentum (vitesse et accélération du prix)
    
    Args:
        df: DataFrame OHLCV
        direction: Direction à confirmer
    
    Returns:
        bool: True si le momentum confirme la direction
    """
    if len(df) < 5:
        return False
    
    # Calculer le momentum sur 5 périodes
    closes = df['close'].values
    momentum = closes[-1] - closes[-5]
    
    # Calculer l'accélération (changement de momentum)
    if len(closes) >= 10:
        prev_momentum = closes[-5] - closes[-10]
        acceleration = momentum - prev_momentum
    else:
        acceleration = 0
    
    if direction == "HAUSSIER":
        # Momentum positif et accélération positive
        return momentum > 0 and acceleration >= 0
    else:  # BAISSIER
        # Momentum négatif et accélération négative
        return momentum < 0 and acceleration <= 0


def check_strong_close(df, direction):
    """
    Confirmation basée sur la force de la clôture (>75% de la range)
    
    Args:
        df: DataFrame OHLCV
        direction: Direction à confirmer
    
    Returns:
        bool: True si la clôture est forte
    """
    if len(df) < 2:
        return False
    
    last_candle = df.iloc[-1]
    
    if direction == "HAUSSIER":
        # Clôture dans le haut 25% de la range
        candle_range = last_candle['high'] - last_candle['low']
        close_position = last_candle['close'] - last_candle['low']
        return (close_position / candle_range) > 0.75
    else:  # BAISSIER
        # Clôture dans le bas 25% de la range
        candle_range = last_candle['high'] - last_candle['low']
        close_position = last_candle['high'] - last_candle['close']
        return (close_position / candle_range) > 0.75


def check_volume_confirmation(df, direction):
    """
    Confirmation basée sur le volume (volume supérieur à la moyenne)
    
    Args:
        df: DataFrame OHLCV avec volume
        direction: Direction à confirmer
    
    Returns:
        bool: True si le volume confirme la direction
    """
    if 'volume' not in df.columns or len(df) < 20:
        return True  # Pas de volume disponible, on considère comme confirmé
    
    last_volume = df['volume'].iloc[-1]
    avg_volume = df['volume'].tail(20).mean()
    
    # Volume doit être au moins 1.2x la moyenne
    return last_volume > (avg_volume * 1.2)


def advanced_direction_confirmation(df, direction):
    """
    Système de confirmation multi-signaux avancé
    
    Args:
        df: DataFrame OHLCV
        direction: Direction à confirmer (HAUSSIER/BAISSIER)
    
    Returns:
        tuple: (confirmed: bool, score: int, confirmations: list)
    """
    confirmations = []
    
    # 1. Confirmation structurelle
    structure_conf = check_structure_confirmation(df, direction)
    confirmations.append(('Structure', structure_conf))
    
    # 2. Confirmation momentum
    momentum_conf = check_momentum_confirmation(df, direction)
    confirmations.append(('Momentum', momentum_conf))
    
    # 3. Confirmation clôture forte
    strong_close = check_strong_close(df, direction)
    confirmations.append(('Strong Close', strong_close))
    
    # 4. Confirmation volume
    volume_conf = check_volume_confirmation(df, direction)
    confirmations.append(('Volume', volume_conf))
    
    # Score de confirmation (nombre de confirmations positives)
    score = sum(1 for _, conf in confirmations if conf)
    
    # Confirmation requise : au moins 3/4
    confirmed = score >= 3
    
    return confirmed, score, confirmations


def print_confirmation_results(confirmations, score, confirmed):
    """
    Affiche les résultats de confirmation de manière lisible
    """
    print("🔍 CONFIRMATION MULTI-SIGNAUX")
    print("=" * 40)
    
    for name, conf in confirmations:
        status = "✅" if conf else "❌"
        print(f"{status} {name}: {'Confirmé' if conf else 'Non confirmé'}")
    
    print(f"\n📊 Score: {score}/4")
    print(f"🎯 Résultat: {'✅ SIGNAL CONFIRMÉ' if confirmed else '❌ SIGNAL NON CONFIRMÉ'}")
    
    if not confirmed:
        print("⚠️ Signal trop faible - Attendre confirmation")
    confirmed, score, confirmations = advanced_direction_confirmation(df, "HAUSSIER")
    print_confirmation_results(confirmations, score, confirmed)
