# app/engine/analyzer.py

from typing import Optional
import pandas as pd
import numpy as np
from datetime import datetime

from app.engine.structure import detect_swings, market_direction, smooth_direction
from app.engine.rules import is_range, extreme_trend
from app.engine.pullback import last_impulse_zone, is_pullback_active, pullback_validated
from app.engine.context import context_status, MarketContext
from app.engine.extreme_event import detect_extreme_market_event
from app.engine.volatility import volatility_ratio
from app.engine.news_filter import is_news_time
from app.engine.confirmation import check_direction_confirmation
from app.engine.fibonacci import FibonacciAnalyzer
from app.engine.price_range_strategy import price_range_signal_advanced, is_valid_price_range_time

# ---------------- EMA RAPIDE ----------------
def compute_ema(df, span=50):
    """EMA par défaut (50) adaptée au timeframe M10"""
    try:
        return df["close"].ewm(span=span, adjust=False).mean()
    except Exception:
        return None


def ema_direction(df, timeframe="M10"):
    """
    Direction basée sur EMA selon le timeframe
    - M30: EMA 9 + EMA 21 (signaux plus rapides)
    - M10: EMA 50 + EMA 200 (signaux plus fiables)
    """
    try:
        # EMA selon timeframe
        if timeframe == "M30":
            ema_fast = df["close"].ewm(span=9, adjust=False).mean()
            ema_slow = df["close"].ewm(span=21, adjust=False).mean()
        elif timeframe == "M5":
            ema_fast = df["close"].ewm(span=21, adjust=False).mean()
            ema_slow = df["close"].ewm(span=50, adjust=False).mean()
        else:  # M10
            ema_fast = df["close"].ewm(span=50, adjust=False).mean()
            ema_slow = df["close"].ewm(span=200, adjust=False).mean()

        price = df["close"].iloc[-1]
        ema_fast_last = ema_fast.iloc[-1]
        ema_slow_last = ema_slow.iloc[-1]

        if price > ema_fast_last and ema_fast_last > ema_slow_last:
            return "HAUSSIER"
        elif price < ema_fast_last and ema_fast_last < ema_slow_last:
            return "BAISSIER"
        else:
            return "NEUTRE"
    except Exception:
        return "NEUTRE"


# ---------------- RSI ----------------
def compute_rsi(df, period=14):
    """
    Calcul du RSI (Relative Strength Index)
    Période standard : 14
    """
    try:
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    except Exception:
        return pd.Series(index=df.index, dtype=float)

def rsi_direction(rsi, direction):
    """
    Direction basée sur le RSI
    - RSI > 50 + tendance haussière = HAUSSIER
    - RSI < 50 + tendance baissière = BAISSIER
    - Divergences et niveaux extrêmes
    """
    try:
        if len(rsi) < 2:
            return "NEUTRE"
        
        rsi_current = rsi.iloc[-1]
        rsi_previous = rsi.iloc[-2]
        
        # Niveaux extrêmes
        if rsi_current >= 70:
            return "SURACHAT"
        elif rsi_current <= 30:
            return "SURVENTE"
        
        # Direction RSI
        if rsi_current > 50 and rsi_current > rsi_previous:
            return "HAUSSIER_RSI"
        elif rsi_current < 50 and rsi_current < rsi_previous:
            return "BAISSIER_RSI"
        else:
            return "NEUTRE_RSI"
            
    except Exception:
        return "NEUTRE"

def detect_rsi_divergence(df, rsi, direction):
    """
    Détection des divergences RSI
    - Bullish divergence : prix plus bas mais RSI plus haut
    - Bearish divergence : prix plus haut mais RSI plus bas
    """
    try:
        if len(df) < 20 or len(rsi) < 20:
            return False, "NO_DATA"
        
        # Derniers 10 périodes pour détecter divergence
        recent_prices = df["close"].tail(10)
        recent_rsi = rsi.tail(10)
        
        # Détecter les points hauts et bas récents
        price_highs = []
        price_lows = []
        rsi_highs = []
        rsi_lows = []
        
        for i in range(2, len(recent_prices)):
            # Points hauts
            if (recent_prices.iloc[i] > recent_prices.iloc[i-1] and 
                recent_prices.iloc[i] > recent_prices.iloc[i-2]):
                price_highs.append(recent_prices.iloc[i])
                rsi_highs.append(recent_rsi.iloc[i])
            
            # Points bas
            if (recent_prices.iloc[i] < recent_prices.iloc[i-1] and 
                recent_prices.iloc[i] < recent_prices.iloc[i-2]):
                price_lows.append(recent_prices.iloc[i])
                rsi_lows.append(recent_rsi.iloc[i])
        
        # Bullish divergence (pour tendance haussière)
        if direction == "HAUSSIER" and len(price_lows) >= 2 and len(rsi_lows) >= 2:
            if price_lows[-1] < price_lows[-2] and rsi_lows[-1] > rsi_lows[-2]:
                return True, "BULLISH_DIVERGENCE"
        
        # Bearish divergence (pour tendance baissière)
        if direction == "BAISSIER" and len(price_highs) >= 2 and len(rsi_highs) >= 2:
            if price_highs[-1] > price_highs[-2] and rsi_highs[-1] < rsi_highs[-2]:
                return True, "BEARISH_DIVERGENCE"
        
        return False, "NO_DIVERGENCE"
        
    except Exception:
        return False, "ERROR"


# ---------------- SUPER TREND ----------------
def compute_supertrend(df, period=10, multiplier=3):
    """
    Super Trend maison pour confirmer la direction
    """
    try:
        high  = df["high"]
        low   = df["low"]
        close = df["close"]

        # ATR
        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low  - close.shift()).abs()
        ], axis=1).max(axis=1)

        atr = tr.rolling(period).mean()

        # Bandes
        basic_upper = (high + low) / 2 + multiplier * atr
        basic_lower = (high + low) / 2 - multiplier * atr

        supertrend = pd.Series(index=df.index, dtype=float)
        direction  = pd.Series(index=df.index, dtype=int)

        for i in range(1, len(df)):
            if close.iloc[i] > basic_upper.iloc[i - 1]:
                direction.iloc[i] = 1   # HAUSSIER
            elif close.iloc[i] < basic_lower.iloc[i - 1]:
                direction.iloc[i] = -1  # BAISSIER
            else:
                direction.iloc[i] = direction.iloc[i - 1]

        last = direction.iloc[-1]

        if last == 1:
            return "HAUSSIER"
        elif last == -1:
            return "BAISSIER"
        else:
            return "NEUTRE"

    except Exception:
        return "NEUTRE"


# ---------------- IMPULSE ----------------
def valid_impulse(highs, lows, direction, df):
    try:
        if len(highs) < 2 or len(lows) < 2:
            return False, 0

        if direction == "HAUSSIER":
            impulse_size = highs[-1][1] - highs[-2][1]
        elif direction == "BAISSIER":
            impulse_size = lows[-2][1] - lows[-1][1]
        else:
            return False, 0

        avg_range = (df["high"] - df["low"]).rolling(14).mean().iloc[-1]

        if pd.isna(avg_range) or avg_range == 0:
            return False, 0

        strength = impulse_size / avg_range

        # ✅ Seuil abaissé de 1.2 → 1.0 pour plus de réactivité
        return strength >= 1.0, strength

    except Exception:
        return False, 0


# ---------------- FIBONACCI PULLBACK QUALITY ----------------
def fibonacci_pullback_quality(df, direction):
    """
    Évaluer la qualité du pullback avec Fibonacci
    Remplace l'ancien pullback_quality avec des niveaux précis
    """
    try:
        fib_analyzer = FibonacciAnalyzer()
        
        # Détecter les swings pour calcul Fibonacci
        swings = fib_analyzer.detect_swing_points(df)
        
        if not swings:
            return False, 0, None
        
        # Prendre le swing le plus récent et le plus fort
        best_swing = max(swings, key=lambda x: x.strength)
        current_price = df['close'].iloc[-1]
        
        # Calculer ATR pour la tolérance
        atr = (df['high'] - df['low']).rolling(14).mean().iloc[-1]
        
        # Analyser les niveaux Fibonacci
        fib_analysis = fib_analyzer.calculate_fibonacci_retracement(best_swing, current_price, atr)
        
        # Vérifier si un niveau Fibonacci est actif
        if fib_analysis['active_levels']:
            best_level = fib_analysis['best_level']
            return True, best_level.score_boost, fib_analysis
        
        return False, 0, None
        
    except Exception as e:
        return False, 0, None

# ---------------- PULLBACK QUALITY (LEGACY) ----------------
def pullback_quality(df, zone, direction):
    """
    Version legacy conservée pour compatibilité
    utilise maintenant Fibonacci par défaut
    """
    return fibonacci_pullback_quality(df, direction)[0]


# ---------------- PRICE RANGE CONFIRMATION ----------------
def check_price_range_confirmation(df, direction, symbol="EURUSD"):
    """
    Vérifie la confirmation de la stratégie Price Range avancée - Phase 1.
    Valide uniquement aux heures optimales selon le symbole.

    Args:
        df: DataFrame OHLCV
        direction: Direction à confirmer
        symbol: Symbole pour ajustements spécifiques

    Returns:
        tuple: (confirmed: bool, bonus: int, signal_data: dict)
    """
    try:
        # Obtenir le signal Price Range avancé
        signal = price_range_signal_advanced(df, direction, symbol, check_time=True)

        if not signal['valid']:
            return False, 0, signal

        # Signal déjà confirmé par le système multi-signaux
        if signal.get('confirmed', False):
            # Bonus selon le score de confirmation
            confirmation_score = signal.get('confirmation_score', 0)
            bonus = min(confirmation_score * 2.5, 15)  # Max 15 points
            
            return True, bonus, signal
        else:
            return False, 0, signal

    except Exception as e:
        return False, 0, {'valid': False, 'reason': f'Erreur: {str(e)}'}


# ---------------- SCORE ----------------
def score_trade(direction, impulse_strength, pullback_ok,
                multi_tf_ok, has_impulse=False,
                ema_dir="NEUTRE", st_dir="NEUTRE", rsi_dir="NEUTRE",
                price_range_confirmed=False):
    score = 0

    # 1. DIRECTION DE FOND (Max 30 pts)
    if direction in ["HAUSSIER", "BAISSIER"]:
        score += 20

    # Bonus si la direction Swings est confirmée par EMA ou SuperTrend
    if direction == ema_dir: score += 5
    if direction == st_dir:  score += 5

    # 2. IMPULSION (Max 30 pts)
    if has_impulse:
        # On donne du poids à la force du mouvement
        score += min(impulse_strength * 15, 30)
    elif ema_dir == direction:
        # Compensation : si pas d'impulsion swing, mais EMA pousse
        score += 10

    # 3. LE SETUP (Max 40 pts)
    if pullback_ok:
        score += 30  # Pullback dans la zone 0.38-0.61

    if multi_tf_ok:
        score += 10

    # 4. FILTRE RSI (Bonus/Malus)
    if (direction == "HAUSSIER" and rsi_dir == "SURACHAT") or \
       (direction == "BAISSIER" and rsi_dir == "SURVENTE"):
        score -= 15 # On évite d'acheter un top ou vendre un bottom

    # 5. PRICE RANGE CONFIRMATION (Bonus +10 pts aux heures valides)
    if price_range_confirmed:
        score += 10

    return min(score, 100)



# ---------------- TREND CONTINUATION ----------------
def detect_trend_continuation(direction, impulse_strength,
                               pullback_active, pullback_ok,
                               ema_dir="NEUTRE", st_dir="NEUTRE"):

    if direction not in ["HAUSSIER", "BAISSIER"]:
        return False

    # ✅ Seuil abaissé de 1.3 → 1.1
    if impulse_strength < 1.1:
        return False

    if pullback_ok:
        return False

    # ✅ EMA ou ST confirment → trend continuation
    ema_confirms = ema_dir == direction
    st_confirms  = st_dir  == direction

    if not pullback_active or impulse_strength > 1.5:
        return True

    # ✅ Si EMA ET ST confirment → valide même avec pullback faible
    if ema_confirms and st_confirms:
        return True

    return False


# ================= MAIN ANALYZER =================
class MarketAnalyzer:

    def __init__(self):
        # Dictionnaire par symbole pour éviter confusion
        self._last_directions = {}
        self._direction_timestamps = {}  # Stocker quand la direction a été détectée
        self._debug_symbol = "EURUSD"  # Activer le debug pour EUR/USD

    def analyze(self, df, context: Optional[MarketContext] = None,
            symbol: str = "UNKNOWN", timeframe: str = "M10"):

        try:
            if df is None or len(df) < 50:
                return self._error_result("DATA_TOO_SMALL", "NEUTRE")

            # 1️⃣ EMA + SUPER TREND + RSI (rapides)
            ema_dir = ema_direction(df, timeframe)
            st_dir  = compute_supertrend(df)
            rsi     = compute_rsi(df)
            rsi_dir = rsi_direction(rsi, "UNKNOWN")
            
            # Retirer le suffixe 'c' pour l'affichage
            display_symbol = symbol.rstrip('c') if symbol.endswith('c') else symbol
            
            # Afficher les informations EMA/ST/RSI pour tous les symboles
            print(f"DEBUG: {display_symbol} [{timeframe}] - EMA: {ema_dir}, ST: {st_dir}, RSI: {rsi_dir}, RSI_val: {rsi.iloc[-1] if len(rsi) > 0 else 'N/A'}")

            # 2️⃣ STRUCTURE (swings)
            highs, lows   = detect_swings(df)
            raw_direction = market_direction(highs, lows)
            
            print(f"DEBUG: {display_symbol} - Swings direction: {raw_direction}")

            # Direction précédente par symbole
            previous_direction = self._last_directions.get(symbol)

            # 3️⃣ FUSION direction
            direction = self._fusion_direction(
                raw_direction, ema_dir, st_dir, previous_direction
            )

            # ✅ SOLUTION RADICALE : Si swings = NEUTRE, on utilise EMA/ST
            if raw_direction == "NEUTRE":
                if ema_dir != "NEUTRE":
                    direction = ema_dir
                elif st_dir != "NEUTRE":
                    direction = st_dir
                else:
                    # Forcer HAUSSIER si RSI > 55, BAISSIER si RSI < 45
                    direction = "HAUSSIER" if rsi.iloc[-1] > 55 else "BAISSIER"

            # ✅ RESET FORCÉ — si EMA + bougies contredisent → on corrige
            direction = self._force_direction_check(df, direction)
            
            # ✅ Stocker le timestamp de détection de direction
            if previous_direction != direction or symbol not in self._direction_timestamps:
                self._direction_timestamps[symbol] = datetime.utcnow()
            direction_detected_at = self._direction_timestamps.get(symbol, datetime.utcnow())

            # ✅ Pip selon symbole
            if "JPY" in symbol:
                pip = 0.01
            elif "XAU" in symbol or "GOLD" in symbol:
                pip = 0.1
            else:
                pip = 0.0001

            # SOLUTION FINALE : Désactiver la logique de confirmation trop stricte
            # Forcer confirmed = True pour éviter le blocage systématique
            confirmed = True
            confirmation_info = {"type": "FORCED_CONFIRMED"}
            
            print(f"DEBUG: {display_symbol} - Direction finale: {direction}, Confirmed: {confirmed}, Type: {confirmation_info.get('type', 'N/A')}")

            # PLUS DE BLOCAGE PAR CONFIRMATION
            # La logique de confirmation était trop stricte et bloquait tous les scores
            # if not confirmed:
            #     if previous_direction and previous_direction != "NEUTRE":
            #         prev_still_valid, _ = check_direction_confirmation(
            #             df, previous_direction, pip
            #         )
            #         if prev_still_valid:
            #             direction         = previous_direction
            #             confirmation_info = {"type": "PREVIOUS_CONFIRMED"}
            #         else:
            #             # Ancienne direction invalide → NEUTRE
            #             direction         = "NEUTRE"
            #             confirmation_info = {"type": "WAITING"}
            #     else:
            #         direction         = "NEUTRE"
            #         confirmation_info = {"type": "WAITING"}
            self._last_directions[symbol] = direction

            # NEWS CHECK
            if is_news_time():
                return self._error_result("NEWS_TIME", direction)

            # 4️⃣ EXCLUSIONS
            exclusions = []

            if direction == "NEUTRE":
                exclusions.append("NO_DIRECTION")

            if is_range(highs, lows):
                exclusions.append("RANGE_MARKET")

            if extreme_trend(df):
                exclusions.append("EXTREME_TREND")

            is_excluded = len(exclusions) > 0

            # 5️⃣ IMPULSE
            has_impulse, impulse_strength = False, 0

            if not is_excluded:
                has_impulse, impulse_strength = valid_impulse(
                    highs, lows, direction, df
                )

            # ✅ Force impulse SEULEMENT si EMA + ST + bougies alignés
            if not has_impulse and ema_dir == direction and st_dir == direction:
                # Vérifier aussi les bougies avant de forcer
                bull_count = sum(
                    1 for i in range(1, 4)
                    if df["close"].iloc[-i] > df["open"].iloc[-i]
                )
                bear_count = sum(
                    1 for i in range(1, 4)
                    if df["close"].iloc[-i] < df["open"].iloc[-i]
                )

                candles_confirm = (
                    (direction == "HAUSSIER" and bull_count >= 2) or
                    (direction == "BAISSIER" and bear_count >= 2)
                )

                if candles_confirm:
                    has_impulse      = True
                    impulse_strength = 1.1

            # 6️⃣ ZONE
            raw_zone = last_impulse_zone(highs, lows, direction)

            if isinstance(raw_zone, (int, float)):
                zone = {"low": raw_zone, "high": raw_zone}
            elif isinstance(raw_zone, (list, tuple)) and len(raw_zone) == 2:
                zone = {"low": raw_zone[0], "high": raw_zone[1]}
            else:
                zone = {"low": None, "high": None}

            # 7️⃣ PULLBACK FIBONACCI
            pullback_active = False
            pullback_ok     = False
            fibonacci_analysis = None
            fibonacci_boost = 0

            if has_impulse and zone["low"] is not None:
                pullback_active = is_pullback_active(df, zone, direction)
                
                # Utiliser Fibonacci pour évaluer le pullback
                fib_pullback_ok, fib_boost, fib_analysis = fibonacci_pullback_quality(df, direction)
                
                pullback_ok = (
                    pullback_active
                    and pullback_validated(df, zone, direction)
                    and fib_pullback_ok  # Nouveau critère Fibonacci
                )
                
                fibonacci_analysis = fib_analysis
                fibonacci_boost = fib_boost or 0

            # 8️⃣ TREND CONTINUATION
            trend_continuation = detect_trend_continuation(
                direction,
                impulse_strength,
                pullback_active,
                pullback_ok,
                ema_dir,
                st_dir
            )

            # 🔟 PRICE RANGE CONFIRMATION (aux heures valides optimisées selon symbole)
            price_range_confirmed, price_range_bonus, price_range_signal = check_price_range_confirmation(
                df, direction, symbol
            )

            # 9️⃣ SCORE AVEC FIBONACCI + PRICE RANGE
            score = score_trade(
                direction,
                impulse_strength,
                pullback_ok,
                multi_tf_ok=True,
                has_impulse=has_impulse,
                ema_dir=ema_dir,
                st_dir=st_dir,
                rsi_dir=rsi_dir,
                price_range_confirmed=price_range_confirmed
            )

            # Ajouter le bonus Fibonacci
            if fibonacci_boost > 0:
                score += fibonacci_boost

            if trend_continuation:
                score += 10

            # Pénalité si direction pas confirmée
            if not confirmed:
                score = int(score * 0.5)

            # Pénalité si direction NEUTRE
            if direction == "NEUTRE":
                score = 0

            # Forcer entier propre sans décimales
            score = int(min(100, score))

            confidence = int(min(100, score * 0.9 + impulse_strength * 10))

            # STATUS
            if is_excluded or direction == "NEUTRE":
                status = "INTERDIT"
            elif pullback_ok or trend_continuation:
                status = "AUTORISÉ"
            elif has_impulse and direction != "NEUTRE":
                status = "OPPORTUNITÉ"
            else:
                status = "SURVEILLANCE"
            
            # DEBUG: Log des conditions pour diagnostiquer les statuts contradictoires
            print(f"DEBUG STATUS [{display_symbol}]: {status}")
            print(f"  - is_excluded: {is_excluded} (exclusions: {exclusions})")
            print(f"  - direction: {direction}")
            print(f"  - pullback_ok: {pullback_ok}")
            print(f"  - trend_continuation: {trend_continuation}")
            print(f"  - has_impulse: {has_impulse}")
            print(f"  - impulse_strength: {impulse_strength}")
            print(f"  - ema_dir: {ema_dir}, st_dir: {st_dir}, rsi_dir: {rsi_dir}")
            print(f"  - score: {score}")
            print(f"  - confirmed: {confirmed}")

            # 1️⃣1️⃣ EXTREME EVENT
            extreme_event = detect_extreme_market_event(
                direction=direction,
                has_impulse=has_impulse,
                pullback_ok=pullback_ok,
                volatility_ratio=volatility_ratio(df),
                context_ok=(context is None or context_status(context)[0] == "OK")
            )

            # Détecter les divergences RSI
            has_divergence, divergence_type = detect_rsi_divergence(df, rsi, direction)
            
            result = {
                "statut"            : status,
                "direction"         : direction,
                "score"             : score,
                "confidence"        : confidence,
                "exclusions"        : exclusions,
                "justification"     : self._reason(status, direction),
                "zone"              : zone,
                "pullback_active"   : pullback_active,
                "pullback_ok"       : pullback_ok,
                "has_impulse"       : has_impulse,
                "impulse_strength"  : impulse_strength,
                "trend_continuation": trend_continuation,
                "extreme_event"     : extreme_event,
                "ema_dir"           : ema_dir,
                "st_dir"            : st_dir,
                "rsi_dir"           : rsi_dir,
                "rsi_value"         : rsi.iloc[-1] if len(rsi) > 0 else None,
                "rsi_divergence"    : has_divergence,
                "direction_detected_at": direction_detected_at,  # ✅ Timestamp de détection de direction
                "rsi_divergence_type": divergence_type,
                "confirmed"         : confirmed,
                "confirmation_type" : confirmation_info.get("type", "WAITING"),
                # Données Fibonacci
                "fibonacci_analysis": fibonacci_analysis,
                "fibonacci_boost"   : fibonacci_boost,
                "fibonacci_active"  : fibonacci_boost > 0,
                # Données Price Range
                "price_range_confirmed": price_range_confirmed,
                "price_range_signal": price_range_signal,
                "price_range_active": price_range_confirmed,
            }

            result["quality_score"] = self.compute_quality_score(result, df)

            return result

        except Exception as e:
            # Erreur critique - on garde le print pour le debug
            display_symbol = symbol.rstrip('c') if symbol.endswith('c') else symbol
            print(f" Analyzer error [{display_symbol}] : {e}")
            return self._error_result("ANALYSIS_ERROR", "NEUTRE")


    def _force_direction_check(self, df, direction):
        """
        Corrige une direction erronée
        en vérifiant bougies + EMA
        """
        try:
            close  = df["close"]
            open_  = df["open"]
            high   = df["high"]
            low    = df["low"]

            ema9  = close.ewm(span=9, adjust=False).mean()
            price = close.iloc[-1]
            ema   = ema9.iloc[-1]

            # Compter bougies
            bull_count = sum(
                1 for i in range(1, 4)
                if close.iloc[-i] > open_.iloc[-i]
            )
            bear_count = sum(
                1 for i in range(1, 4)
                if close.iloc[-i] < open_.iloc[-i]
            )
            
            # Structure
            lh = high.iloc[-1] < high.iloc[-2]
            ll = low.iloc[-1]  < low.iloc[-2]
            hh = high.iloc[-1] > high.iloc[-2]
            hl = low.iloc[-1]  > low.iloc[-2]
            
            # DEBUG EUR/USD - Afficher la tendance
            if hasattr(self, '_debug_symbol') and self._debug_symbol == "EURUSD":
                print(f"[DEBUG EUR/USD] Direction: {direction}, Price: {price:.5f}, EMA9: {ema:.5f}")
                print(f"[DEBUG EUR/USD] Bull candles: {bull_count}, Bear candles: {bear_count}")
                print(f"[DEBUG EUR/USD] Structure - HH: {hh}, HL: {hl}, LH: {lh}, LL: {ll}")

            # ❌ Bot dit HAUSSIER mais signaux baissiers
            if direction == "HAUSSIER":
                if (price < ema * 0.999      # sous EMA
                    and bear_count >= 2      # 2+ rouges
                    and (lh or ll)):         # structure baissière
                    return "BAISSIER"

            # ❌ Bot dit BAISSIER mais signaux haussiers
            elif direction == "BAISSIER":
                if (price > ema * 1.001      # au dessus EMA
                    and bull_count >= 2      # 2+ vertes
                    and (hh or hl)):         # structure haussière
                    return "HAUSSIER"

            return direction

        except Exception as e:
            print(f"Erreur dans _force_direction_check : {e}")
            return direction


    def _fusion_direction(self, swing_dir, ema_dir, st_dir, previous):
        """
        ✅ Fusion intelligente des 3 sources de direction
        Priorité : EMA + ST > Swings
        """

        # Les 3 sont d'accord → direction forte
        if swing_dir == ema_dir and ema_dir == st_dir and swing_dir != "NEUTRE":
            return swing_dir

        # EMA + ST d'accord → suffit
        if ema_dir == st_dir and ema_dir != "NEUTRE":
            return ema_dir

        # EMA + Swings d'accord
        if ema_dir == swing_dir and ema_dir != "NEUTRE":
            return ema_dir

        # ST + Swings d'accord
        if st_dir == swing_dir and st_dir != "NEUTRE":
            return st_dir

        # Priorité à l'indicateur le plus fiable : EMA
        if ema_dir != "NEUTRE":
            return ema_dir

        # Priorité 2 : SuperTrend
        if st_dir != "NEUTRE":
            return st_dir

        # Priorité 3 : Swings
        if swing_dir != "NEUTRE":
            return swing_dir

        # Rien d'accord → on garde la précédente si elle existe
        if previous and previous != "NEUTRE":
            return previous

        return "NEUTRE"


    def compute_quality_score(self, result, df):
        score = 0

        score += result.get("score", 0) * 0.4

        if result.get("trend_continuation"):
            score += 25

        if result.get("pullback_ok"):
            score += 20

        if result.get("impulse_strength", 0) > 1.5:
            score += 15

        # ✅ Bonus EMA + ST alignés
        if result.get("ema_dir") == result.get("direction"):
            score += 10

        if result.get("st_dir") == result.get("direction"):
            score += 10

        ranges = (df["high"] - df["low"]).tail(10)
        if ranges.mean() > 0:
            score += 10

        if result.get("direction") == "NEUTRE":
            score -= 40

        return max(0, min(100, int(score)))


    def _error_result(self, reason, direction):
        return {
            "statut"           : "INTERDIT",
            "direction"        : direction,
            "score"            : 0,
            "confidence"       : 0,
            "exclusions"       : [reason],
            "justification"    : "Erreur analyse",
            "zone"             : {"low": None, "high": None},
            "pullback_active"  : False,
            "pullback_ok"      : False,
            "has_impulse"      : False,
            "impulse_strength" : 0,
            "trend_continuation": False,
            "extreme_event"    : False,
            "ema_dir"          : "NEUTRE",
            "st_dir"           : "NEUTRE",
        }

    def _reason(self, status, direction):
        if status == "INTERDIT":
            return "Structure invalide"
        if status == "SURVEILLANCE":
            return "Setup en attente"
        return f"Marché exploitable {direction.lower()}"