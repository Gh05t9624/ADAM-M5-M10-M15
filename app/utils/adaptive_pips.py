# app/utils/adaptive_pips.py

import pandas as pd
import numpy as np

def get_adaptive_pip_config(symbol, df=None):
    """
    Retourne la configuration de pips adaptée selon le symbole et sa volatilité
    
    Args:
        symbol: Symbole à analyser
        df: DataFrame OHLCV pour analyse de volatilité (optionnel)
    
    Returns:
        dict: Configuration complète des pips
    """
    # Configurations de base
    base_configs = {
        "XAUUSD": {
            "pip_size": 0.1,
            "base_sl_points": 300,
            "base_tp_points": 600,
            "volatility_multiplier": 1.0,
            "description": "Or - Standard"
        },
        "GOLD": {
            "pip_size": 0.1,
            "base_sl_points": 300,
            "base_tp_points": 600,
            "volatility_multiplier": 1.0,
            "description": "Or - Standard"
        },
        "BTCUSD": {
            "pip_size": 0.1,
            "base_sl_points": 500,
            "base_tp_points": 1000,
            "volatility_multiplier": 1.0,
            "description": "Bitcoin - Plus volatil"
        },
        "EURUSD": {
            "pip_size": 0.0001,
            "base_sl_points": 30,
            "base_tp_points": 60,
            "volatility_multiplier": 1.0,
            "description": "Euro/Dollar - Standard"
        },
        "GBPUSD": {
            "pip_size": 0.0001,
            "base_sl_points": 35,
            "base_tp_points": 70,
            "volatility_multiplier": 1.0,
            "description": "Livre/Dollar - Plus volatil"
        },
        "USDJPY": {
            "pip_size": 0.01,
            "base_sl_points": 30,
            "base_tp_points": 60,
            "volatility_multiplier": 1.0,
            "description": "Dollar/Yen - Standard"
        }
    }
    
    # Obtenir la configuration de base
    config = base_configs.get(symbol, base_configs["EURUSD"])
    
    # Adapter selon la volatilité si DataFrame disponible
    if df is not None and len(df) >= 20:
        volatility_multiplier = calculate_volatility_multiplier(df, symbol)
        config["volatility_multiplier"] = volatility_multiplier
        config["base_sl_points"] = round(config["base_sl_points"] * volatility_multiplier)
        config["base_tp_points"] = round(config["base_tp_points"] * volatility_multiplier)
        config["description"] += f" (Volatilité: {volatility_multiplier:.1f}x)"
    
    return config


def calculate_volatility_multiplier(df, symbol):
    """
    Calcule le multiplicateur de volatilité selon les données récentes
    
    Args:
        df: DataFrame OHLCV
        symbol: Symbole pour ajustements spécifiques
    
    Returns:
        float: Multiplicateur de volatilité
    """
    if len(df) < 20:
        return 1.0
    
    # Calculer l'ATR récent
    atr = calculate_atr(df, 14)
    
    # ATR de référence selon symbole
    reference_atrs = {
        "XAUUSD": 15.0,   # 15$ en moyenne
        "GOLD": 15.0,
        "BTCUSD": 500.0,  # 500$ en moyenne
        "EURUSD": 0.0015, # 15 pips en moyenne
        "GBPUSD": 0.0020, # 20 pips en moyenne
        "USDJPY": 0.20    # 20 pips en moyenne
    }
    
    # Obtenir l'ATR de référence
    for key, ref_atr in reference_atrs.items():
        if key in symbol:
            reference_atr = ref_atr
            break
    else:
        reference_atr = 0.0015  # Par défaut EURUSD
    
    # Calculer le multiplicateur
    if reference_atr > 0:
        volatility_multiplier = atr / reference_atr
    else:
        volatility_multiplier = 1.0
    
    # Limiter le multiplicateur entre 0.5 et 2.0
    volatility_multiplier = max(0.5, min(2.0, volatility_multiplier))
    
    return round(volatility_multiplier, 1)


def calculate_atr(df, period=14):
    """
    Calcule l'Average True Range
    
    Args:
        df: DataFrame OHLCV
        period: Période ATR
    
    Returns:
        float: ATR calculé
    """
    if len(df) < period + 1:
        return 0.0010  # Valeur par défaut
    
    high = df['high']
    low = df['low']
    close = df['close']
    
    # True Range
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean().iloc[-1]
    
    return atr if not pd.isna(atr) else 0.0010


def calculate_adaptive_sl_tp(entry, direction, config):
    """
    Calcule SL et TP adaptés selon la configuration
    
    Args:
        entry: Prix d'entrée
        direction: Direction du trade
        config: Configuration de pips
    
    Returns:
        tuple: (sl, tp, sl_pips, tp_pips, sl_usd, tp_usd)
    """
    pip_size = config["pip_size"]
    sl_points = config["base_sl_points"]
    tp_points = config["base_tp_points"]
    
    # Calculer SL et TP
    if direction == "HAUSSIER":
        sl = entry - sl_points
        tp = entry + tp_points
    else:  # BAISSIER
        sl = entry + sl_points
        tp = entry - tp_points
    
    # Calculer les pips
    sl_pips = round(sl_points / pip_size)
    tp_pips = round(tp_points / pip_size)
    
    # Conversion en dollars pour XAU/BTC
    if "XAU" in str(config.get("description", "")) or "BTC" in str(config.get("description", "")):
        sl_usd = round(sl_points, 1)
        tp_usd = round(tp_points, 1)
    else:
        sl_usd = None
        tp_usd = None
    
    return sl, tp, sl_pips, tp_pips, sl_usd, tp_usd


def format_pips_display(symbol, sl_pips, tp_pips, sl_usd=None, tp_usd=None):
    """
    Formate l'affichage des pips selon le symbole
    
    Args:
        symbol: Symbole pour formatage
        sl_pips: SL en pips
        tp_pips: TP en pips
        sl_usd: SL en dollars (optionnel)
        tp_usd: TP en dollars (optionnel)
    
    Returns:
        tuple: (sl_text, tp_text)
    """
    if "XAU" in symbol or "GOLD" in symbol or "BTC" in symbol:
        # Format avec dollars
        sl_text = f"(-{sl_pips} pips/{sl_usd}$)" if sl_usd else f"(-{sl_pips} pips)"
        tp_text = f"(+{tp_pips} pips/{tp_usd}$)" if tp_usd else f"(+{tp_pips} pips)"
    else:
        # Format standard
        sl_text = f"(-{sl_pips} pips)"
        tp_text = f"(+{tp_pips} pips)"
    
    return sl_text, tp_text


def get_pip_summary(symbol, config):
    """
    Retourne un résumé de la configuration de pips
    
    Args:
        symbol: Symbole
        config: Configuration de pips
    
    Returns:
        str: Résumé formaté
    """
    return f"""
📊 Configuration {symbol}:
├─ Taille Pip: {config['pip_size']}
├─ SL: {config['base_sl_points']} points ({config['base_sl_points']/config['pip_size']:.0f} pips)
├─ TP: {config['base_tp_points']} points ({config['base_tp_points']/config['pip_size']:.0f} pips)
├─ Multiplicateur: {config['volatility_multiplier']:.1f}x
└─ {config['description']}
    """.strip()


# Exemple d'utilisation
    sl, tp, sl_pips, tp_pips, sl_usd, tp_usd = calculate_adaptive_sl_tp(2000.0, "HAUSSIER", config)
    print(f"\nSL: {sl} ({sl_pips} pips/{sl_usd}$)")
    print(f"TP: {tp} ({tp_pips} pips/{tp_usd}$)")
