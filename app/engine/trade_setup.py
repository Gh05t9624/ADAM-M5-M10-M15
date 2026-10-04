# app/engine/trade_setup.py

from datetime import datetime

def is_valid_price(x):
    return isinstance(x, (int, float)) and x > 0


def get_adaptive_sl_tp(symbol, direction, analysis=None):
    """
    Retourne le SL/TP adaptatif basé sur l'apprentissage du journal de trade
    
    Args:
        symbol: Symbole du marché
        direction: Direction du trade (HAUSSIER/BAISSIER)
        analysis: Analyse du marché (optionnel)
    
    Returns:
        tuple: (sl_pips, tp_pips)
    """
    try:
        from app.utils.trade_learning import get_optimal_sl_tp
        
        # Obtenir les paramètres optimaux depuis l'apprentissage
        optimal = get_optimal_sl_tp(symbol, direction)
        
        if optimal['confidence'] > 0.5:
            # Utiliser les paramètres appris
            sl_pips = optimal['sl']
            tp_pips = optimal['tp']
            return sl_pips, tp_pips
        else:
            # Utiliser les valeurs par défaut adaptées
            return get_default_sl_tp(symbol)
    except Exception as e:
        # En cas d'erreur, utiliser les valeurs par défaut
        return get_default_sl_tp(symbol)


def get_default_sl_tp(symbol):
    """
    Retourne les SL/TP par défaut adaptés au marché
    
    Args:
        symbol: Symbole du marché
    
    Returns:
        tuple: (sl_pips, tp_pips)
    """
    # Valeurs par défaut selon le type de marché
    if "XAU" in symbol or "GOLD" in symbol:
        # XAU: SL = 300 points (30$), TP = 600 points (60$)
        return 300.0, 600.0
    elif "JPY" in symbol:
        # JPY: SL = 30 pips, TP = 60 pips
        return 30.0, 60.0
    else:
        # FOREX standard: SL = 30 pips, TP = 60 pips
        return 30.0, 60.0


def compute_smart_tp(df, analysis):
    try:
        high   = df["high"]
        low    = df["low"]
        symbol = analysis.get("symbol", "EURUSD")

        # ATR simplifié sur 14 périodes
        atr = (high - low).rolling(14).mean().iloc[-1]

        if atr is None or atr <= 0:
            return None

        # Intelligence marché
        impulse  = analysis.get("impulse_strength", 0)
        trend    = analysis.get("trend_continuation", False)
        pullback = analysis.get("pullback_active", False)

        # Multiplicateur selon contexte
        if trend and impulse > 1.5:
            multiplier = 2.0
        elif impulse > 1.2:
            multiplier = 1.5
        elif pullback:
            multiplier = 1.2
        else:
            multiplier = 0.8

        tp_pips = atr * multiplier

        # ✅ Limites dynamiques selon symbole basées sur l'ATR
        if "JPY" in symbol:
            # JPY: TP entre 0.8x et 3x l'ATR
            tp_pips = max(atr * 0.8, min(atr * 3.0, tp_pips))
        elif "XAU" in symbol or "GOLD" in symbol:
            # Paramètres spécifiques par paire XAU selon leur volatilité
            if "XAUAUD" in symbol:
                # XAUAUD: plus volatil, TP entre 1.0x et 4x l'ATR
                tp_pips = max(atr * 1.0, min(atr * 4.0, tp_pips))
            elif "XAUGBP" in symbol:
                # XAUGBP: volatilité moyenne, TP entre 1.2x et 3.5x l'ATR
                tp_pips = max(atr * 1.2, min(atr * 3.5, tp_pips))
            elif "XAUCHF" in symbol:
                # XAUCHF: moins volatil, TP entre 1.5x et 3x l'ATR
                tp_pips = max(atr * 1.5, min(atr * 3.0, tp_pips))
            else:  # XAUUSD par défaut
                # XAUUSD: volatilité standard, TP entre 1.5x et 3x l'ATR
                tp_pips = max(atr * 1.5, min(atr * 3.0, tp_pips))
        else:
            # Autres paires: TP entre 0.8x et 2.5x l'ATR
            tp_pips = max(atr * 0.8, min(atr * 2.5, tp_pips))

        return tp_pips

    except:
        return None


def generate_trade_plan_multi(analysis, min_score=55):

    plans   = []
    df        = analysis.get("df")
    direction = analysis.get("direction")
    symbol    = analysis.get("symbol", "EURUSD")
    zone      = analysis.get("zone", {})
    score     = analysis.get("score", 0)

    if df is None or direction not in ["HAUSSIER", "BAISSIER"]:
        return None

    last_price = df["close"].iloc[-1]

    zone_low  = zone.get("low")
    zone_high = zone.get("high")

    if not is_valid_price(zone_low) or not is_valid_price(zone_high):
        zone_low  = last_price
        zone_high = last_price

    # ✅ Pip selon symbole avec conversion FOREX/XAU
    if "JPY" in symbol:
        pip = 0.01
    elif "XAU" in symbol or "GOLD" in symbol:
        pip = 0.1
    else:
        pip = 0.0001
    
    # ✅ SL/TP adaptatifs basés sur l'apprentissage
    adaptive_sl_pips, adaptive_tp_pips = get_adaptive_sl_tp(symbol, direction, analysis)
    
    # Convertir en points selon le type de marché
    if "XAU" in symbol or "GOLD" in symbol:
        xau_sl_points = adaptive_sl_pips * pip  # points XAU
        xau_tp_points = adaptive_tp_pips * pip  # points XAU
    else:
        xau_sl_points = adaptive_sl_pips * pip  # points FOREX
        xau_tp_points = adaptive_tp_pips * pip  # points FOREX

    # TP intelligent avec fallback
    smart_tp = compute_smart_tp(df, analysis)
    if smart_tp is None or smart_tp <= 0:
        smart_tp = 30 * pip

    # ================= TREND CONTINUATION =================
    if analysis.get("trend_continuation"):
        entry = last_price
        # 🎯 SL/TP adaptatifs basés sur l'apprentissage
        sl = entry - xau_sl_points if direction == "HAUSSIER" else entry + xau_sl_points
        tp = entry + smart_tp if direction == "HAUSSIER" else entry - smart_tp

        plans.append({
            "type"      : "TREND",
            "direction" : direction,
            "entry"     : entry,
            "entry_type": "MARKET",
            "sl"        : sl,
            "tp"        : tp,
            "score"     : score + 5
        })

    # ================= PULLBACK SOFT =================
    if analysis.get("pullback_active") or analysis.get("trend_continuation"):
        entry = zone_low if direction == "HAUSSIER" else zone_high
        # 🎯 SL/TP adaptatifs basés sur l'apprentissage
        sl = entry - xau_sl_points if direction == "HAUSSIER" else entry + xau_sl_points
        tp = entry + smart_tp if direction == "HAUSSIER" else entry - smart_tp

        plans.append({
            "type"      : "PULLBACK",
            "direction" : direction,
            "entry"     : entry,
            "entry_type": "LIMIT",
            "sl"        : sl,
            "tp"        : tp,
            "score"     : score
        })

    # ================= MICRO BREAKOUT =================
    if analysis.get("has_impulse"):
        entry = last_price
        # 🎯 SL/TP adaptatifs basés sur l'apprentissage
        sl = entry - xau_sl_points if direction == "HAUSSIER" else entry + xau_sl_points
        tp = entry + smart_tp if direction == "HAUSSIER" else entry - smart_tp

        plans.append({
            "type"      : "MICRO_BREAKOUT",
            "direction" : direction,
            "entry"     : entry,
            "entry_type": "MARKET",
            "sl"        : sl,
            "tp"        : tp,
            "score"     : score * 0.8
        })

    # ================= FALLBACK TRADE =================
    if not plans and score >= 50:
        entry = last_price
        # 🎯 SL/TP adaptatifs basés sur l'apprentissage
        sl = entry - xau_sl_points if direction == "HAUSSIER" else entry + xau_sl_points
        tp = entry + smart_tp if direction == "HAUSSIER" else entry - smart_tp

        plans.append({
            "type"      : "FALLBACK",
            "direction" : direction,
            "entry"     : entry,
            "entry_type": "MARKET",
            "sl"        : sl,
            "tp"        : tp,
            "score"     : score * 0.7
        })

    if not plans:
        return None

    best = max(plans, key=lambda x: x["score"])

    if best["score"] < min_score:
        return None

    if not all(map(is_valid_price, [best["entry"], best["sl"], best["tp"]])):
        return None

    # Calcul RR
    sl_pips = abs(best["entry"] - best["sl"]) / pip
    tp_pips = abs(best["tp"]    - best["entry"]) / pip
    rr      = round(tp_pips / sl_pips, 2) if sl_pips > 0 else 0

    return {
        "type"      : best["type"],
        "direction" : best["direction"],
        "symbol"    : symbol,           # ✅ AJOUTÉ
        "entry"     : round(best["entry"], 5),
        "entry_type": best["entry_type"],
        "sl"        : round(best["sl"],    5),
        "tp"        : round(best["tp"],    5),
        "rr"        : rr,
        "score"     : int(best["score"]),
        "reason"    : best["type"],
        "created_at": datetime.utcnow()  # ✅ Timestamp de création du trade plan
    }