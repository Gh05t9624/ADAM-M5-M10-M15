import pandas as pd
import numpy as np

def detect_swings(df, lookback=3):
    """Détecte les sommets et creux en utilisant High et Low."""
    highs, lows = [], []
    
    # On parcourt le dataframe en évitant les bords pour le lookback
    for i in range(lookback, len(df) - lookback):
        # Un sommet : le High est le plus haut du voisinage
        window_high = df['high'].iloc[i - lookback : i + lookback + 1]
        if df['high'].iloc[i] == window_high.max():
            highs.append((i, df['high'].iloc[i]))

        # Un creux : le Low est le plus bas du voisinage
        window_low = df['low'].iloc[i - lookback : i + lookback + 1]
        if df['low'].iloc[i] == window_low.min():
            lows.append((i, df['low'].iloc[i]))

    return highs, lows

def market_direction(highs, lows):
    """Détermine la tendance selon la théorie de Dow (HH/HL ou LH/LL)."""
    if len(highs) < 2 or len(lows) < 2:
        return "NEUTRE"

    # Récupération des deux derniers points pour comparaison
    last_h, prev_h = highs[-1][1], highs[-2][1]
    last_l, prev_l = lows[-1][1], lows[-2][1]

    # Analyse de la structure
    is_hh = last_h > prev_h  # Higher High
    is_hl = last_l > prev_l  # Higher Low
    is_lh = last_h < prev_h  # Lower High
    is_ll = last_l < prev_l  # Lower Low

    # Cas 1 : Tendance haussière confirmée (HH + HL)
    if is_hh and is_hl:
        return "HAUSSIER"
    
    # Cas 2 : Tendance baissière confirmée (LH + LL)
    if is_lh and is_ll:
        return "BAISSIER"

    # Cas 3 : Transition ou indécision (on regarde le dernier mouvement)
    if is_hh: return "HAUSSIER"
    if is_ll: return "BAISSIER"

    return "NEUTRE"

def smooth_direction(raw_direction, previous_direction, df=None):
    """Lissage par EMA pour éviter les faux signaux en range."""
    if raw_direction in ["HAUSSIER", "BAISSIER"]:
        return raw_direction

    if df is not None and not df.empty:
        try:
            # Calcul d'une EMA courte (9) pour la réactivité
            ema9 = df['close'].ewm(span=9, adjust=False).mean().iloc[-1]
            current_price = df['close'].iloc[-1]

            # Si le prix est franchement au-dessus/en-dessous de l'EMA, on maintient ou définit la tendance
            if current_price > ema9:
                return "HAUSSIER"
            elif current_price < ema9:
                return "BAISSIER"
        except Exception as e:
            print(f"Erreur Smooth: {e}")

    return previous_direction if previous_direction else "NEUTRE"
