# app/engine/confirmation.py

import pandas as pd


def check_direction_confirmation(df, direction, pip):
    """
    Confirmation multi-niveaux :
    1. Bougies consécutives
    2. EMA 9
    3. Structure HH/HL ou LH/LL
    4. Super Trend (dernier recours)
    """
    try:
        close  = df["close"]
        open_  = df["open"]
        high   = df["high"]
        low    = df["low"]

        # ============ ATR ============
        atr = (high - low).rolling(14).mean().iloc[-1]
        if atr <= 0:
            return False, "ATR_INVALID"

        # ============ EMA 9 ============
        ema9 = close.ewm(span=9, adjust=False).mean()
        price     = close.iloc[-1]
        ema_value = ema9.iloc[-1]

        ema_bullish = price > ema_value
        ema_bearish = price < ema_value

        # ============ BOUGIES ============
        # Taille des 3 dernières bougies
        bodies = [
            abs(close.iloc[-i] - open_.iloc[-i])
            for i in range(1, 4)
        ]

        # Couleur des 3 dernières bougies
        bull = [close.iloc[-i] > open_.iloc[-i] for i in range(1, 4)]
        bear = [close.iloc[-i] < open_.iloc[-i] for i in range(1, 4)]

        # ============ STRUCTURE ============
        # Higher High / Higher Low = HAUSSIER
        # Lower High / Lower Low   = BAISSIER
        hh = high.iloc[-1] > high.iloc[-2] > high.iloc[-3]
        hl = low.iloc[-1]  > low.iloc[-2]  > low.iloc[-3]
        lh = high.iloc[-1] < high.iloc[-2] < high.iloc[-3]
        ll = low.iloc[-1]  < low.iloc[-2]  < low.iloc[-3]

        structure_bullish = hh and hl
        structure_bearish = lh and ll

        # ============ SUPER TREND ============
        st_bullish, st_bearish = compute_st_signal(df)

        # ============ SCORE DE CONFIRMATION ============
        score = 0
        reasons = []

        if direction == "HAUSSIER":

            # 1. Grande bougie verte (1 suffit)
            if bull[0] and bodies[0] >= atr * 1.2:
                score += 40
                reasons.append("BIG_GREEN_CANDLE")

            # 2. Deux bougies vertes moyennes
            elif bull[0] and bull[1] and bodies[0] >= atr * 0.5 and bodies[1] >= atr * 0.5:
                score += 30
                reasons.append("2_GREEN_CANDLES")

            # 3. Trois petites bougies vertes
            elif bull[0] and bull[1] and bull[2] and all(b >= atr * 0.3 for b in bodies):
                score += 20
                reasons.append("3_GREEN_CANDLES")

            # EMA
            if ema_bullish:
                score += 25
                reasons.append("EMA_OK")

            # Structure
            if structure_bullish:
                score += 20
                reasons.append("HH_HL")

            # Super Trend
            if st_bullish:
                score += 15
                reasons.append("ST_GREEN")

        else:  # BAISSIER

            # 1. Grande bougie rouge (1 suffit)
            if bear[0] and bodies[0] >= atr * 1.2:
                score += 40
                reasons.append("BIG_RED_CANDLE")

            # 2. Deux bougies rouges moyennes
            elif bear[0] and bear[1] and bodies[0] >= atr * 0.5 and bodies[1] >= atr * 0.5:
                score += 30
                reasons.append("2_RED_CANDLES")

            # 3. Trois petites bougies rouges
            elif bear[0] and bear[1] and bear[2] and all(b >= atr * 0.3 for b in bodies):
                score += 20
                reasons.append("3_RED_CANDLES")

            # EMA
            if ema_bearish:
                score += 25
                reasons.append("EMA_OK")

            # Structure
            if structure_bearish:
                score += 20
                reasons.append("LH_LL")

            # Super Trend
            if st_bearish:
                score += 15
                reasons.append("ST_RED")

        # ============ DÉCISION FINALE ============
        # Minimum requis : bougies + EMA (sans ST obligatoire)
        has_candle_signal = any(r in reasons for r in [
            "BIG_GREEN_CANDLE", "BIG_RED_CANDLE",
            "2_GREEN_CANDLES",  "2_RED_CANDLES",
            "3_GREEN_CANDLES",  "3_RED_CANDLES"
        ])

        has_ema = "EMA_OK" in reasons

        # ✅ Confirmé si :
        # Score >= 55 ET (bougies confirmées OU EMA confirmée)
        confirmed = score >= 55 and (has_candle_signal or has_ema)

        return confirmed, {
            "score"   : score,
            "reasons" : reasons,
            "type"    : reasons[0] if reasons else "WAITING"
        }

    except Exception as e:
        # Erreur silencieuse - pas de print pour éviter le spam
        return False, {"score": 0, "reasons": [], "type": "ERROR"}


def compute_st_signal(df, period=10, multiplier=3):
    """Super Trend signal simplifié"""
    try:
        high  = df["high"]
        low   = df["low"]
        close = df["close"]

        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low  - close.shift()).abs()
        ], axis=1).max(axis=1)

        atr = tr.rolling(period).mean()

        upper = (high + low) / 2 + multiplier * atr
        lower = (high + low) / 2 - multiplier * atr

        # Direction ST
        st_dir = pd.Series(0, index=df.index)

        for i in range(1, len(df)):
            if close.iloc[i] > upper.iloc[i - 1]:
                st_dir.iloc[i] = 1
            elif close.iloc[i] < lower.iloc[i - 1]:
                st_dir.iloc[i] = -1
            else:
                st_dir.iloc[i] = st_dir.iloc[i - 1]

        return st_dir.iloc[-1] == 1, st_dir.iloc[-1] == -1

    except Exception:
        return False, False