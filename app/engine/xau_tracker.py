import pandas as pd
import numpy as np

class XAU_Multi_Pair_Engine:
    def __init__(self, symbol="XAUUSD"):
        self.name = "GH05T XAU MULTI-PAIR"
        self.symbol = symbol

    # ================================
    # VOLATILITÉ RÉELLE (ATR)
    # ================================
    def compute_atr(self, df, period=14):
        high = df['high']
        low = df['low']
        close = df['close']

        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()

        return atr.iloc[-1]

    # ================================
    # DÉTECTION DE MARCHÉ
    # ================================
    def detect_market_type(self, df):
        recent_high = df['high'].tail(20).max()
        recent_low = df['low'].tail(20).min()
        current_price = df['close'].iloc[-1]

        range_size = recent_high - recent_low

        if range_size < 15:
            return "RANGE"
        else:
            return "TREND"

    # ================================
    # DIRECTION
    # ================================
    def get_direction(self, df):
        ema50 = df['close'].ewm(span=50).mean()
        ema200 = df['close'].ewm(span=200).mean()

        if ema50.iloc[-1] > ema200.iloc[-1]:
            return "BUY"
        else:
            return "SELL"

    # ================================
    # SL / TP INTELLIGENT
    # ================================
    def compute_levels(self, df):
        atr = self.compute_atr(df)

        price = df['close'].iloc[-1]
        direction = self.get_direction(df)

        # 🔥 Paramètres spécifiques par paire XAU selon leur volatilité
        if self.symbol == "XAUAUD":
            # XAUAUD: plus volatil
            atr_multiplier_sl = 1.2
            atr_multiplier_tp = 2.5
            base_sl_points = 350.0  # points
            base_tp_points = 700.0  # points
        elif self.symbol == "XAUGBP":
            # XAUGBP: volatilité moyenne
            atr_multiplier_sl = 1.5
            atr_multiplier_tp = 3.0
            base_sl_points = 300.0  # points
            base_tp_points = 600.0  # points
        elif self.symbol == "XAUCHF":
            # XAUCHF: moins volatil
            atr_multiplier_sl = 1.8
            atr_multiplier_tp = 3.5
            base_sl_points = 280.0  # points
            base_tp_points = 560.0  # points
        else:  # XAUUSD par défaut
            # XAUUSD: volatilité standard
            atr_multiplier_sl = 1.5
            atr_multiplier_tp = 3.0
            base_sl_points = 300.0  # points
            base_tp_points = 600.0  # points

        # SL/TP basés sur l'ATR adapté à la paire
        atr_sl = atr * atr_multiplier_sl
        atr_tp = atr * atr_multiplier_tp

        # Utiliser le plus grand entre ATR et base fixe
        sl_distance = max(base_sl_points, atr_sl)
        tp_distance = max(base_tp_points, atr_tp)

        if direction == "BUY":
            sl = price - sl_distance
            tp = price + tp_distance
        else:
            sl = price + sl_distance
            tp = price - tp_distance

        return {
            "entry": price,
            "sl": round(sl, 2),
            "tp": round(tp, 2),
            "atr": round(atr, 2),
            "symbol": self.symbol,
            "atr_multiplier_sl": atr_multiplier_sl,
            "atr_multiplier_tp": atr_multiplier_tp,
            "xau_sl_points": round(sl_distance, 2),
            "xau_tp_points": round(tp_distance, 2)
        }

    # ================================
    # STRATÉGIE ADAM (TON STYLE)
    # ================================
    def adam_strategy(self, df):
        market = self.detect_market_type(df)
        levels = self.compute_levels(df)
        direction = self.get_direction(df)

        if market == "RANGE":
            signal = "WAIT ⚠️ (marché en compression)"
        else:
            signal = f"{direction} ✅ (cassure probable)"

        return {
            "signal": signal,
            "entry": levels["entry"],
            "sl": levels["sl"],
            "tp": levels["tp"],
            "atr": levels["atr"],
            "market_type": market
        }

# ================================
# UTILISATION
# ================================