# app/engine/fibonacci.py

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class FibonacciLevel:
    """Niveau Fibonacci avec prix et score"""
    level: float  # 0.382, 0.500, 0.618, etc.
    price: float
    is_active: bool
    score_boost: int
    description: str

@dataclass
class FibonacciSwing:
    """Swing détecté pour calcul Fibonacci"""
    swing_high: float
    swing_low: float
    swing_high_index: int
    swing_low_index: int
    direction: str  # "HAUSSIER" ou "BAISSIER"
    strength: float

class FibonacciAnalyzer:
    """Analyseur Fibonacci pour ADAM"""
    
    def __init__(self):
        self.fibonacci_levels = [0.236, 0.382, 0.447, 0.500, 0.618, 0.786, 0.886]
        self.extension_levels = [1.272, 1.414, 1.618, 2.000, 2.618]
        
        # Scores boost selon niveaux (optimisé M10)
        self.level_scores = {
            0.382: 25,  # Golden zone M10 - très fiable
            0.500: 30,  # Middle point M10 - excellent
            0.618: 35,  # Golden ratio M10 - le meilleur
            0.786: 20,  # Deep pullback M10 - bon
            0.447: 22,  # Alternative zone M10 - fiable
            0.236: 12,  # Shallow pullback M10 - acceptable
            0.886: 15   # Very deep pullback M10 - rare mais bon
        }
    
    def detect_swing_points(self, df: pd.DataFrame, lookback: int = 12) -> List[FibonacciSwing]:
        """
        Détecter les points de swing (HH/LL) pour calcul Fibonacci
        Optimisé pour timeframe M10

        Args:
            df: DataFrame avec OHLC
            lookback: Période de détection (12 pour M10 = 2h)

        Returns:
            Liste des swings détectés
        """
        swings = []
        
        if len(df) < lookback * 2:
            return swings
        
        # Lookback optimisé pour M10 : 12 périodes = 2 heures
        high_idx = df['high'].rolling(lookback, center=True).max() == df['high']
        low_idx = df['low'].rolling(lookback, center=True).min() == df['low']
        
        # Détecter les swings haussiers (Higher Highs + Higher Lows)
        for i in range(lookback, len(df) - lookback):
            if high_idx.iloc[i]:
                # Chercher le LL précédent
                for j in range(i - lookback, i):
                    if low_idx.iloc[j]:
                        # Calculer la force du swing
                        swing_range = df['high'].iloc[i] - df['low'].iloc[j]
                        avg_range = (df['high'] - df['low']).rolling(14).mean().iloc[i]
                        
                        if avg_range > 0:
                            strength = swing_range / avg_range
                            
                            if strength >= 1.0:  # Seuil minimum
                                swing = FibonacciSwing(
                                    swing_high=df['high'].iloc[i],
                                    swing_low=df['low'].iloc[j],
                                    swing_high_index=i,
                                    swing_low_index=j,
                                    direction="HAUSSIER",
                                    strength=strength
                                )
                                swings.append(swing)
                                break
        
        return swings
    
    def calculate_fibonacci_retracement(self, swing: FibonacciSwing, current_price: float, 
                                       atr: float = None) -> Dict:
        """
        Calculer les niveaux de retracement Fibonacci
        
        Args:
            swing: Swing détecté
            current_price: Prix actuel
            atr: ATR pour la tolérance
            
        Returns:
            Dictionnaire avec les niveaux Fibonacci actifs
        """
        swing_range = swing.swing_high - swing.swing_low
        
        # Calculer les niveaux de retracement
        retracement_levels = {}
        
        for level in self.fibonacci_levels:
            if swing.direction == "HAUSSIER":
                # Pullback depuis le haut
                price = swing.swing_high - (swing_range * level)
            else:
                # Pullback depuis le bas
                price = swing.swing_low + (swing_range * level)
            
            # Vérifier si le prix actuel est dans la zone de tolérance (optimisé M10)
            tolerance = (atr * 0.25) if atr else (swing_range * 0.015)  # Tolérance M10 augmentée
            is_active = abs(current_price - price) <= tolerance
            
            retracement_levels[level] = FibonacciLevel(
                level=level,
                price=price,
                is_active=is_active,
                score_boost=self.level_scores.get(level, 10),
                description=self._get_level_description(level, swing.direction)
            )
        
        return {
            'swing': swing,
            'retracement_levels': retracement_levels,
            'active_levels': [k for k, v in retracement_levels.items() if v.is_active],
            'best_level': self._get_best_active_level(retracement_levels)
        }
    
    def calculate_fibonacci_extensions(self, swing: FibonacciSwing, entry_price: float) -> Dict:
        """
        Calculer les niveaux d'extension Fibonacci pour les TP
        
        Args:
            swing: Swing détecté
            entry_price: Prix d'entrée
            
        Returns:
            Dictionnaire avec les niveaux d'extension
        """
        swing_range = swing.swing_high - swing.swing_low
        extensions = {}
        
        for ext_level in self.extension_levels:
            if swing.direction == "HAUSSIER":
                # Extension depuis le swing low
                tp_price = swing.swing_low + (swing_range * ext_level)
            else:
                # Extension depuis le swing high
                tp_price = swing.swing_high - (swing_range * ext_level)
            
            # Calculer le risk/reward
            if swing.direction == "HAUSSIER":
                risk = entry_price - swing.swing_low
                reward = tp_price - entry_price
            else:
                risk = swing.swing_high - entry_price
                reward = entry_price - tp_price
            
            if risk > 0:
                rr_ratio = reward / risk
            else:
                rr_ratio = 0
            
            extensions[ext_level] = {
                'price': tp_price,
                'rr_ratio': rr_ratio,
                'description': f"Extension {ext_level} (RR: {rr_ratio:.2f})"
            }
        
        return extensions
    
    def detect_fibonacci_confluence(self, df: pd.DataFrame, current_price: float) -> Dict:
        """
        Détecter les confluences Fibonacci (multiples swings)
        
        Args:
            df: DataFrame OHLC
            current_price: Prix actuel
            
        Returns:
            Informations sur les confluences détectées
        """
        swings = self.detect_swing_points(df)
        confluences = []
        
        for swing in swings:
            fib_calc = self.calculate_fibonacci_retracement(swing, current_price)
            
            if fib_calc['active_levels']:
                confluence_info = {
                    'swing': swing,
                    'active_levels': fib_calc['active_levels'],
                    'best_level': fib_calc['best_level'],
                    'confluence_score': len(fib_calc['active_levels']) * 10
                }
                confluences.append(confluence_info)
        
        # Trier par score de confluence
        confluences.sort(key=lambda x: x['confluence_score'], reverse=True)
        
        return {
            'confluences': confluences,
            'best_confluence': confluences[0] if confluences else None,
            'total_confluence_score': sum(c['confluence_score'] for c in confluences)
        }
    
    def calculate_fibonacci_score_boost(self, fib_analysis: Dict, ema_alignment: bool = False, 
                                      volume_confirmation: bool = False) -> int:
        """
        Calculer le bonus de score pour l'analyse Fibonacci
        
        Args:
            fib_analysis: Résultat de l'analyse Fibonacci
            ema_alignment: Si les EMA sont alignées
            volume_confirmation: Si le volume confirme
            
        Returns:
            Score boost total
        """
        boost = 0
        
        # Bonus des niveaux actifs
        if fib_analysis['active_levels']:
            best_level = fib_analysis['best_level']
            if best_level:
                boost += best_level.score_boost
        
        # Bonus de confluence
        if len(fib_analysis['active_levels']) > 1:
            boost += 15  # Bonus multi-niveaux
        
        # Bonus de confluence avec indicateurs
        if ema_alignment:
            boost += 10
        
        if volume_confirmation:
            boost += 8
        
        # Bonus selon la force du swing
        swing_strength = fib_analysis['swing'].strength
        if swing_strength >= 2.0:
            boost += 12
        elif swing_strength >= 1.5:
            boost += 8
        elif swing_strength >= 1.0:
            boost += 5
        
        return boost
    
    def _get_level_description(self, level: float, direction: str) -> str:
        """Description du niveau Fibonacci"""
        descriptions = {
            0.236: "Pullback superficiel",
            0.382: "Zone d'or (38.2%)",
            0.447: "Zone alternative",
            0.500: "Point médian (50%)",
            0.618: "Ratio d'or (61.8%)",
            0.786: "Pullback profond",
            0.886: "Pullback très profond"
        }
        
        base_desc = descriptions.get(level, f"Niveau {level}")
        
        if direction == "HAUSSIER":
            return f"{base_desc} - Support"
        else:
            return f"{base_desc} - Résistance"
    
    def _get_best_active_level(self, levels: Dict) -> Optional[FibonacciLevel]:
        """Trouver le meilleur niveau Fibonacci actif"""
        active_levels = [v for v in levels.values() if v.is_active]
        
        if not active_levels:
            return None
        
        # Prioriser les niveaux avec le plus haut score
        return max(active_levels, key=lambda x: x.score_boost)
    
    def get_fibonacci_summary(self, fib_analysis: Dict) -> str:
        """
        Générer un résumé de l'analyse Fibonacci pour l'affichage
        
        Args:
            fib_analysis: Résultat de l'analyse Fibonacci
            
        Returns:
            Texte descriptif
        """
        if not fib_analysis['active_levels']:
            return "Aucun niveau Fibonacci actif"
        
        best_level = fib_analysis['best_level']
        swing = fib_analysis['swing']
        
        summary = f"FIBONACCI ACTIF\n"
        summary += f"Swing: {swing.direction} ({swing.swing_strength:.1f})\n"
        summary += f"Niveau: {best_level.level * 100:.1f}% - {best_level.description}\n"
        summary += f"Score Boost: +{best_level.score_boost} pts"
        
        if len(fib_analysis['active_levels']) > 1:
            summary += f"\nConfluence: {len(fib_analysis['active_levels'])} niveaux"
        
        return summary
