import tkinter as tk
import tkinter.messagebox as messagebox
from datetime import datetime, timedelta
import winsound

from app.ui.components import GhostButton
from app.ui.trade_journal_window import TradeJournalWindow
from app.ui.trade_plan_window import TradePlanWindow
from app.ui.favorites_panel import FavoritesPanel
from app.ui.symbol_selector import SymbolSelector
from app.ui.image_analyzer import ImageAnalyzer
from app.ui.users_manager_window import UsersManagerWindow

from app.ui.stats_panel import StatsPanel
from app.ui.symbol_selector import SymbolSelector
from app.ui.image_analyzer import ImageAnalyzer
from app.ui.users_manager_window import UsersManagerWindow

from app.engine.analyzer import MarketAnalyzer
from app.engine.trade_setup import generate_trade_plan_multi
from app.engine.priority import compute_priority

from app.data.mt5_provider import MT5Provider
from app.services.market_analysis_service import MarketAnalysisService
from app.journal.trade_journal import TradeJournal
from app.engine.stats import StatsEngine
from app.engine.session_filter import is_trading_session, get_session_info
from app.engine.news_filter import is_news_time

from app.utils.telegram import (
    send_signal, send_trade_signal, send_session_open,
    send_session_close, send_daily_summary, format_signal,
    get_chat_ids_for_symbol, delete_old_messages
)
from app.utils.news_sharing import get_news_sharing_service

# API Integration
try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from api.bot_connector import start_api_integration, broadcast_signal, stop_api_integration
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

# 🚀 Optimisations avancées
from app.engine.advanced_optimizations import (
    MultiTimeframeValidator, VolumeValidator, DynamicLevelCalculator,
    MarketRegimeDetector, CorrelationFilter, TimeOptimizer,
    AdvancedPerformanceTracker, PositionSizer
)
from app.config.optimization_config import (
    BASE_SESSION_SCORES, TELEGRAM_SCORE_THRESHOLDS, PRIORITY_SYMBOLS, SECONDARY_SYMBOLS,
    MULTI_TIMEFRAME_CONFIG, VOLUME_CONFIG, DYNAMIC_LEVELS_CONFIG,
    MARKET_REGIME_CONFIG, CORRELATION_CONFIG, TIME_OPTIMIZATION_CONFIG,
    PERFORMANCE_CONFIG, RISK_MANAGEMENT_CONFIG, ADVANCED_VALIDATION_CONFIG,
    GLOBAL_CONFIG, SCORE_WEIGHTS
)

# SAFE import (évite crash hors Windows)
try:
    import winsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False
    winsound = None


def get_active_session(hour):
    """Retourne la session active selon l'heure UTC"""
    if 22 <= hour or hour < 8:
        return "ASIE"
    elif 8 <= hour < 13:
        return "LONDRES"
    elif 13 <= hour < 17:
        return "OVERLAP"
    elif 17 <= hour < 22:
        return "NEW YORK"
    else:
        return "OFF"


class GhostUI(tk.Frame):
    """
    Interface principale du Ghost Analyzer
    
    Structure du layout:
    ├── HEADER
    │   ├── Titre
    │   ├── Best Trade Label
    │   ├── Notification Zone
    │   ├── Boutons (Analyse Image, Sélection Marchés)
    │   ├── Search Bar
    │   ├── Score Slider
    │   └── Clock
    ├── MAIN CONTENT
    │   ├── TENDANCES (3 colonnes)
    │   │   ├── Haussier
    │   │   ├── Baissier
    │   │   └── Neutre
    │   ├── STATUTS (3 colonnes)
    │   │   ├── Interdit
    │   │   ├── Surveillance
    │   │   └── Autorisé
    │   └── STATS PANEL
    └── CLOCK
    """

    def __init__(self, parent):
        print("=" * 60)
        print("[DEBUG CLOCK] 🚀 INITIALISATION DE GHOSTUI - DÉBUT")
        print("=" * 60)
        super().__init__(parent, bg="#0B0F14")
        
        # ============================================================================
        # INITIALISATION DES VARIABLES - UNE SEULE FOIS
        # ============================================================================
        
        # Score management
        self.min_score = 55
        
        # Mode trading
        self.MODE = "NORMAL"  # RELAX / NORMAL / STRICT
        
        # Contrôle d'analyse
        self.is_analyzing = False
        self.alerted_markets = set()
        self.current_best_trade = None
        
        # Système de cooldown pour les notifications sonores
        self.sound_notifications = {}  # {symbol: last_notification_time}
        self.notification_cooldown = 120  # 2 minutes en secondes
        
        # État du trading
        self.active_trades = {}
        self.sent_signals = set()
        self.last_directions = {}
        self.direction_history = {}
        self.cached_results = {}
        self.last_session = None
        self.last_summary_day = None
        self._status_results = {
            "INTERDIT": [],
            "SURVEILLANCE": [],
            "AUTORISÉ": [],
            "OPPORTUNITÉ": []
        }
        
        # ============================================================================
        # CORE COMPONENTS - UNE SEULE FOIS
        # ============================================================================
        
        # Data & Analysis - Utilisation de la couche de services pour séparation métier/UI
        self.market_service = MarketAnalysisService()
        # Maintien des références directes pour compatibilité avec l'UI existante
        self.analyzer = self.market_service.analyzer
        self.data_provider = self.market_service.mt5_provider
        self.journal = TradeJournal("journal_trades.csv")
        self.stats_engine = StatsEngine("journal_trades.csv")
        
        # Performance tracking
        self.performance_tracker = AdvancedPerformanceTracker()
        
        # API
        self.api_enabled = False
        if API_AVAILABLE:
            try:
                self.api_enabled = start_api_integration()
            except Exception as e:
                print(f"Erreur initialisation API: {e}")
        
        # Symboles sélectionnés par défaut
        self.selected_symbols = ["EURUSD", "GBPUSD", "XAUUSD"]
        
        # Stats par défaut
        self.last_stats = {
            "total_trades": 0,
            "authorized": 0,
            "by_symbol": {},
            "by_direction": {},
            "winrate": 0
        }
        
        # ============================================================================
        # SYSTÈMES INDÉPENDANTS DE CARTES
        # ============================================================================
        
        # Système 1: TENDANCES (Haussier / Baissier / Neutre)
        self._trend_results = {
            "Haussier": None,   # Frame à populer
            "Baissier": None,
            "Neutre": None
        }
        self.trend_cards = {}  # Stocker les frames des cartes de tendance
        
        # Système 2: STATUTS (Autorisé / Surveillance / Interdit)
        self.status_cards = {
            "AUTORISÉ": None,      # Frame à populer
            "SURVEILLANCE": None,
            "INTERDIT": None
        }
        
        # ============================================================================
        # CONSTRUCTION DU LAYOUT - ORDRE CORRECT
        # ============================================================================
        
        # 1. HEADER (avec clock, boutons, etc.)
        print("[DEBUG CLOCK] Étape 1: Création du header...")
        header = self._build_header()
        print(f"[DEBUG CLOCK] Header créé: {header}")
        header.pack(fill="x", padx=20, pady=10)
        print("[DEBUG CLOCK] Header packé")
        
        # 2. CONTENU PRINCIPAL
        self._build_main_content()
        
        # 3. START LIVE LOOP
        self.start_live_loop()

    # ============================================================================
    # NOTIFICATIONS SONORES
    # ============================================================================

    def play_notification_sound(self, sound_type="authorization"):
        """Joue un son de notification"""
        try:
            if sound_type == "authorization":
                # Son pour autorisation - 2 bips courts
                winsound.Beep(1000, 200)  # 1000 Hz, 200ms
                winsound.Beep(1200, 200)  # 1200 Hz, 200ms
            elif sound_type == "opportunity":
                # Son pour opportunité - 3 bips rapides
                winsound.Beep(800, 150)   # 800 Hz, 150ms
                winsound.Beep(1000, 150) # 1000 Hz, 150ms
                winsound.Beep(1200, 150) # 1200 Hz, 150ms
            elif sound_type == "alert":
                # Son d'alerte - bip long
                winsound.Beep(600, 500)  # 600 Hz, 500ms
        except Exception as e:
            print(f"[ERROR SOUND] Erreur lors de la lecture du son: {e}")

    def _should_notify_authorization(self, symbol, new_status):
        """Vérifie si on doit notifier le changement de statut"""
        # Stocker les statuts précédents pour éviter les notifications répétées
        if not hasattr(self, '_previous_statuses'):
            self._previous_statuses = {}
        
        previous_status = self._previous_statuses.get(symbol)
        self._previous_statuses[symbol] = new_status
        
        # Notifier si le statut passe à AUTORISÉ ou OPPORTUNITÉ depuis un autre statut
        if new_status in ["AUTORISÉ", "OPPORTUNITÉ"] and previous_status not in ["AUTORISÉ", "OPPORTUNITÉ"]:
            return True
        return False
    
    def _should_play_sound(self, symbol, sound_type):
        """Vérifie si on doit jouer un son (avec cooldown)"""
        from datetime import datetime, timedelta
        
        current_time = datetime.now()
        
        # Vérifier si une notification a déjà été envoyée récemment pour ce symbole
        if symbol in self.sound_notifications:
            last_notification = self.sound_notifications[symbol]
            time_since_last = (current_time - last_notification).total_seconds()
            
            if time_since_last < self.notification_cooldown:
                print(f"[SOUND COOLDOWN] {symbol} - Dernière notification il y a {int(time_since_last)}s (cooldown: {self.notification_cooldown}s)")
                return False
        
        # Enregistrer cette notification
        self.sound_notifications[symbol] = current_time
        return True

    # ============================================================================
    # HEADER BUILDING
    # ============================================================================
    
    def _build_header(self):
        """Construit l'en-tête avec tous les contrôles"""
        header = tk.Frame(self, bg="#0B0F14")

        # Titre
        title = tk.Label(
            header,
            text="A.D.A.M 🤖",
            fg="#E5E7EB",
            bg="#0B0F14",
            font=("Segoe UI", 18, "bold")
        )
        title.pack(side="left", padx=20)
        
        # Best Trade Label
        self.best_trade_label = tk.Label(
            header,
            text="",
            fg="#FACC15",
            bg="#0B0F14",
            font=("Segoe UI", 12, "bold")
        )
        self.best_trade_label.pack(side="left", padx=20)
        
        # Notification Zone
        self.notification_frame = tk.Frame(header, bg="#0B0F14")
        self.notification_frame.pack(side="right", padx=20)
        
        self.notification_label = tk.Label(
            self.notification_frame,
            text="",
            fg="#22C55E",
            bg="#0B0F14",
            font=("Segoe UI", 10, "bold"),
            wraplength=300
        )
        self.notification_label.pack()

        # Boutons
        image_btn = GhostButton(
            header,
            text="Analyse Image",
            command=self.show_image_analyzer,
            smaller=True
        )
        image_btn.pack(side="right", padx=5)
        
        symbol_btn = GhostButton(
            header,
            text="Marchés (3)",
            command=self.show_symbol_selector,
            smaller=True
        )
        symbol_btn.pack(side="right", padx=5)
        
        journal_btn = GhostButton(
            header,
            text="📊 Journal",
            command=self.show_trade_journal,
            smaller=True
        )
        journal_btn.pack(side="right", padx=5)
        
        # Bouton Analyser
        analyze_btn = GhostButton(
            header,
            text="Analyser",
            command=self.on_analyze,
            smaller=True
        )
        analyze_btn.pack(side="right", padx=10)
        
        # Loading Label
        self.loading_label = tk.Label(
            header,
            text="",
            fg="#9CA3AF",
            bg="#0B0F14",
            font=("Segoe UI Emoji", 12, "bold")
        )
        self.loading_label.pack(side="right", padx=15)

        return header

    def _build_clock(self, parent):
        """Construit la zone d'horloge"""
        print("[DEBUG CLOCK] Étape 3: Création du frame horloge...")
        self.clock_frame = tk.Frame(parent, bg="#0B0F14")
        self.clock_frame.pack(side="right", padx=10, pady=5)
        print(f"[DEBUG CLOCK] Frame horloge créé et packé: {self.clock_frame}")

        print("[DEBUG CLOCK] Création des labels...")
        self.label_sng = tk.Label(self.clock_frame, text="SNG --:--:-- | ", fg="#FFFFFF", bg="#0B0F14", font=("Consolas", 12, "bold"))
        self.label_asie = tk.Label(self.clock_frame, text="ASIE --:--:-- | ", fg="#FF9800", bg="#0B0F14", font=("Consolas", 12, "bold"))
        self.label_lon = tk.Label(self.clock_frame, text="LON --:--:-- | ", fg="#2196F3", bg="#0B0F14", font=("Consolas", 12, "bold"))
        self.label_ny = tk.Label(self.clock_frame, text="NY --:--:-- | ", fg="#F44336", bg="#0B0F14", font=("Consolas", 12, "bold"))
        self.label_session = tk.Label(self.clock_frame, text="[ OFF ]", fg="#757575", bg="#0B0F14", font=("Consolas", 12, "bold"))
        print("[DEBUG CLOCK] Labels créés")

        print("[DEBUG CLOCK] Packing des labels...")
        self.label_sng.pack(side="left")
        self.label_asie.pack(side="left")
        self.label_lon.pack(side="left")
        self.label_ny.pack(side="left")
        self.label_session.pack(side="left")
        print("[DEBUG CLOCK] Labels packés")
        
        print("[DEBUG CLOCK] Lancement du premier update_clock...")
        self.update_clock()

    def update_clock(self):
        """Mets à jour l'horloge et la session"""
        now_utc = datetime.utcnow()

        senegal = now_utc
        tokyo = now_utc + timedelta(hours=9)
        london = now_utc + timedelta(hours=1)
        newyork = now_utc - timedelta(hours=4)

        sng = senegal.strftime("%H:%M:%S")
        tok = tokyo.strftime("%H:%M:%S")
        lon = london.strftime("%H:%M:%S")
        ny = newyork.strftime("%H:%M:%S")

        active = get_active_session(senegal.hour)

        session_colors = {
            "ASIE": "#FF9800",
            "LONDRES": "#2196F3",
            "OVERLAP": "#9C27B0",
            "NEW YORK": "#F44336",
            "OFF": "#757575",
        }
        color_session = session_colors.get(active, "#FFFFFF")

        # Mettre à jour les labels
        self.label_sng.config(text=f"SNG {sng} | ")
        self.label_asie.config(text=f"ASIE {tok} | ")
        self.label_lon.config(text=f"LON {lon} | ")
        self.label_ny.config(text=f"NY {ny} | ")
        self.label_session.config(text=f"[ {active} ]", fg=color_session)

        self.after(1000, self.update_clock)

    # ============================================================================
    # MAIN CONTENT BUILDING
    # ============================================================================
    
    def _build_main_content(self):
        """Construit le contenu principal (tendances + statuts + stats)"""
        
        # Container principal
        main_container = tk.Frame(self, bg="#0B0F14")
        main_container.pack(fill="both", expand=True, padx=20)
        
        # Container pour les tendances et statuts
        content_container = tk.Frame(main_container, bg="#0B0F14")
        content_container.pack(fill="both", expand=True)
        
        # 1. TENDANCES
        self._build_trends_section(content_container)
        
        # 2. STATUTS
        self._build_status_section(content_container)
        
        # 3. STATS PANEL
        self.stats_panel = StatsPanel(main_container)
        self.stats_panel.pack(side="bottom", fill="x", pady=10)
        
        # UI Components (pour sélecteurs et analyseurs)
        self.favorites_panel = FavoritesPanel(self, self)
        self.symbol_selector = SymbolSelector(self, self)
        self.image_analyzer = ImageAnalyzer(self)

    def _build_trends_section(self, parent):
        """Construit la section des tendances"""
        container = tk.Frame(parent, bg="#0B0F14")
        container.pack(fill="both", expand=True, padx=10)

        # Frame horizontal pour titre + horloge
        title_frame = tk.Frame(container, bg="#0B0F14")
        title_frame.pack(fill="x", padx=10, pady=(10, 5))

        title = tk.Label(
            title_frame,
            text="Tendance des marchés",
            fg="#E5E7EB",
            bg="#0B0F14",
            font=("Segoe UI", 14, "bold")
        )
        title.pack(side="left")

        # Horloge à côté du titre
        self.clock_frame = tk.Frame(title_frame, bg="#0B0F14")
        self.clock_frame.pack(side="right", padx=10)

        self.label_sng = tk.Label(self.clock_frame, text="SNG --:--:--", fg="#FFFFFF", bg="#0B0F14", font=("Consolas", 10, "bold"))
        self.label_asie = tk.Label(self.clock_frame, text="ASIE --:--:--", fg="#FF9800", bg="#0B0F14", font=("Consolas", 10, "bold"))
        self.label_lon = tk.Label(self.clock_frame, text="LON --:--:--", fg="#2196F3", bg="#0B0F14", font=("Consolas", 10, "bold"))
        self.label_ny = tk.Label(self.clock_frame, text="NY --:--:--", fg="#F44336", bg="#0B0F14", font=("Consolas", 10, "bold"))
        self.label_session = tk.Label(self.clock_frame, text="[ OFF ]", fg="#757575", bg="#0B0F14", font=("Consolas", 10, "bold"))

        self.label_sng.pack(side="left", padx=2)
        self.label_asie.pack(side="left", padx=2)
        self.label_lon.pack(side="left", padx=2)
        self.label_ny.pack(side="left", padx=2)
        self.label_session.pack(side="left", padx=2)

        # Lancer update_clock
        self.update_clock()

        # 3 colonnes de tendances
        for title, color in [
            ("Haussier", "#22C55E"),
            ("Baissier", "#EF4444"),
            ("Neutre", "#9CA3AF"),
        ]:
            card = self._create_scrollable_card(container, title, color)
            self.trend_cards[title] = card

    def _build_status_section(self, parent):
        """Construit la section des statuts"""
        container = tk.Frame(parent, bg="#0B0F14")
        container.pack(fill="both", expand=True, padx=10)

        title = tk.Label(
            container,
            text="Statut du marché",
            fg="#E5E7EB",
            bg="#0B0F14",
            font=("Segoe UI", 14, "bold")
        )
        title.pack(anchor="w", padx=10, pady=(10, 5))

        # 3 colonnes de statuts
        for title, color in [
            ("AUTORISÉ", "#22C55E"),
            ("SURVEILLANCE", "#FACC15"),
            ("INTERDIT", "#EF4444"),
        ]:
            card = self._create_scrollable_card(container, title, color)
            self.status_cards[title] = card

    def _create_scrollable_card(self, parent, title, color):
        """Crée une carte scrollable réutilisable"""
        card = tk.Frame(parent, bg="#111827")
        card.pack(side="left", expand=True, fill="both", padx=10, pady=10)

        # Titre
        lbl = tk.Label(
            card,
            text=f"MARCHÉS {title.upper()}S",
            fg=color,
            bg="#111827",
            font=("Segoe UI", 14, "bold")
        )
        lbl.pack(anchor="w", padx=15, pady=10)

        # Canvas avec scrollbar
        canvas = tk.Canvas(
            card,
            bg="#111827",
            highlightthickness=0,
            height=200
        )
        
        scrollbar = tk.Scrollbar(
            card,
            orient="vertical",
            command=canvas.yview,
            width=8,
            bg="#374151",
            troughcolor="#1F2937",
            activebackground="#4B5563"
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y", padx=(2, 0))
        canvas.pack(side="left", fill="both", expand=True)
        
        # Frame scrollable
        content = tk.Frame(canvas, bg="#111827")
        content_window = canvas.create_window((0, 0), window=content, anchor="nw")
        
        # Update scroll region
        def on_frame_configure(event, c=canvas):
            c.configure(scrollregion=c.bbox("all"))
        
        def on_canvas_configure(event, c=canvas, cw=content_window):
            c.itemconfig(cw, width=event.width)
        
        content.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Scroll with mouse
        def on_mousewheel(event):
            try:
                if hasattr(event, 'delta'):
                    scroll_amount = int(-1 * (event.delta / 120))
                    canvas.yview_scroll(scroll_amount, "units")
                else:
                    scroll_amount = -1 if event.num == 4 else 1
                    canvas.yview_scroll(scroll_amount, "units")
            except:
                pass
        
        canvas.bind("<MouseWheel>", on_mousewheel)
        content.bind("<MouseWheel>", on_mousewheel)
        
        try:
            canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
            canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        except:
            pass

        return content

    # ============================================================================
    # MARKET MANAGEMENT
    # ============================================================================
    
    def add_market(self, category, symbol, direction=None, score=None, result=None):
        """Ajoute un marché à une catégorie (tendances OU statuts)"""
        
        # Déterminer le frame cible
        if category in self.trend_cards:
            frame = self.trend_cards[category]
        elif category in self.status_cards:
            frame = self.status_cards[category]
        else:
            print(f"[ERROR] Catégorie inconnue: {category}")
            return
        
        if frame is None:
            print(f"[ERROR] Frame vide pour: {category}")
            return
        
        # Supprimer des autres catégories
        self._remove_symbol_from_other_categories(symbol, category)

        color = self._score_color(score) if score is not None else "#9CA3AF"

        # Frame marché
        market_frame = tk.Frame(frame, bg="#111827")
        market_frame.pack(anchor="w", pady=3, fill="x")

        # Status de Trade Plan et Session
        tp_available = result and result.get("trade_plan_available")
        session_ok = result and result.get("session_ok", True)
        news_blocked = result and result.get("news_block", False)
        
        # Déterminer le texte et couleur de statut
        if news_blocked:
            tp_text = " ⚠️ NEWS"
            tp_color = "#F59E0B"  # Orange
        elif not session_ok:
            tp_text = " 🔴 FERMÉ"
            tp_color = "#EF4444"  # Rouge
        elif tp_available:
            tp_text = " ✅ TP"
            tp_color = "#22C55E"  # Vert
        else:
            tp_text = " ❌ NO TP"
            tp_color = "#6B7280"  # Gris

        # Base text - retirer le suffixe 'c' pour les symboles USC (cents)
        display_symbol = symbol.rstrip('c') if symbol.endswith('c') else symbol
        base_text = f"{display_symbol} ({score})" if score else display_symbol
        
        # Frame principal pour le texte
        text_frame = tk.Frame(market_frame, bg="#111827")
        text_frame.pack(side=tk.LEFT, fill="x", expand=True)
        
        lbl = tk.Label(
            text_frame,
            text=base_text,
            fg=color,
            bg="#111827",
            font=("Segoe UI", 11, "bold" if score and score >= 80 else "normal")
        )
        lbl.pack(side="left", padx=(0, 5))

        # TP label
        tp_lbl = tk.Label(
            text_frame,
            text=tp_text,
            fg=tp_color,
            bg="#111827",
            font=("Segoe UI", 10, "bold")
        )
        tp_lbl.pack(side="left", padx=(5, 5))

        # Decision label
        decision = result.get("decision", "") if result else ""
        decision_color = {
            "A+ TRADE": "#22C55E",
            "A TRADE": "#4ADE80",
            "B TRADE": "#FACC15",
            "SKIP": "#6B7280"
        }.get(decision, "#6B7280")

        if decision:
            decision_lbl = tk.Label(
                market_frame,
                text=decision,
                fg=decision_color,
                bg="#111827",
                font=("Segoe UI", 10, "bold")
            )
            decision_lbl.pack(side="left", padx=(5, 5))

        # Trade Plan Button - couleur selon le statut ET la disponibilité du trade plan
        status = result.get("statut", "INTERDIT") if result else "INTERDIT"
        
        # Définir la couleur du bouton selon le statut ET la disponibilité
        if not tp_available:
            # Trade plan non disponible : gris (quelle que soit le statut)
            btn_bg = "#1F2937"  # Gris
            btn_fg = "#FFFFFF"  # Texte blanc
        elif status == "AUTORISÉ" or status == "OPPORTUNITÉ":
            # Trade plan disponible + AUTORISÉ : vert
            btn_bg = "#22C55E"  # Vert
            btn_fg = "#020617"  # Texte foncé
        elif status == "SURVEILLANCE":
            # Trade plan disponible + SURVEILLANCE : jaune
            btn_bg = "#FACC15"  # Jaune
            btn_fg = "#020617"  # Texte foncé
        else:
            # Trade plan disponible + INTERDIT : gris par défaut
            btn_bg = "#1F2937"  # Gris
            btn_fg = "#FFFFFF"  # Texte blanc
        
        btn = tk.Button(
            market_frame,
            text="Trade Plan",
            font=("Segoe UI", 9, "bold"),
            bg=btn_bg,
            fg=btn_fg,
            relief="flat",
            cursor="hand2",
            command=lambda s=symbol: self.open_trade_plan(symbol=s)
        )
        btn.pack(side="right")

    def _remove_symbol_from_other_categories(self, symbol, current_category):
        """Supprime un symbole des autres catégories"""
        all_categories = list(self.trend_cards.keys()) + list(self.status_cards.keys())
        
        for category in all_categories:
            if category == current_category:
                continue
            
            # Récupérer le frame
            if category in self.trend_cards:
                frame = self.trend_cards[category]
            else:
                frame = self.status_cards[category]
            
            if not frame:
                continue
            
            # Chercher et supprimer le symbole
            for widget in list(frame.winfo_children()):
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Label):
                            text = child.cget("text")
                            if symbol in text and "(" in text:
                                widget.destroy()
                                break

    def _score_color(self, score):
        """Retourne la couleur selon le score"""
        if score >= 80:
            return "#22C55E"  # Vert
        if score >= 60:
            return "#FACC15"  # Jaune
        return "#6B7280"      # Gris

    def clear_markets(self):
        """Vide tous les marchés affichés"""
        for frame in list(self.trend_cards.values()) + list(self.status_cards.values()):
            if frame:
                for widget in frame.winfo_children():
                    widget.destroy()

    # ============================================================================
    # UI INTERACTIONS
    # ============================================================================
    
    def on_search_filter(self, event=None):
        """Filtre les marchés selon la recherche"""
        search_term = self.search_var.get().upper().strip()
        
        # Si la recherche est vide, réafficher tous les marchés
        if not search_term:
            self._show_all_markets()
            print(f"[SEARCH] Réinitialisation - Affichage de tous les marchés")
            return
        
        print(f"[SEARCH] Recherche: '{search_term}'")
        
        # Rechercher dans tous les résultats cachés
        found_markets = []
        for symbol, result in self.cached_results.items():
            if search_term in symbol.upper():
                found_markets.append((symbol, result))
        
        print(f"[SEARCH] {len(found_markets)} marchés trouvés pour '{search_term}'")
        
        # Afficher uniquement les marchés trouvés dans une catégorie spéciale
        self._show_search_results(found_markets, search_term)
    
    def _show_all_markets(self):
        """Réaffiche tous les marchés dans leurs catégories respectives"""
        # Réafficher tous les résultats cachés dans leurs catégories
        for symbol, result in self.cached_results.items():
            direction = result.get("direction")
            score = result.get("score")
            
            if direction == "HAUSSIER":
                self.add_market("Haussier", symbol, "BUY", score, result)
            elif direction == "BAISSIER":
                self.add_market("Baissier", symbol, "SELL", score, result)
            else:
                self.add_market("Neutre", symbol, "NEUTRE", score, result)
            
            # Statuts
            status = result.get("statut", "INTERDIT")
            if status == Status.AUTORISE :
                self.add_market("Autorisé", symbol, None, score, result)
                # Notification sonore quand un marché est autorisé
                if self._should_notify_authorization(symbol, status):
                    if self._should_play_sound(symbol, "authorization"):
                        self.play_notification_sound("authorization")
                        print(f"[SOUND] Notification sonore: {symbol} passé à AUTORISÉ")
            elif status == "SURVEILLANCE":
                self.add_market("Surveillance", symbol, None, score, result)
            elif status == "OPPORTUNITÉ":
                self.add_market("Autorisé", symbol, None, score, result)  # Les opportunités sont affichées comme autorisées
                # Notification sonore pour opportunité (statut spécial) - traité comme autorisé
                if self._should_notify_authorization(symbol, status):
                    if self._should_play_sound(symbol, "authorization"):
                        self.play_notification_sound("authorization")
                        print(f"[SOUND] Notification sonore: {symbol} statut OPPORTUNITÉ")
            else:
                self.add_market("Interdit", symbol, None, score, result)
    
    def _show_search_results(self, found_markets, search_term):
        """Affiche les résultats de recherche dans une catégorie spéciale"""
        # Effacer toutes les catégories
        self.clear_markets()
        
        # Afficher les résultats dans une catégorie "Recherche"
        if found_markets:
            for symbol, result in found_markets:
                direction = result.get("direction")
                score = result.get("score")
                
                # Afficher dans la catégorie "Recherche"
                self.add_market("Haussier" if direction == "HAUSSIER" else "Baissier" if direction == "BAISSIER" else "Neutre", 
                               symbol, direction, score, result)
        else:
            # Afficher un message "Aucun résultat"
            print(f"[SEARCH] Aucun marché trouvé pour '{search_term}'")

    def on_analyze(self):
        """Lance l'analyse du marché"""
        if self.is_analyzing:
            return
        self.is_analyzing = True
        self.start_analysis()

    def start_analysis(self):
        """Démarre l'analyse"""
        self.show_loading(True)
        self.after(100, self.refresh_ui_async)

    def show_loading(self, state: bool):
        """Affiche/cache le message de chargement"""
        if state:
            self.loading_label.config(text="Analyse du marché en cours...")
        else:
            self.loading_label.config(text="")

    def show_notification(self, message: str, color: str = "#22C55E", duration: int = 5000):
        """Affiche une notification"""
        self.notification_label.config(text=message, fg=color)
        self.after(duration, lambda: self.notification_label.config(text=""))

    def show_symbol_selector(self):
        """Affiche le sélecteur de marchés"""
        self.symbol_selector.show_selector()

    def show_image_analyzer(self):
        """Affiche l'analyseur d'images"""
        self.image_analyzer.show_analyzer()
    
    def show_trade_journal(self):
        """Affiche le journal de trade"""
        TradeJournalWindow(self)

    def open_trade_plan(self, symbol=None, timeframe="M10"):
        """Ouvre la fenêtre du Trade Plan avec les 3 timeframes (threadé pour éviter le freeze)"""
        if not hasattr(self, "cached_results") or symbol not in self.cached_results:
            return

        analysis = self.cached_results[symbol]

        # Rebuild minimal data si nécessaire
        if "df" not in analysis or analysis["df"] is None:
            markets = self.data_provider.get_all_markets()
            if symbol in markets:
                analysis["df"] = markets[symbol]

        # Afficher une fenêtre de chargement
        loading_window = tk.Toplevel(self)
        loading_window.title("Chargement...")
        loading_window.geometry("300x100")
        loading_window.configure(bg="#1E1E2F")
        loading_window.resizable(False, False)
        
        tk.Label(
            loading_window,
            text="Génération des Trade Plans...",
            font=("Segoe UI", 12),
            bg="#1E1E2F",
            fg="#FFFFFF"
        ).pack(expand=True)

        def generate_plans():
            """Génère les trade plans dans un thread séparé"""
            trade_plans = {}
            timeframes = ["M5", "M10", "M15"]

            for tf in timeframes:
                try:
                    import MetaTrader5 as mt5
                    if tf == "M5":
                        df = self.data_provider.get_candles(symbol, timeframe=mt5.TIMEFRAME_M5, count=500)
                    elif tf == "M10":
                        df = self.data_provider.get_candles(symbol, timeframe=mt5.TIMEFRAME_M10, count=500)
                    else:  # M15
                        df = self.data_provider.get_candles(symbol, timeframe=mt5.TIMEFRAME_M15, count=500)
                    
                    if df is not None and len(df) >= 50:
                        tf_analysis = analysis.copy()
                        tf_analysis["df"] = df
                        tf_analysis["symbol"] = symbol
                        tf_analysis.setdefault("zone", {"low": None, "high": None})
                        tf_analysis.setdefault("trend_continuation", False)
                        tf_analysis.setdefault("pullback_active", False)
                        tf_analysis.setdefault("has_impulse", False)
                        # ✅ Transmettre le timestamp de détection de direction
                        tf_analysis.setdefault("direction_detected_at", analysis.get("direction_detected_at"))
                        
                        tf_plan = generate_trade_plan_multi(tf_analysis, min_score=self.min_score)
                        if tf_plan and tf_plan.get("entry") is not None:
                            tf_plan["timeframe"] = tf
                            # ✅ Ajouter le timestamp de détection de direction au trade plan
                            tf_plan["direction_detected_at"] = analysis.get("direction_detected_at")
                            trade_plans[tf] = tf_plan
                except Exception as e:
                    print(f"[ERROR] Trade plan {tf} pour {symbol}: {e}")

            # Mettre à jour l'UI depuis le thread principal
            self.after(0, lambda: self._show_trade_plan_window(trade_plans, symbol, loading_window))

        # Lancer dans un thread séparé
        import threading
        thread = threading.Thread(target=generate_plans, daemon=True)
        thread.start()

    def _show_trade_plan_window(self, trade_plans, symbol, loading_window):
        """Affiche la fenêtre Trade Plan et ferme la fenêtre de chargement"""
        try:
            loading_window.destroy()
        except:
            pass

        if trade_plans:
            TradePlanWindow(self, trade_plans=trade_plans, symbol=symbol)
        else:
            tk.messagebox.showinfo("Trade Plan", f"Aucun trade valide pour {symbol}")

    def play_alert(self):
        """Joue une alerte sonore"""
        if SOUND_AVAILABLE:
            winsound.Beep(1200, 500)

    # ============================================================================
    # ANALYSIS & REFRESH
    # ============================================================================
    
    def get_mode_config(self, session):
        """Retourne la config selon le mode et la session"""
        base = {
            "ASIE": 70,
            "LONDRES": 60,
            "OVERLAP": 55,
            "NEW YORK": 60,
            "OFF": 75
        }

        if self.MODE == "RELAX":
            return {
                "min_score": base.get(session, 70) - 10,
                "confirmations": 1,
                "require_quality": False
            }
        elif self.MODE == "STRICT":
            return {
                "min_score": base.get(session, 70) + 5,
                "confirmations": 3,
                "require_quality": True
            }
        
        return {
            "min_score": base.get(session, 70),
            "confirmations": 2,
            "require_quality": False
        }

    def start_live_loop(self):
        """Boucle de rafraîchissement principal (threadé pour éviter le freeze)"""
        # Rafraîchissement adaptatif
        if hasattr(self, "urgent_mode") and self.urgent_mode:
            refresh_time = 15_000  # 15s en mode urgent
        else:
            refresh_time = 30_000  # 30s en mode normal
        
        self.after(refresh_time, self.start_live_loop)
        
        # Empêcher le lancement multiple d'analyses
        if hasattr(self, 'is_analyzing') and self.is_analyzing:
            return
        
        self.is_analyzing = True
        
        # Lancer l'analyse dans un thread séparé (non-daemon pour garantir la fin)
        import threading
        thread = threading.Thread(target=self.refresh_ui, daemon=False)
        thread.start()

    def refresh_ui(self):
        """Rafraîchit l'interface complète (exécuté dans un thread séparé)"""
        
        # SESSION
        session = get_active_session(datetime.utcnow().hour)
        
        if session != self.last_session:
            if session != "OFF":
                send_session_open(session)
            elif self.last_session:
                send_session_close(self.last_session)
            
            self.last_session = session
            self.sent_signals = set()
        
        # CONFIG
        config = self.get_mode_config(session)
        self.min_score = config["min_score"]
        
        # DAILY SUMMARY
        now = datetime.utcnow()
        if now.hour == 22 and now.day != self.last_summary_day:
            try:
                stats = self.stats_engine.compute()
                send_daily_summary(stats)
                self.last_summary_day = now.day
            except:
                pass
        
        # NEWS SHARING - DÉSACTIVÉ (MT5 ne fournit pas de news)
        # try:
        #     # Envoyer les news économiques importantes
        #     news_service = get_news_sharing_service()
        #     news_sent = news_service.send_news_summary(symbol="EURUSD", hours_back=24)
        #     
        #     if news_sent:
        #         print("✅ News économiques partagées avec succès")
        #     else:
        #         print("ℹ️ Aucune news économique récente à partager")
        # except Exception as e:
        #     print(f"⚠️ Erreur partage news: {e}")
        print("ℹ️ News Telegram désactivées - MT5 ne fournit pas de news")
        
        # APPRENTISSAGE AUTONOME DES MOMENTS DE NEWS
        try:
            from app.utils.news_learning import get_news_learning_system, print_learning_summary
            from app.utils.news_calendar import get_news_calendar
            
            learning_system = get_news_learning_system()
            
            # Apprendre des données de marché actuelles
            print("🧠 Apprentissage autonome des patterns de news...")
            
            # Analyser quelques marchés pour l'apprentissage
            symbols_to_learn = ["EURUSD", "GBPUSD", "USDJPY"]
            
            for symbol in symbols_to_learn:
                try:
                    # Récupérer les données récentes pour l'apprentissage
                    df = self.data_provider.get_data(symbol, timeframe="M5", limit=100)
                    if df is not None and len(df) > 50:
                        detected_events = learning_system.analyze_market_for_news(symbol, df, "M5")
                        if detected_events:
                            print(f"✅ {len(detected_events)} événements détectés pour {symbol}")
                except Exception as e:
                    print(f"⚠️ Erreur apprentissage {symbol}: {e}")
            
            # Afficher le résumé de l'apprentissage
            print_learning_summary()
            
        except Exception as e:
            print(f"⚠️ Erreur système d'apprentissage: {e}")
        
        # NE PAS VIDER L'UI AVANT L'ANALYSE - garder les anciens résultats visibles
        # self.after(0, lambda: self.clear_markets())
        self._status_results = {"INTERDIT": [], "SURVEILLANCE": [], "AUTORISÉ": [], "OPPORTUNITÉ": []}
        
        # GET MARKETS
        if not self.data_provider:
            return
        
        try:
            markets = self.data_provider.get_all_markets()
            print(f"📊 [MARKETS] {len(markets)} marchés récupérés: {list(markets.keys())}")
            
            # Vérifier si BTCUSD est dans les marchés
            if "BTCUSD" in markets:
                print("✅ [BTC] BTCUSD trouvé dans les marchés")
            else:
                print("❌ [BTC] BTCUSD NON trouvé dans les marchés")
                print(f"📋 [BTC] Marchés disponibles: {list(markets.keys())}")
                
        except Exception as e:
            print(f"❌ Erreur récupération marchés: {e}")
            return
        
        if not markets:
            return
        
        # ANALYSE CHAQUE MARCHÉ
        market_results = []
        
        try:
            session_info, session_ok = get_session_info_dynamic(symbol, df)
        except:
            session_info = session
            session_ok = session != "OFF"
        
        for symbol in markets:
            df = markets[symbol]
            
            # Logging spécifique pour BTCUSD
            if "BTC" in symbol.upper():
                print(f"🔍 [BTC DEBUG] Analyse de {symbol} - DataFrame: {len(df) if df is not None else 'None'} lignes")
            
            try:
                # Analyse complète du marché avec détection dynamique
                from app.engine.session_filter import get_comprehensive_market_analysis
                market_analysis = get_comprehensive_market_analysis(df, symbol)
                
                result = self.analyzer.analyze(df, symbol=symbol)
                result["df"] = df
                result["symbol"] = symbol
                result["session_ok"] = market_analysis['session_active']
                result["news_block"] = market_analysis['news_blocking']
                result["market_status"] = market_analysis['market_status']
                result["market_activity"] = market_analysis['market_activity']
                result["session_info"] = market_analysis['session_info']
                result["recommendations"] = market_analysis['recommendations']
                
                # Logging détaillé pour BTCUSD
                if "BTC" in symbol.upper():
                    print(f"📊 [BTC DEBUG] {symbol} - Status: {market_analysis['market_status']}, Session: {market_analysis['session_active']}, Score: {result.get('score', 'N/A')}")
                
                # Priorité pour marchés sélectionnés
                base_priority = compute_priority(result, self.last_stats)
                if symbol in self.selected_symbols:
                    result["priority"] = base_priority + 1000
                    result["user_selected"] = True
                else:
                    result["priority"] = base_priority
                    result["user_selected"] = False
                
                # Trade Plan
                trade_plan = generate_trade_plan_multi(result, min_score=self.min_score)
                
                # Vérifier la probabilité de news avec l'apprentissage automatique
                news_probability_ok = True
                try:
                    from app.utils.news_learning import is_high_news_probability
                    
                    # Vérifier si probabilité élevée de news
                    if is_high_news_probability(symbol, threshold=0.3):
                        news_probability_ok = False
                        print(f"⚠️ [APPRENTISSAGE] Probabilité élevée de news détectée pour {symbol}")
                        result["news_probability"] = "HIGH"
                        result["news_confidence"] = "LEARNING_SYSTEM"
                    else:
                        result["news_probability"] = "LOW"
                        result["news_confidence"] = "LEARNING_SYSTEM"
                except Exception as e:
                    print(f"⚠️ Erreur vérification probabilité news: {e}")
                
                result["trade_plan_available"] = (
                    trade_plan is not None and session_ok and news_probability_ok
                )
                
                # Cache
                self.cached_results[symbol] = result
                market_results.append((symbol, result))
                
                # API Signal - Multi-timeframe
                if self.api_enabled and API_AVAILABLE:
                    try:
                        import MetaTrader5 as mt5
                        
                        # Retirer le suffixe 'c' pour l'affichage
                        display_symbol = symbol.rstrip('c') if symbol.endswith('c') else symbol
                        
                        # Utiliser les résultats de Tkinter (cached_results) pour les messages Telegram
                        # au lieu de faire une nouvelle analyse
                        if hasattr(self, 'cached_results') and symbol in self.cached_results:
                            cached_result = self.cached_results[symbol]
                            
                            # Envoyer les signaux basés sur les résultats Tkinter pour tous les timeframes
                            try:
                                df_h4 = cached_result.get("df")
                                if df_h4 is not None and len(df_h4) >= 50:
                                    # Vérifier le statut avant d'envoyer
                                    statut = cached_result.get("statut", "INTERDIT")
                                    print(f"[DEBUG TELEGRAM] {display_symbol} - Statut Tkinter: {statut}")
                                    if statut == "AUTORISÉ":
                                        # Envoyer pour tous les timeframes (M5, M10, M15)
                                        for timeframe in ["M5", "M10", "M15"]:
                                            broadcast_signal(symbol, cached_result, df_h4, timeframe=timeframe)
                                    else:
                                        print(f"[DEBUG TELEGRAM] {display_symbol} - Non envoyé (statut: {statut})")
                            except Exception as e:
                                print(f"[ERROR TELEGRAM] {display_symbol}: {e}")
                        else:
                            print(f"[WARNING] {display_symbol} non trouvé dans cached_results")
                            
                    except Exception as e:
                        print(f"[ERROR API Signal] {display_symbol}: {e}")
                
            except Exception as e:
                display_symbol = symbol.rstrip('c') if symbol.endswith('c') else symbol
                print(f"[ERROR] {display_symbol}: {e}")
                continue
        
        # TRI par priorité
        market_results.sort(
            key=lambda x: (
                x[1].get("user_selected", False),
                x[1].get("trade_plan_available", False),
                x[1].get("priority", 0),
                x[1].get("score", 0)
            ),
            reverse=True
        )
        
        # UPDATE UI (via thread principal)
        def update_ui_thread_safe():
            try:
                # D'abord vider l'UI
                self.clear_markets()
                
                # Ensuite ajouter les nouveaux résultats
                for symbol, result in market_results:
                    direction = result.get("direction", "NEUTRE")
                    score = result.get("score", 0)
                    
                    # Update tendances
                    if direction == "HAUSSIER":
                        self.add_market("Haussier", symbol, "BUY", score, result)
                    elif direction == "BAISSIER":
                        self.add_market("Baissier", symbol, "SELL", score, result)
                    else:
                        self.add_market("Neutre", symbol, "NEUTRE", score, result)
                    
                    # Update statuts
                    status = result.get("statut", "INTERDIT")
                    if status in self._status_results:
                        self._status_results[status].append(symbol)
                        
                        # Ajouter directement au frame de statuts
                        if status in self.status_cards and self.status_cards[status]:
                            # Retirer le suffixe 'c' pour l'affichage
                            display_symbol = symbol.rstrip('c') if symbol.endswith('c') else symbol
                            lbl = tk.Label(
                                self.status_cards[status],
                                text=f" {display_symbol} | {direction} | {score}",
                                fg={"AUTORISÉ": "#22C55E", "SURVEILLANCE": "#FACC15", "INTERDIT": "#EF4444", "OPPORTUNITÉ": "#22C55E"}.get(status, "#6B7280"),
                                bg="#111827",
                                font=("Segoe UI", 10)
                            )
                            lbl.pack(anchor="w", padx=5, pady=2)
                            
                            # Notification sonore quand un marché passe à AUTORISÉ
                            if status == "AUTORISÉ" and self._should_notify_authorization(symbol, status):
                                if self._should_play_sound(symbol, "authorization"):
                                    self.play_notification_sound("authorization")
                                    print(f"[SOUND] Notification sonore: {display_symbol} passé à AUTORISÉ")
            except Exception as e:
                print(f"❌ Erreur mise à jour UI: {e}")
        
        # Utiliser try/catch pour éviter l'erreur de thread
        try:
            self.after(0, update_ui_thread_safe)
        except RuntimeError as e:
            print(f"⚠️ Erreur thread UI: {e}")
            # Essayer de mettre à jour directement si possible
            try:
                update_ui_thread_safe()
            except:
                print("❌ Impossible de mettre à jour l'interface")

        # BEST TRADE
        best = next((x for x in market_results if x[1]["trade_plan_available"]), None)
        if best:
            symbol, r = best
            # Retirer le suffixe 'c' pour l'affichage
            display_symbol = symbol.rstrip('c') if symbol.endswith('c') else symbol
            try:
                self.best_trade_label.config(
                    text=f"🏆 BEST TRADE: {display_symbol} | {r['direction']} | Score {r['score']}"
                )
            except RuntimeError:
                print("⚠️ Erreur mise à jour best trade label")
        else:
            try:
                self.best_trade_label.config(text="Aucune opportunité forte")
            except RuntimeError:
                print("⚠️ Erreur mise à jour best trade label")
        
        # UPDATE STATS
        try:
            stats = self.stats_engine.compute()
            self.last_stats = stats
            self.stats_panel.update(stats)
        except RuntimeError:
            print("⚠️ Erreur mise à jour stats panel")
        except Exception as e:
            print(f"❌ Erreur stats: {e}")
        
        # Réinitialiser le flag d'analyse
        self.is_analyzing = False

    def refresh_ui_async(self):
        """Rafraîchissement asynchrone"""
        try:
            self.refresh_ui()
        finally:
            self.is_analyzing = False
            self.show_loading(False)