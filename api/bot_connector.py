# api/bot_connector.py
from app.utils.telegram import send_trade_signal, format_signal, send_signal
from datetime import datetime, timedelta
import MetaTrader5 as mt5

# Cache pour éviter les envois répétitifs
_sent_signals_cache = {}  # {(symbol, timeframe): {"last_sent": datetime, "last_plan": {...}}}
COOLDOWN_MINUTES = 1  # Envoi toutes les 1 minute (réduit de 5 min pour plus de réactivité)

def start_api_integration():
    """Initialise l'intégration API"""
    return True

def stop_api_integration():
    """Arrête l'intégration API"""
    pass

def _should_send_signal(symbol, trade_plan, timeframe="H4"):
    """Vérifie si un signal doit être envoyé (évite les doublons)"""
    now = datetime.utcnow()
    key = (symbol, timeframe)
    
    if key not in _sent_signals_cache:
        return True
    
    last_data = _sent_signals_cache[key]
    last_sent = last_data["last_sent"]
    
    # Vérifier le cooldown
    if now - last_sent < timedelta(minutes=COOLDOWN_MINUTES):
        return False
    
    # Vérifier si le plan a changé significativement
    last_plan = last_data["last_plan"]
    if last_plan:
        # Comparer les éléments clés
        if (trade_plan.get("entry") == last_plan.get("entry") and
            trade_plan.get("sl") == last_plan.get("sl") and
            trade_plan.get("tp") == last_plan.get("tp") and
            trade_plan.get("direction") == last_plan.get("direction")):
            return False  # Même plan, ne pas renvoyer
    
    return True

def broadcast_signal(symbol, result, df, timeframe="H4"):
    """Envoie un signal de trade avec routage automatique vers le bon canal (Forex ou Gold)"""
    try:
        # DEBUG: Log du symbole et du statut
        statut = result.get("statut", "INCONNU")
        score = result.get("score", 0)
        print(f"[DEBUG BROADCAST] {symbol} [{timeframe}] - Statut: {statut}, Score: {score}")
        
        # Générer un trade plan si possible
        from app.engine.trade_setup import generate_trade_plan_multi
        
        analysis = {
            "df": df,
            "direction": result.get("direction"),
            "symbol": symbol,
            "zone": result.get("zone", {"low": None, "high": None}),
            "score": result.get("score", 0),
            "trend_continuation": result.get("trend_continuation", False),
            "pullback_active": result.get("pullback_active", False),
            "has_impulse": result.get("has_impulse", False)
        }
        
        trade_plan = generate_trade_plan_multi(analysis, min_score=55)
        
        if trade_plan:
            print(f"[DEBUG BROADCAST] {symbol} [{timeframe}] - Trade plan généré, vérification envoi...")
            # Vérifier si on doit envoyer le signal
            if _should_send_signal(symbol, trade_plan, timeframe):
                # Récupérer le statut depuis result
                statut = result.get("statut", "INTERDIT")
                
                # Détecter si c'est un Best Trade (score élevé et trade plan disponible)
                score = result.get("score", 0)
                is_best_trade = score >= 85 and statut == "AUTORISÉ"
                
                print(f"[DEBUG BROADCAST] {symbol} [{timeframe}] - Envoi autorisé (cooldown OK)")
                # Pour le canal VIP: ignorer les trade plan non disponibles
                # Le trade plan est déjà vérifié au-dessus, donc on a un plan valide
                
                # Utiliser send_trade_signal pour le routage automatique
                send_trade_signal(symbol, trade_plan, timeframe, statut, is_best_trade)
                # Mettre en cache
                key = (symbol, timeframe)
                _sent_signals_cache[key] = {
                    "last_sent": datetime.utcnow(),
                    "last_plan": trade_plan.copy()
                }
            else:
                print(f"[DEBUG BROADCAST] {symbol} [{timeframe}] - Envoi bloqué (cooldown)")
        else:
            print(f"[DEBUG BROADCAST] {symbol} [{timeframe}] - PAS de trade plan généré")
        # Pas de fallback - on n'envoie que les signaux avec trade plan
            
    except Exception as e:
        print(f"Erreur broadcast_signal: {e}")
