# app/engine/pullback.py

def last_impulse_zone(highs, lows, direction):
    """
    Retourne une vraie zone structurelle (low/high)
    basée sur le dernier swing cassé
    """

    if direction == "HAUSSIER" and len(lows) >= 2:
        low = lows[-2][1]
        high = lows[-1][1]
        return {"low": min(low, high), "high": max(low, high)}

    if direction == "BAISSIER" and len(highs) >= 2:
        high = highs[-2][1]
        low = highs[-1][1]
        return {"low": min(low, high), "high": max(low, high)}

    return {"low": None, "high": None}


def is_pullback_active(df, zone, direction, tolerance_pips=10):
    """
    Vérifie si le prix est dans la zone de pullback
    (tolérance en pips, plus réaliste que %)
    """

    if not zone or zone["low"] is None or zone["high"] is None:
        return False

    last_price = df['close'].iloc[-1]

    # estimation pip dynamique
    pip = 0.0001
    tolerance = tolerance_pips * pip

    if direction == "HAUSSIER":
        return zone["low"] - tolerance <= last_price <= zone["high"] + tolerance

    if direction == "BAISSIER":
        return zone["low"] - tolerance <= last_price <= zone["high"] + tolerance

    return False


def pullback_validated(df, zone, direction):
    """
    Validation du rejet du pullback (price action simple)
    """

    if len(df) < 3:
        return False

    c1 = df["close"].iloc[-3]
    c2 = df["close"].iloc[-2]
    c3 = df["close"].iloc[-1]

    if direction == "HAUSSIER":
        # rejet haussier
        return c3 > c2 and c2 <= c1

    if direction == "BAISSIER":
        # rejet baissier
        return c3 < c2 and c2 >= c1

    return False