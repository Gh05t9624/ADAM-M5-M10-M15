# app/config/optimization_config.py
# Configuration des optimisations avancées

# Scores de base par session (peuvent être ajustés dynamiquement)
BASE_SESSION_SCORES = {
    "ASIE": 65,      # Plus permissif pour plus d'opportunités
    "LONDRES": 60,    # Équilibré
    "OVERLAP": 50,    # Très permissif - meilleure session
    "NEW YORK": 60,    # Standard
    "OFF": 80          # Très sélectif hors session
}

# Scores pour signaux Telegram (plus sélectifs)
TELEGRAM_SCORE_THRESHOLDS = {
    "ASIE": 72,       # Plus sélectif pour les notifications
    "LONDRES": 70,     # Standard
    "OVERLAP": 68,      # Plus permissif en overlap
    "NEW YORK": 71,     # Modéré
    "OFF": 75           # Très sélectif
}

# Symboles prioritaires (les plus liquides et rentables)
PRIORITY_SYMBOLS = {
    "EURUSD", "GBPUSD", "XAUUSD", "USDJPY", 
    "AUDUSD", "USDCAD", "EURJPY", "GBPJPY"
}

# Symboles secondaires (si besoin de plus de trades)
SECONDARY_SYMBOLS = {
    "NZDUSD", "EURGBP", "EURCAD", "GBPAUD",
    "AUDJPY", "CADJPY", "CHFJPY", "EURNZD"
}

# Configuration multi-timeframe
MULTI_TIMEFRAME_CONFIG = {
    "enable_m10_confirmation": True,
    "enable_d1_trend_check": True,
    "m10_weight": 0.3,      # Poids de la confirmation M10
    "d1_weight": 0.2,      # Poids de la tendance Daily
    "min_m10_candles": 50,   # Minimum de bougies M10
    "min_d1_candles": 20    # Minimum de bougies Daily
}

# Configuration volume
VOLUME_CONFIG = {
    "enable_volume_filter": True,
    "min_volume_ratio": 1.5,    # Ratio volume/avg minimum
    "volume_weight": 0.15,        # Poids dans le score final
    "volume_spike_threshold": 2.0   # Seuil de spike de volume
}

# Configuration TP/SL dynamiques
DYNAMIC_LEVELS_CONFIG = {
    "enable_dynamic_levels": True,
    "base_rr_by_symbol": {
        "XAUUSD": 1.8,
        "EURUSD": 1.5,
        "GBPUSD": 1.6,
        "USDJPY": 1.4,
        "AUDUSD": 1.5,
        "USDCAD": 1.4
    },
    "volatility_adjustment": True,
    "session_adjustment": True,
    "min_rr": 1.2,
    "max_rr": 2.5
}

# Configuration détection régime marché
MARKET_REGIME_CONFIG = {
    "enable_regime_detection": True,
    "atr_period": 14,
    "trend_period": 20,
    "volatility_threshold": 0.015,  # 1.5%
    "range_threshold": 0.005,        # 0.5%
    "regime_adjustments": {
        "VOLATILE": -8,   # Plus permissif
        "RANGE": 12,       # Plus sélectif
        "TREND": 0,        # Neutre
        "UNKNOWN": 5        # Légèrement sélectif
    }
}

# Configuration corrélation
CORRELATION_CONFIG = {
    "enable_correlation_filter": True,
    "max_correlated_trades": 1,     # Max trades par groupe de corrélation
    "correlation_weight": 0.1,        # Poids dans la décision
    "exclude_highly_correlated": True
}

# Configuration temporelle
TIME_OPTIMIZATION_CONFIG = {
    "enable_time_filter": True,
    "optimal_hours": {
        "ASIE": [(0, 3), (5, 8)],
        "LONDRES": [(8, 11), (14, 16)],
        "OVERLAP": [(13, 16)],
        "NEW YORK": [(16, 19), (20, 21)],
        "OFF": []
    },
    "time_adjustments": {
        "optimal": -5,     # Plus permissif en heures optimales
        "suboptimal": 8    # Plus sélectif hors heures optimales
    }
}

# Configuration performance tracking
PERFORMANCE_CONFIG = {
    "enable_ml_prediction": True,
    "min_trades_for_ml": 50,
    "similarity_threshold": 0.8,
    "history_size": 1000,
    "prediction_weight": 0.2,      # Poids de la prédiction ML
    "performance_window": 30,       # Jours pour le calcul de performance
    "min_trades_for_stats": 5       # Minimum de trades pour stats fiables
}

# Configuration gestion du risque
RISK_MANAGEMENT_CONFIG = {
    "enable_adaptive_sizing": True,
    "base_risk_percent": 2.0,        # 2% par trade
    "max_risk_percent": 5.0,         # 5% maximum
    "risk_adjustments": {
        "high_winrate": 1.3,     # >65% winrate
        "good_winrate": 1.1,       # 55-65% winrate
        "low_winrate": 0.7         # <45% winrate
    },
    "volatility_adjustments": {
        "high": 0.7,      # >0.8 volatilité
        "medium": 1.0,    # 0.4-0.8 volatilité
        "low": 0.9        # <0.4 volatilité
    }
}

# Configuration validation avancée
ADVANCED_VALIDATION_CONFIG = {
    "enable_strict_validation": True,
    "min_confirmations": 2,           # Minimum de confirmations requises
    "confirmation_factors": {
        "trend_continuation": 1,
        "pullback_active": 1,
        "high_score": 1,             # Score >= 75
        "volume_confirmation": 1,       # Volume spike
        "multi_timeframe": 1           # Confirmation H4/D1
    },
    "high_score_threshold": 75
}

# Configuration globale
GLOBAL_CONFIG = {
    "max_trades_per_session": 8,        # Maximum de trades par session
    "max_daily_trades": 15,              # Maximum de trades par jour
    "enable_news_filter": True,           # Filtrer les news importantes
    "enable_weekend_filter": True,        # Éviter les trades week-end
    "enable_holiday_filter": True,        # Éviter les jours fériés
    "min_profit_factor": 1.3,           # Ratio profit/perte minimum
    "max_drawdown_percent": 15           # Drawdown maximum autorisé
}

# Pondérations pour le score composite
SCORE_WEIGHTS = {
    "base_score": 0.4,           # Score de base de l'analyse
    "volume_confirmation": 0.15,    # Confirmation par volume
    "multi_timeframe": 0.2,        # Confirmation multi-timeframe
    "ml_prediction": 0.1,          # Prédiction ML
    "time_optimization": 0.1,       # Optimisation temporelle
    "correlation_filter": 0.05        # Filtrage corrélation
}
