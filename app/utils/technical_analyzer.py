# app/utils/technical_analyzer.py
# Module d'analyse technique avancée pour suivre les détails de chaque marché

import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
import json
import os

class TechnicalAnalyzer:
    """
    Analyse technique détaillée pour chaque marché
    """
    
    def __init__(self):
        self.analysis_file = "technical_analysis.json"
        self.analysis_data = self._load_analysis_data()
    
    def _load_analysis_data(self) -> Dict:
        """Charge les données d'analyse depuis le fichier"""
        if os.path.exists(self.analysis_file):
            try:
                with open(self.analysis_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Erreur chargement analyse technique: {e}")
                return {}
        return {}
    
    def _save_analysis_data(self):
        """Sauvegarde les données d'analyse dans le fichier"""
        try:
            with open(self.analysis_file, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erreur sauvegarde analyse technique: {e}")
    
    def analyze_market_structure(self, symbol: str, df: pd.DataFrame, timeframe: str = "M5"):
        """
        Analyse la structure complète d'un marché
        
        Args:
            symbol: Symbole du marché
            df: DataFrame OHLCV
            timeframe: Timeframe de l'analyse
        
        Returns:
            Dict: Analyse technique complète
        """
        if df is None or len(df) < 50:
            return {'error': 'Pas assez de données pour analyse'}
        
        # Initialiser l'analyse pour ce symbole/timeframe
        key = f"{symbol}_{timeframe}"
        if key not in self.analysis_data:
            self.analysis_data[key] = {
                'symbol': symbol,
                'timeframe': timeframe,
                'analyses': [],
                'created_at': datetime.now(timezone.utc).isoformat()
            }
        
        # Analyse de tendance
        trend_analysis = self._analyze_trend(df)
        
        # Analyse des niveaux
        levels_analysis = self._analyze_key_levels(df)
        
        # Analyse de volatilité
        volatility_analysis = self._analyze_volatility(df)
        
        # Analyse de momentum
        momentum_analysis = self._analyze_momentum(df)
        
        # Analyse de volume
        volume_analysis = self._analyze_volume(df)
        
        # Analyse de patterns
        pattern_analysis = self._analyze_patterns(df)
        
        # Score de qualité technique
        quality_score = self._calculate_quality_score(trend_analysis, levels_analysis, 
                                                  volatility_analysis, momentum_analysis, 
                                                  volume_analysis, pattern_analysis)
        
        analysis = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'trend': trend_analysis,
            'levels': levels_analysis,
            'volatility': volatility_analysis,
            'momentum': momentum_analysis,
            'volume': volume_analysis,
            'patterns': pattern_analysis,
            'quality_score': quality_score,
            'price_data': {
                'current': df['close'].iloc[-1],
                'change_24h': self._calculate_24h_change(df),
                'change_week': self._calculate_week_change(df),
                'atr': self._calculate_atr(df)
            }
        }
        
        # Ajouter à l'historique
        self.analysis_data[key]['analyses'].append(analysis)
        self.analysis_data[key]['last_updated'] = datetime.now(timezone.utc).isoformat()
        
        # Garder seulement les 100 dernières analyses
        if len(self.analysis_data[key]['analyses']) > 100:
            self.analysis_data[key]['analyses'] = self.analysis_data[key]['analyses'][-100:]
        
        self._save_analysis_data()
        
        print(f"✅ Analyse technique {symbol} ({timeframe}): Score {quality_score}/100")
        
        return analysis
    
    def _analyze_trend(self, df: pd.DataFrame) -> Dict:
        """Analyse la tendance du marché"""
        close = df['close']
        
        # Moyennes mobiles
        ema_9 = close.ewm(span=9).mean()
        ema_21 = close.ewm(span=21).mean()
        ema_50 = close.ewm(span=50).mean()
        sma_200 = close.rolling(window=200).mean()
        
        # Direction de tendance
        current_price = close.iloc[-1]
        trend_direction = "HAUSSIER" if current_price > ema_21 else "BAISSIER"
        
        # Force de tendance
        trend_strength = abs((current_price - sma_200.iloc[-1]) / sma_200.iloc[-1]) * 100
        
        # Croisement de moyennes
        ema_cross = "BULLISH" if ema_9.iloc[-1] > ema_21.iloc[-1] else "BEARISH"
        
        # Structure de plus hauts/plus bas
        highs = df['high']
        lows = df['low']
        
        # Derniers plus hauts/bas (20 périodes)
        recent_highs = highs.rolling(window=20).max()
        recent_lows = lows.rolling(window=20).min()
        
        # Position actuelle par rapport aux niveaux
        position_vs_highs = "ABOVE" if current_price > recent_highs.iloc[-1] else "BELOW"
        position_vs_lows = "ABOVE" if current_price > recent_lows.iloc[-1] else "BELOW"
        
        return {
            'direction': trend_direction,
            'strength': trend_strength,
            'ema_9': ema_9.iloc[-1],
            'ema_21': ema_21.iloc[-1],
            'ema_50': ema_50.iloc[-1],
            'sma_200': sma_200.iloc[-1],
            'ema_cross': ema_cross,
            'position_vs_highs': position_vs_highs,
            'position_vs_lows': position_vs_lows,
            'trend_consistency': self._calculate_trend_consistency(close)
        }
    
    def _analyze_key_levels(self, df: pd.DataFrame) -> Dict:
        """Analyse les niveaux clés de support/résistance"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        # Pivot points
        recent_data = df.tail(1)  # Dernière période
        pivot_high = recent_data['high'].max()
        pivot_low = recent_data['low'].min()
        pivot_close = recent_data['close'].iloc[-1]
        
        # Calculer pivot classique
        pivot = (pivot_high + pivot_low + pivot_close) / 3
        
        # Supports et résistances
        s1 = (pivot * 2) - pivot_high
        r1 = (pivot * 2) - pivot_low
        s2 = pivot - (pivot_high - pivot_low)
        r2 = pivot + (pivot_high - pivot_low)
        
        # Niveaux de plus hauts/bas historiques (50 périodes)
        period_50_high = high.rolling(window=50).max()
        period_50_low = low.rolling(window=50).min()
        
        current_price = close.iloc[-1]
        
        return {
            'pivot': pivot,
            'support_1': s1,
            'support_2': s2,
            'resistance_1': r1,
            'resistance_2': r2,
            'current_vs_pivot': "ABOVE" if current_price > pivot else "BELOW",
            'distance_to_r1': abs(r1 - current_price),
            'distance_to_s1': abs(current_price - s1),
            'period_50_high': period_50_high.iloc[-1],
            'period_50_low': period_50_low.iloc[-1],
            'key_level_strength': self._calculate_level_strength(df, current_price)
        }
    
    def _analyze_volatility(self, df: pd.DataFrame) -> Dict:
        """Analyse la volatilité du marché"""
        close = df['close']
        high = df['high']
        low = df['low']
        
        # ATR (Average True Range)
        atr = self._calculate_atr(df)
        
        # Volatilité historique
        returns = close.pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)  # Annualisée
        
        # Bollinger Bands
        bb_period = 20
        bb_std = 2
        bb_middle = close.rolling(window=bb_period).mean()
        bb_upper = bb_middle + (returns.rolling(window=bb_period).std() * bb_std)
        bb_lower = bb_middle - (returns.rolling(window=bb_period).std() * bb_std)
        
        current_price = close.iloc[-1]
        bb_position = (current_price - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1])
        
        # Range expansion
        recent_range = (high - low).tail(20).mean()
        historical_range = (high - low).tail(100).mean()
        range_expansion = recent_range / historical_range
        
        return {
            'atr': atr,
            'atr_percent': (atr / current_price) * 100,
            'volatility_annualized': volatility,
            'bb_upper': bb_upper.iloc[-1],
        'bb_middle': bb_middle.iloc[-1],
            'bb_lower': bb_lower.iloc[-1],
            'bb_position': bb_position,
            'range_expansion': range_expansion,
            'volatility_regime': self._classify_volatility_regime(volatility, range_expansion)
        }
    
    def _analyze_momentum(self, df: pd.DataFrame) -> Dict:
        """Analyse le momentum du marché"""
        close = df['close']
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = close.ewm(span=12).mean()
        exp2 = close.ewm(span=26).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=9).mean()
        histogram = macd_line - signal_line
        
        # Stochastic
        low_14 = low.rolling(window=14).min()
        high_14 = high.rolling(window=14).max()
        k_percent = 100 * ((close - low_14) / (high_14 - low_14))
        d_percent = k_percent.rolling(window=3).mean()
        
        current_values = {
            'rsi': rsi.iloc[-1],
            'macd': macd_line.iloc[-1],
            'macd_signal': signal_line.iloc[-1],
            'macd_histogram': histogram.iloc[-1],
            'stoch_k': k_percent.iloc[-1],
            'stoch_d': d_percent.iloc[-1]
        }
        
        # Signaux de momentum
        rsi_signal = "SURACHAT" if current_values['rsi'] > 70 else "SURVENTE" if current_values['rsi'] < 30 else "NEUTRE"
        macd_signal = "HAUSSIER" if current_values['macd'] > current_values['macd_signal'] else "BAISSIER"
        stoch_signal = "SURACHAT" if current_values['stoch_k'] > 80 else "SURVENTE" if current_values['stoch_k'] < 20 else "NEUTRE"
        
        return {
            'current_values': current_values,
            'rsi_signal': rsi_signal,
            'macd_signal': macd_signal,
            'stoch_signal': stoch_signal,
            'momentum_strength': self._calculate_momentum_strength(current_values),
            'divergence_detected': self._detect_divergence(close, rsi, macd_line)
        }
    
    def _analyze_volume(self, df: pd.DataFrame) -> Dict:
        """Analyse le volume du marché"""
        volume = df['volume']
        close = df['close']
        
        # Volume moyen
        avg_volume_20 = volume.rolling(window=20).mean()
        avg_volume_50 = volume.rolling(window=50).mean()
        
        current_volume = volume.iloc[-1]
        volume_ratio_20 = current_volume / avg_volume_20.iloc[-1]
        volume_ratio_50 = current_volume / avg_volume_50.iloc[-1]
        
        # Volume Price Trend (VPT)
        price_change = close.diff()
        vpt = (price_change * volume).cumsum()
        
        # Accumulation/Distribution
        accumulation = 0
        distribution = 0
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                accumulation += volume.iloc[i]
            else:
                distribution += volume.iloc[i]
        
        total_volume = volume.sum()
        accumulation_ratio = accumulation / total_volume
        distribution_ratio = distribution / total_volume
        
        return {
            'current_volume': current_volume,
            'avg_volume_20': avg_volume_20.iloc[-1],
            'avg_volume_50': avg_volume_50.iloc[-1],
            'volume_ratio_20': volume_ratio_20,
            'volume_ratio_50': volume_ratio_50,
            'volume_trend': "INCREASING" if volume_ratio_20 > 1.2 else "DECREASING" if volume_ratio_20 < 0.8 else "NEUTRAL",
            'vpt': vpt.iloc[-1],
            'accumulation_ratio': accumulation_ratio,
            'distribution_ratio': distribution_ratio,
            'volume_profile': self._analyze_volume_profile(df)
        }
    
    def _analyze_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyse les patterns chartistes"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        # Dernières 20 bougies pour pattern detection
        recent = df.tail(20)
        
        patterns = []
        
        # Detection de patterns simples
        # Doji
        doji_detected = []
        for i in range(len(recent)):
            candle = recent.iloc[i]
            body_size = abs(candle['close'] - candle['open'])
            range_size = candle['high'] - candle['low']
            
            if body_size < range_size * 0.1:  # Corps < 10% du range
                doji_detected.append(i)
        
        # Hammer/Shooting Star
        hammer_detected = []
        shooting_star_detected = []
        
        for i in range(1, len(recent)):
            prev_candle = recent.iloc[i-1]
            candle = recent.iloc[i]
            
            body_size = abs(candle['close'] - candle['open'])
            upper_shadow = candle['high'] - max(candle['open'], candle['close'])
            lower_shadow = min(candle['open'], candle['close']) - candle['low']
            
            # Hammer (longue ombre inférieure)
            if lower_shadow > body_size * 2 and upper_shadow < body_size * 0.5:
                hammer_detected.append(i)
            
            # Shooting Star (longue ombre supérieure)
            if upper_shadow > body_size * 2 and lower_shadow < body_size * 0.5:
                shooting_star_detected.append(i)
        
        # Engulfing patterns
        engulfing_bullish = []
        engulfing_bearish = []
        
        for i in range(1, len(recent)):
            prev_candle = recent.iloc[i-1]
            candle = recent.iloc[i]
            
            # Bullish engulfing
            if (prev_candle['close'] < prev_candle['open'] and  # Bougie rouge précédente
                candle['close'] > candle['open'] and  # Bougie verte actuelle
                candle['open'] < prev_candle['close'] and  # Open < close précédent
                candle['close'] > prev_candle['open']):  # Close > open précédent
                engulfing_bullish.append(i)
            
            # Bearish engulfing
            if (prev_candle['close'] > prev_candle['open'] and  # Bougie verte précédente
                candle['close'] < candle['open'] and  # Bougie rouge actuelle
                candle['open'] > prev_candle['close'] and  # Open > close précédent
                candle['close'] < prev_candle['open']):  # Close < open précédent
                engulfing_bearish.append(i)
        
        return {
            'doji_count': len(doji_detected),
            'hammer_count': len(hammer_detected),
            'shooting_star_count': len(shooting_star_detected),
            'bullish_engulfing_count': len(engulfing_bullish),
            'bearish_engulfing_count': len(engulfing_bearish),
            'recent_patterns': {
                'doji_positions': doji_detected[-5:] if doji_detected else [],
                'hammer_positions': hammer_detected[-5:] if hammer_detected else [],
                'shooting_star_positions': shooting_star_detected[-5:] if shooting_star_detected else [],
                'bullish_engulfing_positions': engulfing_bullish[-3:] if engulfing_bullish else [],
                'bearish_engulfing_positions': engulfing_bearish[-3:] if engulfing_bearish else []
            },
            'pattern_reliability': self._calculate_pattern_reliability(df)
        }
    
    def _calculate_quality_score(self, trend_analysis: Dict, levels_analysis: Dict, 
                               volatility_analysis: Dict, momentum_analysis: Dict,
                               volume_analysis: Dict, pattern_analysis: Dict) -> int:
        """Calcule un score de qualité technique (0-100)"""
        score = 0
        
        # Tendance (25 points)
        trend_strength = trend_analysis.get('strength', 0)
        if trend_strength > 2:
            score += 20
        elif trend_strength > 1:
            score += 15
        elif trend_strength > 0.5:
            score += 10
        elif trend_strength > 0.2:
            score += 5
        
        # Niveaux clés (20 points)
        level_strength = levels_analysis.get('key_level_strength', 0)
        if level_strength > 0.8:
            score += 20
        elif level_strength > 0.6:
            score += 15
        elif level_strength > 0.4:
            score += 10
        elif level_strength > 0.2:
            score += 5
        
        # Momentum (20 points)
        momentum_strength = momentum_analysis.get('momentum_strength', 0)
        if momentum_strength > 0.7:
            score += 20
        elif momentum_strength > 0.5:
            score += 15
        elif momentum_strength > 0.3:
            de += 10
        elif momentum_strength > 0.1:
            score += 5
        
        # Volume (15 points)
        volume_ratio = volume_analysis.get('volume_ratio_20', 1)
        if volume_ratio > 1.5:
            score += 15
        elif volume_ratio > 1.2:
            score += 12
        elif volume_ratio > 1.0:
            score += 8
        elif volume_ratio > 0.8:
            score += 5
        
        # Patterns (20 points)
        pattern_reliability = pattern_analysis.get('pattern_reliability', 0)
        if pattern_reliability > 0.8:
            score += 20
        elif pattern_reliability > 0.6:
            score += 15
        elif pattern_reliability > 0.4:
            score += 10
        elif pattern_reliability > 0.2:
            score += 5
        
        return min(score, 100)
    
    # Méthodes utilitaires pour les calculs
    def _calculate_24h_change(self, df: pd.DataFrame) -> float:
        """Calcule le changement sur 24h"""
        if len(df) < 25:
            return 0
        current_price = df['close'].iloc[-1]
        price_24h_ago = df['close'].iloc[-25] if len(df) >= 25 else df['close'].iloc[0]
        return ((current_price - price_24h_ago) / price_24h_ago) * 100
    
    def _calculate_week_change(self, df: pd.DataFrame) -> float:
        """Calcule le changement sur la semaine"""
        if len(df) < 168:  # 7 jours * 24h
            return 0
        current_price = df['close'].iloc[-1]
        price_week_ago = df['close'].iloc[-168] if len(df) >= 168 else df['close'].iloc[0]
        return ((current_price - price_week_ago) / price_week_ago) * 100
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calcule l'Average True Range"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr.iloc[-1] if not atr.empty else 0
    
    def _calculate_trend_consistency(self, close: pd.Series) -> str:
        """Calcule la consistance de la tendance"""
        if len(close) < 20:
            return "INSUFFICIENT_DATA"
        
        # Vérifier la direction sur différentes périodes
        short_trend = "UP" if close.iloc[-1] > close.iloc[-5] else "DOWN"
        medium_trend = "UP" if close.iloc[-1] > close.iloc[-10] else "DOWN"
        long_trend = "UP" if close.iloc[-1] > close.iloc[-20] else "DOWN"
        
        if short_trend == medium_trend == long_trend:
            return "STRONG_CONSISTENCY"
        elif short_trend == medium_trend or medium_trend == long_trend:
            return "MODERATE_CONSISTENCY"
        else:
            return "WEAK_CONSISTENCY"
    
    def _calculate_level_strength(self, df: pd.DataFrame, current_price: float) -> float:
        """Calcule la force des niveaux de support/résistance"""
        high = df['high']
        low = df['low']
        
        # Nombre de fois que le prix a testé ces niveaux
        recent_highs = high.rolling(window=20).max()
        recent_lows = low.rolling(window=20).min()
        
        # Proximité avec les niveaux clés
        proximity_score = 0
        
        if current_price >= recent_highs.iloc[-1] * 0.98 and current_price <= recent_highs.iloc[-1]:
            proximity_score += 0.3
        
        if current_price >= recent_lows.iloc[-1] and current_price <= recent_lows.iloc[-1] * 1.02:
            proximity_score += 0.3
        
        # Historique de réaction aux niveaux
        level_tests = 0
        for i in range(1, len(df)):
            if df['close'].iloc[i] >= recent_highs.iloc[i] * 0.98 or df['close'].iloc[i] <= recent_lows.iloc[i] * 1.02:
                level_tests += 1
        
        historical_strength = min(level_tests / len(df), 1.0)
        
        return (proximity_score + historical_strength) / 2
    
    def _classify_volatility_regime(self, volatility: float, range_expansion: float) -> str:
        """Classifie le régime de volatilité"""
        if volatility > 0.3 and range_expansion > 1.5:
            return "HIGH_VOLATILITY_EXPANSION"
        elif volatility > 0.3:
            return "HIGH_VOLATILITY"
        elif range_expansion > 1.3:
            return "RANGE_EXPANSION"
        elif volatility > 0.2:
            return "MODERATE_VOLATILITY"
        else:
            return "LOW_VOLATILITY"
    
    def _calculate_momentum_strength(self, current_values: Dict) -> float:
        """Calcule la force du momentum"""
        rsi = current_values.get('rsi', 50)
        macd = current_values.get('macd', 0)
        stoch = current_values.get('stoch_k', 50)
        
        strength = 0
        
        # RSI contribution
        if 40 <= rsi <= 60:
            strength += 0.3
        elif rsi > 60 or rsi < 40:
            strength += 0.2
        
        # MACD contribution
        if abs(macd) > 0.001:
            strength += 0.3
        elif abs(macd) > 0.0005:
            strength += 0.2
        
        # Stochastic contribution
        if 20 <= stoch <= 80:
            strength += 0.2
        elif stoch > 80 or stoch < 20:
            strength += 0.1
        
        return min(strength, 1.0)
    
    def _detect_divergence(self, close: pd.Series, rsi: pd.Series, macd: pd.Series) -> Dict:
        """Détecte les divergences RSI/MACD"""
        if len(close) < 20:
            return {'bullish_divergence': False, 'bearish_divergence': False}
        
        # Divergence RSI
        rsi_divergence = self._detect_rsi_divergence(close, rsi)
        
        # Divergence MACD
        macd_divergence = self._detect_macd_divergence(close, macd)
        
        return {
            'bullish_divergence': rsi_divergence['bullish'] or macd_divergence['bullish'],
            'bearish_divergence': rsi_divergence['bearish'] or macd_divergence['bearish'],
            'rsi_divergence': rsi_divergence,
            'macd_divergence': macd_divergence
        }
    
    def _detect_rsi_divergence(self, close: pd.Series, rsi: pd.Series) -> Dict:
        """Détecte les divergences RSI"""
        # Simplifié - détecter basé sur les pics
        price_highs = close.rolling(window=10).max()
        price_lows = close.rolling(window=10).min()
        rsi_highs = rsi.rolling(window=10).max()
        rsi_lows = rsi.rolling(window=10).min()
        
        bullish_divergence = False
        bearish_divergence = False
        
        # Divergence haussière (prix plus bas mais RSI plus haut)
        if (close.iloc[-1] < price_highs.iloc[-5] and 
            rsi.iloc[-1] > rsi_highs.iloc[-5]):
            bullish_divergence = True
        
        # Divergence baissière (prix plus haut mais RSI plus bas)
        if (close.iloc[-1] > price_lows.iloc[-5] and 
            rsi.iloc[-1] < rsi_lows.iloc[-5]):
            bearish_divergence = True
        
        return {'bullish': bullish_divergence, 'bearish': bearish_divergence}
    
    def _detect_macd_divergence(self, close: pd.Series, macd: pd.Series) -> Dict:
        """Détecte les divergences MACD"""
        # Similar à RSI mais avec MACD
        price_highs = close.rolling(window=10).max()
        price_lows = close.rolling(window=10).min()
        macd_highs = macd.rolling(window=10).max()
        macd_lows = macd.rolling(window=10).min()
        
        bullish_divergence = False
        bearish_divergence = False
        
        # Divergence haussière
        if (close.iloc[-1] < price_highs.iloc[-5] and 
            macd.iloc[-1] > macd_highs.iloc[-5]):
            bullish_divergence = True
        
        # Divergence baissière
        if (close.iloc[-1] > price_lows.iloc[-5] and 
            macd.iloc[-1] < macd_lows.iloc[-5]):
            bearish_divergence = True
        
        return {'bullish': bullish_divergence, 'bearish': bearish_divergence}
    
    def _analyze_volume_profile(self, df: pd.DataFrame) -> Dict:
        """Analyse le profil de volume (simplifié)"""
        close = df['close']
        volume = df['volume']
        
        # Niveaux de prix à fort volume
        price_levels = {}
        for i in range(len(df)):
            price = round(close.iloc[i], 5)
            if price not in price_levels:
                price_levels[price] = 0
            price_levels[price] += volume.iloc[i]
        
        # Trier par volume
        sorted_levels = sorted(price_levels.items(), key=lambda x: x[1], reverse=True)
        
        if len(sorted_levels) > 0:
            poc_price = sorted_levels[0][0]  # Point of Control
            poc_volume = sorted_levels[0][1]
            
            # Niveaux de valeur élevée
            total_volume = sum(price_levels.values())
            value_area_low = 0
            value_area_high = 0
            cumulative_volume = 0
            
            for price, vol in sorted_levels:
                cumulative_volume += vol
                if cumulative_volume >= total_volume * 0.7 and value_area_low == 0:
                    value_area_low = price
                if cumulative_volume >= total_volume * 0.3 and value_area_high == 0:
                    value_area_high = price
            
            return {
                'poc_price': poc_price,
                'poc_volume': poc_volume,
                'value_area_low': value_area_low,
                'value_area_high': value_area_high,
                'volume_distribution': sorted_levels[:10]  # Top 10 niveaux
            }
        
        return {'poc_price': 0, 'poc_volume': 0, 'value_area_low': 0, 'value_area_high': 0}
    
    def get_analysis_summary(self, symbol: str, timeframe: str = "M5", limit: int = 10) -> Dict:
        """
        Retourne un résumé des analyses pour un marché
        
        Args:
            symbol: Symbole du marché
            timeframe: Timeframe de l'analyse
            limit: Nombre d'analyses à retourner
        
        Returns:
            Dict: Résumé des analyses
        """
        key = f"{symbol}_{timeframe}"
        
        if key not in self.analysis_data:
            return {'error': f'Aucune analyse pour {symbol} {timeframe}'}
        
        analyses = self.analysis_data[key]['analyses']
        
        if not analyses:
            return {'error': f'Aucune analyse pour {symbol} {timeframe}'}
        
        # Prendre les plus récentes
        recent_analyses = analyses[-limit:]
        
        # Calculer les moyennes
        avg_quality = sum(a['quality_score'] for a in recent_analyses) / len(recent_analyses)
        max_quality = max(a['quality_score'] for a in recent_analyses)
        min_quality = min(a['quality_score'] for a in recent_analyses)
        
        # Tendance actuelle
        latest_analysis = recent_analyses[-1]
        current_trend = latest_analysis.get('trend', {}).get('direction', 'UNKNOWN')
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'total_analyses': len(analyses),
            'recent_analyses_count': len(recent_analyses),
            'avg_quality_score': round(avg_quality, 1),
            'max_quality_score': max_quality,
            'min_quality_score': min_quality,
            'current_trend': current_trend,
            'latest_analysis': latest_analysis,
            'analysis_history': recent_analyses
        }
    
    def print_analysis_report(self, symbol: str, timeframe: str = "M5"):
        """Affiche un rapport détaillé des analyses"""
        summary = self.get_analysis_summary(symbol, timeframe)
        
        if 'error' in summary:
            print(f"❌ {summary['error']}")
            return
        
        print(f"\n📊 RAPPORT D'ANALYSE TECHNIQUE - {symbol} ({timeframe})")
        print("=" * 60)
        print(f"Total analyses: {summary['total_analyses']}")
        print(f"Score qualité moyen: {summary['avg_quality_score']}/100")
        print(f"Score qualité max: {summary['max_quality_score']}/100")
        print(f"Tendance actuelle: {summary['current_trend']}")
        
        latest = summary['latest_analysis']
        
        print(f"\n📈 TENDANCE:")
        print(f"  Direction: {latest['trend']['direction']}")
        print(f"  Force: {latest['trend']['strength']:.2f}%")
        print(f"  EMA 9/21: {latest['trend']['ema_cross']}")
        
        print(f"\n🎯 NIVEAUX CLÉS:")
        print(f"  Pivot: {latest['levels']['pivot']:.5f}")
        print(f"  Support 1: {latest['levels']['support_1']:.5f}")
        print(f"  Résistance 1: {latest['levels']['resistance_1']:.5f}")
        
        print(f"\n📊 VOLATILITÉ:")
        print(f"  ATR: {latest['volatility']['atr']:.5f}")
        print(f"  Régime: {latest['volatility']['volatility_regime']}")
        
        print(f"\n⚡ MOMENTUM:")
        print(f"  RSI: {latest['momentum']['current_values']['rsi']:.1f} ({latest['momentum']['rsi_signal']})")
        print(f"  MACD: {latest['momentum']['macd_signal']}")
        
        print(f"\n📊 VOLUME:")
        print(f"  Ratio actuel/moyenne: {latest['volume']['volume_ratio_20']:.2f}")
        print(f"  Tendance: {latest['volume']['volume_trend']}")
        
        print(f"\n🔍 PATTERNS:")
        patterns = latest['patterns']
        print(f"  Engulfing baissier: {patterns['bearish_engulfing_count']}")
        print(f"  Engulfing haussier: {patterns['bullish_engulfing_count']}")
        print(f"  Doji: {patterns['doji_count']}")
        
        print(f"\n💰 PRIX ACTUEL:")
        price_data = latest['price_data']
        print(f"  Prix: {price_data['current']:.5f}")
        print(f"  Variation 24h: {price_data['change_24h']:+.2f}%")
        print(f"  Variation semaine: {price_data['change_week']:+.2f}%")

# Instance globale
_technical_analyzer = None

def get_technical_analyzer():
    """Retourne l'instance globale de l'analyseur technique"""
    global _technical_analyzer
    if _technical_analyzer is None:
        _technical_analyzer = TechnicalAnalyzer()
    return _technical_analyzer

# Fonctions utilitaires
def analyze_market_structure(symbol: str, df: pd.DataFrame, timeframe: str = "M5"):
    """Analyse la structure d'un marché"""
    analyzer = get_technical_analyzer()
    return analyzer.analyze_market_structure(symbol, df, timeframe)

def print_analysis_report(symbol: str, timeframe: str = "M5"):
    """Affiche le rapport d'analyse technique"""
    analyzer = get_technical_analyzer()
    analyzer.print_analysis_report(symbol, timeframe)
