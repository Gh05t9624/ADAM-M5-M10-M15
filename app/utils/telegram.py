# app/utils/telegram.py
import requests
import os
from datetime import datetime
from typing import List, Optional, Dict

TOKEN = "8543784444:AAGLiduK-VBy3tbuYYJTOFrckODtot4BnRE"
# TOKEN = "ee33444"
CHAT_ID_FOREX = "-1003808380486"
CHAT_ID_GOLD = "-1003760208475"  # À compléter avec l'ID du canal Gold
# app/utils/telegram.py

# Import du gestionnaire d'utilisateurs
try:
    from app.config.users_manager import get_users_manager
    USERS_MANAGER_AVAILABLE = True
except ImportError:
    USERS_MANAGER_AVAILABLE = False

# Import du scheduler de messages
try:
    from app.utils.message_scheduler import get_message_scheduler, should_send_telegram_message, mark_telegram_sent
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False

# Cache des messages envoyés: {(symbol, chat_id, timeframe): message_id}
_sent_messages_cache: Dict[tuple, int] = {}

def get_chat_id_for_symbol(symbol):
    """Détermine le chat_id selon le type de symbole (méthode de fallback)"""
    if "XAU" in symbol or "GOLD" in symbol:
        return CHAT_ID_GOLD if CHAT_ID_GOLD else CHAT_ID_FOREX
    return CHAT_ID_FOREX

def get_chat_ids_for_symbol(symbol: str, exclude_vip=False) -> List[str]:
    """Retourne tous les chat_ids abonnés à un symbole"""
    if USERS_MANAGER_AVAILABLE:
        users_manager = get_users_manager()
        users = users_manager.get_users_for_symbol(symbol)
        
        # DEBUG: Log des utilisateurs trouvés
        display_symbol = symbol.rstrip('c') if symbol.endswith('c') else symbol
        print(f"[DEBUG USERS] {display_symbol}: {len(users)} utilisateurs trouvés")
        for user in users:
            user_id = user.get("id", "unknown")
            chat_id = user.get("chat_id", "no_chat_id")
            print(f"  - {user_id}: {chat_id}")
        
        # Filtrer pour exclure VIP si demandé
        if exclude_vip:
            original_count = len(users)
            users = [user for user in users if user.get("id") != "VIP"]
            filtered_count = len(users)
            print(f"[DEBUG FILTER] VIP exclu: {original_count} -> {filtered_count} utilisateurs")
        
        chat_ids = [user["chat_id"] for user in users if user.get("chat_id")]
        print(f"[DEBUG FINAL] Chat IDs à envoyer: {chat_ids}")
        return chat_ids
    return []

def delete_message(chat_id: str, message_id: int) -> bool:
    """Supprime un message Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/deleteMessage"
    data = {
        "chat_id": chat_id,
        "message_id": message_id
    }
    try:
        response = requests.post(url, data=data)
        return response.status_code == 200
    except Exception as e:
        print(f"Erreur suppression message {message_id}: {e}")
        return False

def edit_message(chat_id: str, message_id: int, text: str) -> bool:
    """Modifie un message Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=data)
        return response.status_code == 200
    except Exception as e:
        print(f"Erreur modification message {message_id}: {e}")
        return False

def delete_old_messages(symbol: str, chat_ids: List[str], timeframe: str = "M10"):
    """Supprime les anciens messages pour un symbole et timeframe donnés"""
    # Retirer le suffixe 'c' pour l'affichage
    display_symbol = symbol.rstrip('c') if symbol.endswith('c') else symbol
    for cid in chat_ids:
        key = (symbol, cid, timeframe)
        if key in _sent_messages_cache:
            message_id = _sent_messages_cache[key]
            if delete_message(cid, message_id):
                del _sent_messages_cache[key]
                print(f"Message supprimé pour {display_symbol} [{timeframe}] dans {cid}")

def send_signal(text, chat_id=None, symbol=None, multi_user=False, delete_old=False, timeframe="M10", score=0):
    """Envoie un signal Telegram.

    Args:
        text: Le message à envoyer
        chat_id: Chat ID spécifique (prioritaire)
        symbol: Symbole pour déterminer les destinataires automatiquement
        multi_user: Si True, envoie à tous les utilisateurs abonnés au symbole
        delete_old: Si True, supprime les anciens messages pour ce symbole
        timeframe: Timeframe du signal (M5, M10 ou M15)
        score: Score du signal (pour filtrage par scheduler)
    """
    chat_ids = []
    
    if chat_id:
        chat_ids = [chat_id]
    elif symbol and multi_user and USERS_MANAGER_AVAILABLE:
        # Utiliser directement get_users_for_symbol sans scheduler
        chat_ids = get_chat_ids_for_symbol(symbol)
    elif symbol:
        chat_ids = [get_chat_id_for_symbol(symbol)]
    else:
        chat_ids = [CHAT_ID_FOREX]
    
    # Envoyer à tous les chat_ids
    success_count = 0
    for cid in chat_ids:
        # Vérifier si un message existe déjà pour ce symbole
        key = (symbol, cid, timeframe) if symbol else None
        message_id = _sent_messages_cache.get(key) if key else None
        
        if message_id and delete_old and symbol:
            # Modifier le message existant
            if edit_message(cid, message_id, text):
                success_count += 1
                print(f"Message modifié pour {symbol.rstrip('c') if symbol else 'unknown'} [{timeframe}] dans {cid}")
            else:
                # Si la modification échoue, supprimer et envoyer un nouveau
                delete_old_messages(symbol, [cid], timeframe)
                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                data = {
                    "chat_id"   : cid,
                    "text"      : text,
                    "parse_mode": "Markdown"
                }
                try:
                    response = requests.post(url, data=data)
                    if response.status_code == 200:
                        success_count += 1
                        if symbol:
                            result = response.json()
                            message_id = result.get("result", {}).get("message_id")
                            if message_id:
                                _sent_messages_cache[key] = message_id
                except Exception as e:
                    print(f"Telegram erreur pour {cid}: {e}")
        else:
            # Envoyer un nouveau message
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            data = {
                "chat_id"   : cid,
                "text"      : text,
                "parse_mode": "Markdown"
            }
            try:
                response = requests.post(url, data=data)
                if response.status_code == 200:
                    success_count += 1
                    # Stocker le message_id si un symbole est fourni
                    if symbol:
                        result = response.json()
                        message_id = result.get("result", {}).get("message_id")
                        if message_id:
                            _sent_messages_cache[(symbol, cid, timeframe)] = message_id
                    
                    # Marquer le message comme envoyé dans le scheduler
                    if SCHEDULER_AVAILABLE and symbol and multi_user:
                        scheduler = get_message_scheduler()
                        users_for_symbol = scheduler.get_users_for_symbol(symbol)
                        for user in users_for_symbol:
                            if user.get("chat_id") == cid:
                                user_id = user.get("id")
                                if user_id and should_send_telegram_message(user_id, symbol, score):
                                    mark_telegram_sent(user_id, symbol)
                                    break
            except Exception as e:
                # Erreur critique - on garde le print pour le debug
                print(f"Telegram erreur pour {cid}: {e}")
    
    return success_count > 0

def format_signal(symbol, plan, timeframe="M10", statut=None):
    direction_emoji = "📈" if plan['direction'] == "HAUSSIER" else "📉"
    now   = datetime.utcnow().strftime("%H:%M UTC")

    # Retirer le suffixe 'c' pour les symboles USC (cents)
    display_symbol = symbol.rstrip('c') if symbol.endswith('c') else symbol

    # Signe de reconnaissance selon timeframe
    if timeframe == "M5":
        timeframe_emoji = "🎯"  # Cible = équilibré
        timeframe_label = "M5 (Équilibré)"
    elif timeframe == "M10":
        timeframe_emoji = "📊"  # Graphique = analyse
        timeframe_label = "M10 (Fiable)"
    else:  # M15
        timeframe_emoji = "⚡"  # Éclair = rapide
        timeframe_label = "M15 (Rapide)"
    
    # Statut avec emoji et couleur
    statut_emoji = ""
    statut_text = ""
    if statut:
        if statut == "AUTORISÉ":
            statut_emoji = "✅"
            statut_text = "AUTORISÉ"
        elif statut == "SURVEILLANCE":
            statut_emoji = "⚠️"
            statut_text = "SURVEILLANCE"
        else:  # INTERDIT
            statut_emoji = "❌"
            statut_text = "INTERDIT"

    entry = plan.get("entry")
    sl    = plan.get("sl")
    tp    = plan.get("tp")
    score = plan.get("score")
    rr    = plan.get("rr", 0)

    # Pip selon symbole avec conversion FOREX/XAU/BTC
    if "JPY" in display_symbol:
        pip = 0.01
        sl_pips = round(abs(entry - sl) / pip)
        tp_pips = round(abs(tp - entry) / pip)
    elif "XAU" in display_symbol or "GOLD" in display_symbol:
        pip = 0.1
        # 🎯 Norme corrigée XAU : SL = 300 points (30$), TP = 600 points (60$)
        sl_points = abs(entry - sl) if entry and sl else 300  # Valeur par défaut
        tp_points = abs(tp - entry) if entry and tp else 600  # Valeur par défaut
        sl_pips = round(sl_points / pip)  # Pips réels
        tp_pips = round(tp_points / pip)  # Pips réels
        # Conversion en dollars pour clarté
        sl_usd = round(sl_points, 1)
        tp_usd = round(tp_points, 1)
    elif "BTC" in display_symbol:
        pip = 0.1
        # 🎯 Norme corrigée BTC : SL = 500 points (50$), TP = 1000 points (100$) - plus volatil
        sl_points = abs(entry - sl) if entry and sl else 500  # Valeur par défaut
        tp_points = abs(tp - entry) if entry and tp else 1000  # Valeur par défaut
        sl_pips = round(sl_points / pip)  # Pips réels
        tp_pips = round(tp_points / pip)  # Pips réels
        # Conversion en dollars pour clarté
        sl_usd = round(sl_points, 1)
        tp_usd = round(tp_points, 1)
    else:
        pip = 0.0001
        sl_pips = round(abs(entry - sl) / pip)
        tp_pips = round(abs(tp - entry) / pip)

    return f"""
🤖 *ADAM — SIGNAL*
━━━━━━━━━━━━━━━━━━
{timeframe_emoji} *{display_symbol}* | `{plan['type']}` | `{timeframe_label}`
{direction_emoji} Direction : *{plan['direction']}*
{statut_emoji} Statut : *{statut_text}*
🕐 Heure : `{now}`
━━━━━━━━━━━━━━━━━━
🎯 Entry : `{entry}`
🛑 SL    : `{sl}` _(-{sl_pips} pips{"/" + str(sl_usd) + "$" if "XAU" in display_symbol or "GOLD" in display_symbol or "BTC" in display_symbol else ""})_
💰 TP    : `{tp}` _(+{tp_pips} pips{"/" + str(tp_usd) + "$" if "XAU" in display_symbol or "GOLD" in display_symbol or "BTC" in display_symbol else ""})_
━━━━━━━━━━━━━━━━━━
⚖️ RR    : `1:{rr}`
⭐ Score : `{score}/100`
━━━━━━━━━━━━━━━━━━
🧠 _TP dynamique adapté au marché_
⚠️ _Pas un conseil financier_
    """


def send_trade_signal(symbol, plan, timeframe="M10", statut=None, is_best_trade=False):
    text = format_signal(symbol, plan, timeframe, statut)
    
    # DEBUG: Log pour vérifier le filtrage
    display_symbol = symbol.rstrip('c') if symbol.endswith('c') else symbol
    print(f"[DEBUG SIGNAL] {display_symbol} [{timeframe}] - Statut: {statut}, BestTrade: {is_best_trade}")
    
    # Pour le canal VIP, n'envoyer que si AUTORISÉ ou Best Trade
    if statut == "AUTORISÉ" or is_best_trade:
        print(f"[DEBUG SIGNAL] {display_symbol} [{timeframe}] -> Envoi TOUS les canaux (AUTORISÉ/Best)")
        return send_signal(text, symbol=symbol, multi_user=True, delete_old=True, timeframe=timeframe)
    elif statut in ["INTERDIT", "SURVEILLANCE"]:
        print(f"[DEBUG SIGNAL] {display_symbol} [{timeframe}] -> Envoi SANS VIP (exclus)")
        # Filtrer pour exclure le canal VIP
        return _send_signal_filtered(text, symbol=symbol, multi_user=True, delete_old=True, timeframe=timeframe, exclude_vip=True)
    else:
        print(f"[DEBUG SIGNAL] {display_symbol} [{timeframe}] -> Envoi TOUS les canaux (statut inconnu)")
        return send_signal(text, symbol=symbol, multi_user=True, delete_old=True, timeframe=timeframe)

def _send_signal_filtered(text, chat_id=None, symbol=None, multi_user=False, delete_old=False, timeframe="M10", exclude_vip=False):
    """Envoie un signal Telegram avec filtre (exclure VIP si demandé)"""
    chat_ids = []
    
    if chat_id:
        chat_ids = [chat_id]
    elif symbol and multi_user and USERS_MANAGER_AVAILABLE:
        chat_ids = get_chat_ids_for_symbol(symbol, exclude_vip=exclude_vip)
    elif symbol:
        chat_ids = [get_chat_id_for_symbol(symbol)]
    else:
        chat_ids = [CHAT_ID_FOREX]
    
    # Supprimer les anciens messages si demandé
    if delete_old and symbol:
        delete_old_messages(symbol, chat_ids, timeframe)
    
    # Envoyer à tous les chat_ids
    success_count = 0
    for cid in chat_ids:
        url  = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {
            "chat_id": cid,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                success_count += 1
                result = response.json()
                message_id = result.get("result", {}).get("message_id")
                if message_id:
                    _sent_messages_cache[(symbol, cid, timeframe)] = message_id
        except Exception as e:
            # Erreur critique - on garde le print pour le debug
            print(f"Telegram erreur pour {cid}: {e}")
    
    return success_count > 0


def send_tp_hit(symbol, price):
    # Retirer le suffixe 'c' pour l'affichage
    display_symbol = symbol.rstrip('c') if symbol.endswith('c') else symbol
    text = f"""
🎯 *TP ATTEINT — {display_symbol}*
━━━━━━━━━━━━━━━━━━
💰 Prix : `{price}`
✅ Objectif validé !
━━━━━━━━━━━━━━━━━━
👁️ _Ghost Analyzer_
    """
    send_signal(text, symbol=symbol)


def send_sl_hit(symbol, price):
    # Retirer le suffixe 'c' pour l'affichage
    display_symbol = symbol.rstrip('c') if symbol.endswith('c') else symbol
    text = f"""
❌ *SL TOUCHÉ — {display_symbol}*
━━━━━━━━━━━━━━━━━━
🛑 Prix : `{price}`
⚠️ Position stoppée
━━━━━━━━━━━━━━━━━━
👁️ _Ghost Analyzer_
    """
    send_signal(text, symbol=symbol)


def send_session_open(session):
    sessions = {
        "ASIE"    : ("🟠", "00h00", "Score min : 70"),
        "LONDRES" : ("🔵", "08h00", "Score min : 60"),
        "OVERLAP" : ("🟣", "13h00", "Score min : 50 🔥 GOLD TIME"),
        "NEW YORK": ("🔴", "17h00", "Score min : 55"),
    }
    if session not in sessions:
        return
    emoji, heure, info = sessions[session]
    text = f"""
{emoji} *SESSION {session} — OUVERTE*
━━━━━━━━━━━━━━━━━━
🕐 Heure : `{heure} UTC`
📊 {info}
🤖 Analyse en cours...
━━━━━━━━━━━━━━━━━━
🤖 _ADAM actif_
    """
    # Envoyer à tous les utilisateurs actifs
    if USERS_MANAGER_AVAILABLE:
        from app.config.users_manager import get_users_manager
        users_manager = get_users_manager()
        chat_ids = users_manager.get_all_chat_ids()
        for cid in chat_ids:
            send_signal(text, chat_id=cid)
    else:
        send_signal(text)


def send_session_close(session):
    sessions = {
        "ASIE"    : ("🟠", "08h00"),
        "LONDRES" : ("🔵", "17h00"),
        "OVERLAP" : ("🟣", "17h00"),
        "NEW YORK": ("🔴", "22h00"),
    }
    if session not in sessions:
        return
    emoji, heure = sessions[session]
    text = f"""
{emoji} *SESSION {session} — FERMÉE*
━━━━━━━━━━━━━━━━━━
🕐 Heure : `{heure} UTC`
😴 Marché en pause...
━━━━━━━━━━━━━━━━━━
🤖 _ADAM en veille_
    """
    # Envoyer à tous les utilisateurs actifs
    if USERS_MANAGER_AVAILABLE:
        from app.config.users_manager import get_users_manager
        users_manager = get_users_manager()
        chat_ids = users_manager.get_all_chat_ids()
        for cid in chat_ids:
            send_signal(text, chat_id=cid)
    else:
        send_signal(text)


def send_daily_summary(stats):
    winrate  = stats.get("winrate", 0)
    total    = stats.get("total_trades", 0)
    wins     = stats.get("authorized", 0)
    emoji_wr = "🟢" if winrate >= 60 else "🟡" if winrate >= 50 else "🔴"
    text = f"""
📊 *ADAM — RÉSUMÉ JOURNALIER*
━━━━━━━━━━━━━━━━━━
🗓️ Date : `{datetime.utcnow().strftime("%d/%m/%Y")}`
━━━━━━━━━━━━━━━━━━
📈 Trades analysés : `{total}`
✅ Signaux envoyés : `{wins}`
{emoji_wr} Winrate : `{winrate}%`
━━━━━━━━━━━━━━━━━━
🤖 _ADAM — Bonne nuit_ 🌙
    """
    send_signal(text)


def send_startup():
    now = datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC")
    text = f"""
🤖 *ADAM — ONLINE*
━━━━━━━━━━━━━━━━━━
🤖 Bot IA démarré avec succès
⚡ Analyse des marchés en cours...
🌍 Multi-Marchés • 24h/24
🕐 `{now}`
━━━━━━━━━━━━━━━━━━
✅ _Système opérationnel_
    """
    send_signal(text)
    
def send_direction_change(symbol, old_direction, new_direction):
    # Retirer le suffixe 'c' pour l'affichage
    display_symbol = symbol.rstrip('c') if symbol.endswith('c') else symbol
    old_emoji = "📈" if old_direction == "HAUSSIER" else "📉"
    new_emoji = "📈" if new_direction == "HAUSSIER" else "📉"
    now = datetime.utcnow().strftime("%H:%M UTC")

    text = f"""
🔄 *CHANGEMENT DE DIRECTION — {display_symbol}*
━━━━━━━━━━━━━━━━━━
{old_emoji} Avant : *{old_direction}*
{new_emoji} Maintenant : *{new_direction}*
🕐 Heure : `{now}`
━━━━━━━━━━━━━━━━━━
⚡ _Nouveau signal en cours d'analyse..._
👁️ _Ghost Analyzer_
    """
    send_signal(text, symbol=symbol)