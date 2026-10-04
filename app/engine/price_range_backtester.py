# app/engine/price_range_backtester.py

import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from app.engine.price_range_strategy import price_range_signal, is_valid_price_range_time

def backtest_price_range_strategy(df, symbol="EURUSD", start_date=None, end_date=None):
    """
    Backtest la stratégie Price Range sur les données historiques
    
    Args:
        df: DataFrame OHLCV avec index datetime
        symbol: Symbole testé
        start_date: Date de début (optionnel)
        end_date: Date de fin (optionnel)
    
    Returns:
        dict: Résultats du backtest
    """
    if df is None or len(df) < 100:
        return {"error": "Pas assez de données pour backtest"}
    
    # Filtrer par dates si spécifiées
    if start_date:
        df = df[df.index >= start_date]
    if end_date:
        df = df[df.index <= end_date]
    
    results = {
        "total_trades": 0,
        "winning_trades": 0,
        "losing_trades": 0,
        "total_pips": 0,
        "win_rate": 0,
        "avg_win": 0,
        "avg_loss": 0,
        "profit_factor": 0,
        "max_drawdown": 0,
        "trades": []
    }
    
    # Itérer sur chaque bougie (simuler entrée à chaque bougie)
    for i in range(50, len(df) - 10):  # Commencer après 50 bougies pour avoir assez d'historique
        current_time = df.index[i]
        current_df = df.iloc[:i+1]  # Jusqu'à la bougie actuelle
        
        # Simuler vérification de l'heure
        hour = current_time.hour
        minute = current_time.minute
        
        # Vérifier si c'est une heure valide (8h, 12h, 16h, 20h UTC)
        valid_hours = [8, 12, 16, 20]
        if "XAU" in symbol or "GOLD" in symbol:
            valid_hours = [12, 16, 20]  # Éviter 8h pour l'or
        
        is_valid_hour = hour in valid_hours and minute <= 5
        
        if not is_valid_hour:
            continue
        
        # Obtenir le signal Price Range
        # Simuler une direction du bot (pour test, on utilise EMA simple)
        bot_direction = "HAUSSIER" if current_df['close'].iloc[-1] > current_df['close'].iloc[-20] else "BAISSIER"
        
        signal = price_range_signal(current_df, bot_direction, check_time=False)
        
        if not signal['valid']:
            continue
        
        # Vérifier si la direction est confirmée
        third_candle_dir = signal.get('third_candle_direction')
        
        if third_candle_dir != bot_direction:
            continue  # Pas de confirmation
        
        # Calculer SL et TP
        entry = signal['entry']
        range_size = signal['range_size']
        
        if bot_direction == "HAUSSIER":
            sl = entry - range_size
            tp = entry + (range_size * 2)
        else:
            sl = entry + range_size
            tp = entry - (range_size * 2)
        
        # Simuler le trade sur les 10 prochaines bougies
        trade_result = simulate_trade(df.iloc[i+1:i+11], entry, sl, tp, bot_direction)
        
        if trade_result['hit']:
            results['total_trades'] += 1
            results['trades'].append({
                'time': current_time,
                'direction': bot_direction,
                'entry': entry,
                'sl': sl,
                'tp': tp,
                'result': trade_result['result'],
                'pips': trade_result['pips'],
                'bars_held': trade_result['bars_held']
            })
            
            if trade_result['result'] == 'WIN':
                results['winning_trades'] += 1
                results['total_pips'] += trade_result['pips']
            else:
                results['losing_trades'] += 1
                results['total_pips'] -= trade_result['pips']
    
    # Calculer les statistiques
    if results['total_trades'] > 0:
        results['win_rate'] = (results['winning_trades'] / results['total_trades']) * 100
        
        # Moyennes
        wins = [t['pips'] for t in results['trades'] if t['result'] == 'WIN']
        losses = [t['pips'] for t in results['trades'] if t['result'] == 'LOSS']
        
        results['avg_win'] = np.mean(wins) if wins else 0
        results['avg_loss'] = np.mean(losses) if losses else 0
        
        # Profit Factor
        total_wins = sum(wins)
        total_losses = sum(losses)
        results['profit_factor'] = total_wins / total_losses if total_losses > 0 else 0
        
        # Max Drawdown
        results['max_drawdown'] = calculate_max_drawdown(results['trades'])
    
    return results


def simulate_trade(df, entry, sl, tp, direction):
    """
    Simule un trade sur les données futures
    
    Args:
        df: DataFrame des bougies futures
        entry: Prix d'entrée
        sl: Stop loss
        tp: Take profit
        direction: HAUSSIER ou BAISSIER
    
    Returns:
        dict: Résultat du trade
    """
    for i, candle in df.iterrows():
        high = candle['high']
        low = candle['low']
        
        if direction == "HAUSSIER":
            if high >= tp:
                return {'hit': True, 'result': 'WIN', 'pips': tp - entry, 'bars_held': i + 1}
            elif low <= sl:
                return {'hit': True, 'result': 'LOSS', 'pips': entry - sl, 'bars_held': i + 1}
        else:  # BAISSIER
            if low <= tp:
                return {'hit': True, 'result': 'WIN', 'pips': entry - tp, 'bars_held': i + 1}
            elif high >= sl:
                return {'hit': True, 'result': 'LOSS', 'pips': sl - entry, 'bars_held': i + 1}
    
    # Si ni SL ni TP n'est touché
    last_price = df.iloc[-1]['close']
    if direction == "HAUSSIER":
        pips = last_price - entry
    else:
        pips = entry - last_price
    
    return {'hit': True, 'result': 'PARTIAL', 'pips': pips, 'bars_held': len(df)}


def calculate_max_drawdown(trades):
    """
    Calcule le drawdown maximum
    """
    if not trades:
        return 0
    
    cumulative_pips = 0
    peak = 0
    max_drawdown = 0
    
    for trade in trades:
        if trade['result'] == 'WIN':
            cumulative_pips += trade['pips']
        else:
            cumulative_pips -= trade['pips']
        
        if cumulative_pips > peak:
            peak = cumulative_pips
        
        drawdown = peak - cumulative_pips
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    return max_drawdown


def print_backtest_results(results, symbol):
    """
    Affiche les résultats du backtest de manière lisible
    """
    print(f"\n📊 BACKTEST PRICE RANGE STRATEGY - {symbol}")
    print("=" * 50)
    
    if "error" in results:
        print(f"❌ Erreur: {results['error']}")
        return
    
    print(f"📈 Total Trades: {results['total_trades']}")
    print(f"✅ Winning Trades: {results['winning_trades']}")
    print(f"❌ Losing Trades: {results['losing_trades']}")
    print(f"📊 Win Rate: {results['win_rate']:.1f}%")
    print(f"💰 Total Pips: {results['total_pips']:.1f}")
    print(f"📈 Avg Win: {results['avg_win']:.1f} pips")
    print(f"📉 Avg Loss: {results['avg_loss']:.1f} pips")
    print(f"💎 Profit Factor: {results['profit_factor']:.2f}")
    print(f"📉 Max Drawdown: {results['max_drawdown']:.1f} pips")
    
    # Analyse des résultats
    print(f"\n🎯 ANALYSE:")
    if results['win_rate'] >= 60:
        print("✅ Win Rate excellent (≥60%)")
    elif results['win_rate'] >= 50:
        print("⚠️ Win Rate acceptable (50-60%)")
    else:
        print("❌ Win Rate faible (<50%)")
    
    if results['profit_factor'] >= 1.5:
        print("✅ Profit Factor excellent (≥1.5)")
    elif results['profit_factor'] >= 1.0:
        print("⚠️ Profit Factor acceptable (1.0-1.5)")
    else:
        print("❌ Profit Factor faible (<1.0)")
    
    if results['total_trades'] >= 100:
        print("✅ Nombre de trades suffisant (≥100)")
    else:
        print("⚠️ Nombre de trades limité (<100) - besoin plus de données")
    
