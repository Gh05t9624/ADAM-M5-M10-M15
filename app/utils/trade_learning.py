# app/utils/trade_learning.py
# Système d'apprentissage basé sur le journal de trade manuel

import json
import os
import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Optional
from collections import defaultdict

class TradeLearningSystem:
    """
    Système d'apprentissage qui analyse le journal de trade pour améliorer les performances
    """
    
    def __init__(self):
        self.learning_file = "trade_learning.json"
        self.learning_data = self._load_learning_data()
        self.trade_patterns = self._initialize_patterns()
    
    def _load_learning_data(self) -> Dict:
        """Charge les données d'apprentissage"""
        if os.path.exists(self.learning_file):
            try:
                with open(self.learning_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Erreur chargement apprentissage trade: {e}")
                return {}
        return {}
    
    def _save_learning_data(self):
        """Sauvegarde les données d'apprentissage"""
        try:
            with open(self.learning_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erreur sauvegarde apprentissage trade: {e}")
    
    def _initialize_patterns(self) -> Dict:
        """Initialise les structures de pattern"""
        return {
            'market_performance': defaultdict(dict),  # Performance par marché
            'sl_optimal': defaultdict(list),          # SL optimaux par marché
            'tp_optimal': defaultdict(list),          # TP optimaux par marché
            'time_performance': defaultdict(list),    # Performance par heure
            'trend_performance': defaultdict(list),   # Performance par tendance
            'session_performance': defaultdict(list), # Performance par session
            'winning_trades': [],                     # Trades gagnants
            'losing_trades': [],                      # Trades perdants
            'optimal_parameters': {}                  # Paramètres optimaux
        }
    
    def learn_from_trade(self, trade: dict):
        """Apprend d'un trade du journal"""
        market = trade['market']
        trend = trade['trend']
        sl = trade['stop_loss']
        tp = trade['take_profit']
        pnl = trade.get('profit_loss')
        entry_time = trade.get('entry_time', '')
        
        # Déterminer si le trade est gagnant
        is_winner = pnl is not None and pnl > 0
        
        # Analyser l'heure d'entrée
        try:
            if entry_time:
                entry_datetime = datetime.fromisoformat(entry_time.replace('Z', '+00:00'))
                hour = entry_datetime.hour
                session = self._get_session_at_time(entry_datetime)
            else:
                hour = None
                session = None
        except:
            hour = None
            session = None
        
        # Enregistrer les patterns
        if market not in self.trade_patterns['market_performance']:
            self.trade_patterns['market_performance'][market] = {
                'total_trades': 0,
                'winning_trades': 0,
                'total_pnl': 0,
                'avg_sl': 0,
                'avg_tp': 0
            }
        
        # Mettre à jour la performance par marché
        perf = self.trade_patterns['market_performance'][market]
        perf['total_trades'] += 1
        if is_winner:
            perf['winning_trades'] += 1
        if pnl is not None:
            perf['total_pnl'] += pnl
        
        # Mettre à jour les moyennes SL/TP
        perf['avg_sl'] = (perf['avg_sl'] * (perf['total_trades'] - 1) + sl) / perf['total_trades']
        perf['avg_tp'] = (perf['avg_tp'] * (perf['total_trades'] - 1) + tp) / perf['total_trades']
        
        # Enregistrer les SL/TP par résultat
        if is_winner:
            self.trade_patterns['sl_optimal'][market].append(sl)
            self.trade_patterns['tp_optimal'][market].append(tp)
            self.trade_patterns['winning_trades'].append(trade)
        else:
            self.trade_patterns['losing_trades'].append(trade)
        
        # Performance par heure
        if hour is not None:
            self.trade_patterns['time_performance'][hour].append(pnl if pnl is not None else 0)
        
        # Performance par tendance
        self.trade_patterns['trend_performance'][trend].append(pnl if pnl is not None else 0)
        
        # Performance par session
        if session:
            self.trade_patterns['session_performance'][session].append(pnl if pnl is not None else 0)
        
        # Sauvegarder les apprentissages
        self._save_learning_data()
        
        print(f"🧠 Apprentissage trade: {market} {trend} (SL: {sl}, TP: {tp}, P/L: {pnl})")
    
    def get_optimal_sl_tp(self, market: str, trend: str = None) -> Dict:
        """
        Retourne les paramètres SL/TP optimaux pour un marché
        
        Args:
            market: Symbole du marché
            trend: Tendance (optionnel)
        
        Returns:
            Dict: Paramètres optimaux
        """
        if market not in self.trade_patterns['market_performance']:
            # Pas assez de données - retourner des valeurs par défaut
            return {
                'sl': 30.0,
                'tp': 60.0,
                'confidence': 0.0,
                'based_on': 'default'
            }
        
        perf = self.trade_patterns['market_performance'][market]
        
        # Calculer les SL/TP optimaux basés sur les trades gagnants
        sl_list = self.trade_patterns['sl_optimal'][market]
        tp_list = self.trade_patterns['tp_optimal'][market]
        
        if len(sl_list) < 3:
            # Pas assez de trades gagnants - utiliser les moyennes
            return {
                'sl': perf['avg_sl'],
                'tp': perf['avg_tp'],
                'confidence': 0.3,
                'based_on': 'averages'
            }
        
        # Calculer les médianes (plus robustes que les moyennes)
        optimal_sl = np.median(sl_list)
        optimal_tp = np.median(tp_list)
        
        # Calculer le taux de réussite
        win_rate = perf['winning_trades'] / perf['total_trades']
        confidence = min(win_rate, 1.0)
        
        return {
            'sl': optimal_sl,
            'tp': optimal_tp,
            'confidence': confidence,
            'based_on': 'winning_trades',
            'win_rate': win_rate,
            'total_trades': perf['total_trades']
        }
    
    def get_best_trading_hours(self, market: str = None) -> List[Dict]:
        """
        Retourne les meilleures heures de trading
        
        Args:
            market: Symbole du marché (optionnel)
        
        Returns:
            List[Dict]: Meilleures heures avec performance
        """
        hour_performance = {}
        
        for hour, pnl_list in self.trade_patterns['time_performance'].items():
            if pnl_list:
                avg_pnl = np.mean(pnl_list)
                win_rate = sum(1 for p in pnl_list if p > 0) / len(pnl_list)
                
                hour_performance[hour] = {
                    'hour': hour,
                    'avg_pnl': avg_pnl,
                    'win_rate': win_rate,
                    'total_trades': len(pnl_list)
                }
        
        # Trier par performance
        sorted_hours = sorted(hour_performance.values(), key=lambda x: x['avg_pnl'], reverse=True)
        
        return sorted_hours[:5]  # Top 5 heures
    
    def get_market_performance_summary(self, market: str) -> Dict:
        """
        Retourne un résumé de performance pour un marché
        
        Args:
            market: Symbole du marché
        
        Returns:
            Dict: Résumé de performance
        """
        if market not in self.trade_patterns['market_performance']:
            return {'error': f'Pas de données pour {market}'}
        
        perf = self.trade_patterns['market_performance'][market]
        
        return {
            'market': market,
            'total_trades': perf['total_trades'],
            'winning_trades': perf['winning_trades'],
            'win_rate': perf['winning_trades'] / perf['total_trades'] if perf['total_trades'] > 0 else 0,
            'total_pnl': perf['total_pnl'],
            'avg_pnl': perf['total_pnl'] / perf['total_trades'] if perf['total_trades'] > 0 else 0,
            'avg_sl': perf['avg_sl'],
            'avg_tp': perf['avg_tp'],
            'optimal_sl_tp': self.get_optimal_sl_tp(market)
        }
    
    def _get_session_at_time(self, datetime_obj: datetime) -> str:
        """Détermine la session de trading"""
        hour = datetime_obj.hour
        
        if 0 <= hour < 8:
            return "ASIE"
        elif 8 <= hour < 13:
            return "LONDRES"
        elif 13 <= hour < 17:
            return "NEW_YORK"
        elif 17 <= hour < 22:
            return "OVERLAP"
        else:
            return "WEEKEND"
    
    def print_learning_summary(self):
        """Affiche un résumé de l'apprentissage"""
        print("\n🧠 RÉSUMÉ DE L'APPRENTISSAGE TRADE")
        print("=" * 70)
        
        total_trades = sum(perf['total_trades'] for perf in self.trade_patterns['market_performance'].values())
        
        if total_trades == 0:
            print("❌ Aucun trade enregistré - Utilisez le journal de trade pour commencer l'apprentissage")
            return
        
        print(f"📊 Total trades appris: {total_trades}")
        
        # Performance par marché
        print(f"\n💱 PERFORMANCE PAR MARCHÉ:")
        for market, perf in self.trade_patterns['market_performance'].items():
            win_rate = (perf['winning_trades'] / perf['total_trades']) * 100 if perf['total_trades'] > 0 else 0
            avg_pnl = perf['total_pnl'] / perf['total_trades'] if perf['total_trades'] > 0 else 0
            print(f"  {market}: {perf['total_trades']} trades, {win_rate:.1f}% win rate, {avg_pnl:+.1f} pips avg")
            print(f"    SL moyen: {perf['avg_sl']:.1f} | TP moyen: {perf['avg_tp']:.1f}")
        
        # Meilleures heures
        best_hours = self.get_best_trading_hours()
        if best_hours:
            print(f"\n⏰ MEILLEURES HEURES DE TRADING:")
            for hour_data in best_hours:
                print(f"  {hour_data['hour']:02d}:00 UTC: {hour_data['avg_pnl']:+.1f} pips avg ({hour_data['win_rate']*100:.1f}% win rate)")
        
        # Paramètres optimaux par marché
        print(f"\n🎯 PARAMÈTRES OPTIMAUX PAR MARCHÉ:")
        for market in self.trade_patterns['market_performance'].keys():
            optimal = self.get_optimal_sl_tp(market)
            if optimal['confidence'] > 0.5:
                print(f"  {market}: SL {optimal['sl']:.1f} | TP {optimal['tp']:.1f} (Confiance: {optimal['confidence']:.1%})")

# Instance globale
_trade_learning = None

def get_trade_learning_system():
    """Retourne l'instance globale du système d'apprentissage trade"""
    global _trade_learning
    if _trade_learning is None:
        _trade_learning = TradeLearningSystem()
    return _trade_learning

# Fonctions utilitaires
def learn_from_trade(trade: dict):
    """Apprend d'un trade"""
    system = get_trade_learning_system()
    system.learn_from_trade(trade)

def get_optimal_sl_tp(market: str, trend: str = None) -> Dict:
    """Retourne les paramètres SL/TP optimaux"""
    system = get_trade_learning_system()
    return system.get_optimal_sl_tp(market, trend)

def print_trade_learning_summary():
    """Affiche le résumé de l'apprentissage trade"""
    system = get_trade_learning_system()
    system.print_learning_summary()
