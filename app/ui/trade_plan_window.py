# app/ui/trade_plan_window.py

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading


class TradePlanWindow(tk.Toplevel):

    def __init__(self, parent, trade_plans=None, symbol=None):
        super().__init__(parent)

        self.title("Trade Plan")
        self.geometry("500x580")
        self.configure(bg="#1E1E2F")
        self.resizable(False, False)
        self.trade_plans = trade_plans or {}
        self.symbol = symbol
        self.current_timeframe = None
        self.signal_time = datetime.utcnow()  # Heure de génération du signal (fallback)
        self.trade_plan_time = None  # Heure de création du trade plan (depuis created_at)
        self.clock_running = True
        self.protocol("WM_DELETE_WINDOW", self.safe_close)

        try:
            self.create_widgets()
            self.create_tabs()
            self.populate_trade_plan()
            self.start_clock()  # Démarrer l'horloge
        except Exception as e:
            print(f"Erreur TradePlanWindow: {e}")
            self.safe_close()

    def safe_close(self):
        try:
            self.destroy()
        except:
            pass

    def create_widgets(self):

        # ===== HEADER =====
        tk.Label(
            self,
            text="ADAM - SIGNAL",
            font=("Segoe UI", 14, "bold"),
            bg="#1E1E2F",
            fg="#FFFFFF"
        ).pack(pady=10)

        tk.Frame(self, height=2, bg="#4A5568").pack(fill="x", padx=20, pady=2)

        # ===== TABS FRAME =====
        self.tabs_frame = tk.Frame(self, bg="#1E1E2F")
        self.tabs_frame.pack(fill="x", padx=20, pady=5)

        self.frame_content = tk.Frame(self, bg="#1E1E2F")
        self.frame_content.pack(fill="both", expand=True, padx=20, pady=10)

        # ===== SYMBOLE + TYPE =====
        self.header_frame = tk.Frame(self.frame_content, bg="#1E1E2F")
        self.header_frame.pack(fill="x", pady=8)

        self.symbol_label = tk.Label(
            self.header_frame,
            text="",
            font=("Segoe UI", 12, "bold"),
            bg="#1E1E2F",
            fg="#38BDF8"
        )
        self.symbol_label.pack(anchor="w")

        self.timeframe_label = tk.Label(
            self.header_frame,
            text="",
            font=("Segoe UI", 10, "bold"),
            bg="#1E1E2F",
            fg="#FACC15"
        )
        self.timeframe_label.pack(anchor="w", pady=2)

        self.direction_label = tk.Label(
            self.header_frame,
            text="",
            font=("Segoe UI", 11, "bold"),
            bg="#1E1E2F",
            fg="#FFFFFF"
        )
        self.direction_label.pack(anchor="w", pady=2)

        self.time_label = tk.Label(
            self.header_frame,
            text="",
            font=("Segoe UI", 10),
            bg="#1E1E2F",
            fg="#9CA3AF"
        )
        self.time_label.pack(anchor="w")

        tk.Frame(self.frame_content, height=1, bg="#4A5568").pack(fill="x", pady=8)

        # ===== SL / TP =====
        self.labels = {}

        trade_fields = [
            ("SL    :", "sl"),
            ("TP    :", "tp"),
        ]

        for label_text, key in trade_fields:
            frame = tk.Frame(self.frame_content, bg="#1E1E2F")
            frame.pack(fill="x", pady=3)

            tk.Label(
                frame,
                text=label_text,
                font=("Segoe UI", 11, "bold"),
                bg="#1E1E2F",
                fg="#E5E7EB",
                width=8,
                anchor="w"
            ).pack(side="left")

            value_label = tk.Label(
                frame,
                text="",
                font=("Segoe UI", 11),
                bg="#1E1E2F",
                fg="#FFFFFF",
                anchor="w"
            )
            value_label.pack(side="left", padx=(5, 0))
            self.labels[key] = value_label

        tk.Frame(self.frame_content, height=1, bg="#4A5568").pack(fill="x", pady=8)

        # ===== RR + SCORE =====
        stats_frame = tk.Frame(self.frame_content, bg="#1E1E2F")
        stats_frame.pack(fill="x", pady=5)

        self.rr_label = tk.Label(
            stats_frame,
            text="",
            font=("Segoe UI", 11),
            bg="#1E1E2F",
            fg="#E5E7EB"
        )
        self.rr_label.pack(anchor="w")

        self.score_label = tk.Label(
            stats_frame,
            text="",
            font=("Segoe UI", 11),
            bg="#1E1E2F",
            fg="#FACC15"
        )
        self.score_label.pack(anchor="w", pady=2)

        tk.Frame(self.frame_content, height=1, bg="#4A5568").pack(fill="x", pady=8)

        # ===== FOOTER =====
        footer_frame = tk.Frame(self.frame_content, bg="#1E1E2F")
        footer_frame.pack(fill="x", pady=5)

        tk.Label(
            footer_frame,
            text="TP dynamique adapte au marche",
            font=("Segoe UI", 9, "italic"),
            bg="#1E1E2F",
            fg="#6B7280"
        ).pack(anchor="w")

        tk.Label(
            footer_frame,
            text="Pas un conseil financier",
            font=("Segoe UI", 9, "italic"),
            bg="#1E1E2F",
            fg="#6B7280"
        ).pack(anchor="w", pady=2)

        ttk.Button(
            self,
            text="Fermer",
            command=self.destroy
        ).pack(pady=15)

    def create_tabs(self):
        """Crée les onglets pour les timeframes disponibles"""
        self.tab_buttons = {}
        timeframe_order = ["M5", "M10", "M15"]
        
        for tf in timeframe_order:
            if tf in self.trade_plans:
                btn = tk.Button(
                    self.tabs_frame,
                    text=tf,
                    font=("Segoe UI", 10, "bold"),
                    bg="#374151",
                    fg="#FFFFFF",
                    relief="flat",
                    cursor="hand2",
                    width=8
                )
                btn.pack(side="left", padx=2)
                btn.config(command=lambda t=tf, b=btn: self.switch_tab(t, b))
                self.tab_buttons[tf] = btn
        
        # Sélectionner le premier timeframe disponible
        if self.trade_plans:
            first_tf = list(self.trade_plans.keys())[0]
            self.switch_tab(first_tf, self.tab_buttons[first_tf])

    def switch_tab(self, timeframe, button):
        """Change l'onglet actif"""
        self.current_timeframe = timeframe
        
        # Réinitialiser les couleurs de tous les boutons
        for tf, btn in self.tab_buttons.items():
            btn.config(bg="#374151", fg="#FFFFFF")
        
        # Mettre en surbrillance le bouton actif
        button.config(bg="#FACC15", fg="#000000")
        
        # Mettre à jour l'affichage
        self.populate_trade_plan()

    def populate_trade_plan(self):
        # Récupérer le trade plan du timeframe actuel
        if not self.current_timeframe or self.current_timeframe not in self.trade_plans:
            self.symbol_label.config(text="Aucun trade disponible")
            self.timeframe_label.config(text="")
            self.direction_label.config(text="")
            self.time_label.config(text="")
            for lbl in self.labels.values():
                lbl.config(text="")
            self.rr_label.config(text="")
            self.score_label.config(text="")
            return

        trade_plan = self.trade_plans[self.current_timeframe]

        # ✅ Récupération symbol depuis trade_plan
        symbol     = trade_plan.get("symbol", self.symbol or "INCONNU")
        trade_type = trade_plan.get("type",   "N/A")
        direction  = trade_plan.get("direction", "N/A")
        timeframe  = trade_plan.get("timeframe", self.current_timeframe)
        
        # ✅ Récupérer le timestamp de création du trade plan
        created_at = trade_plan.get("created_at")
        if created_at:
            self.trade_plan_time = created_at
            self.signal_time = created_at  # Utiliser created_at comme temps de référence
        
        # ✅ Récupérer le timestamp de détection de direction depuis l'analyse
        direction_detected_at = trade_plan.get("direction_detected_at")
        if direction_detected_at:
            self.signal_time = direction_detected_at  # Priorité au timestamp de direction

        # Noms lisibles
        market_names = {
            "EURUSD" : "EUR/USD",
            "GBPUSD" : "GBP/USD",
            "USDJPY" : "USD/JPY",
            "USDCHF" : "USD/CHF",
            "USDCAD" : "USD/CAD",
            "AUDUSD" : "AUD/USD",
            "NZDUSD" : "NZD/USD",
            "EURJPY" : "EUR/JPY",
            "GBPJPY" : "GBP/JPY",
            "CHFJPY" : "CHF/JPY",
            "AUDJPY" : "AUD/JPY",
            "GBPAUD" : "GBP/AUD",
            "GBPNZD" : "GBP/NZD",
            "GBPCAD" : "GBP/CAD",
            "EURAUD" : "EUR/AUD",
            "EURNZD" : "EUR/NZD",
            "EURCAD" : "EUR/CAD",
            "EURGBP" : "EUR/GBP",
            "AUDCAD" : "AUD/CAD",
            "AUDNZD" : "AUD/NZD",
            "AUDCHF" : "AUD/CHF",
            "NZDCAD" : "NZD/CAD",
            "XAUUSD" : "GOLD/USD",
            "XAGUSD" : "SILVER/USD",
            "BTCUSD" : "BTC/USD",
            "ETHUSD" : "ETH/USD",
        }

        type_names = {
            "TREND"         : "Tendance",
            "PULLBACK"      : "Pullback",
            "MICRO_BREAKOUT": "Breakout",
            "FALLBACK"      : "Fallback"
        }

        timeframe_names = {
            "M5": "M5 (Équilibré)",
            "M10": "M10 (Fiable)",
            "M15": "M15 (Rapide)"
        }

        market_name       = market_names.get(symbol, symbol)
        trade_type_name   = type_names.get(trade_type, trade_type)
        timeframe_name    = timeframe_names.get(timeframe, timeframe)
        direction_arrow   = "+" if direction == "HAUSSIER" else "-"

        # ✅ Affichage symbole + type
        self.symbol_label.config(
            text=f"{market_name} | {trade_type_name}"
        )
        self.timeframe_label.config(
            text=f"Timeframe : {timeframe_name}"
        )
        self.direction_label.config(
            text=f"Direction : {direction_arrow} {direction}"
        )
        self.time_label.config(
            text=f"Tendance détectée : {self.signal_time.strftime('%H:%M UTC')} | Actuel : {datetime.utcnow().strftime('%H:%M UTC')} | Écoulé : 0s"
        )

        sl    = trade_plan.get("sl",    0)
        tp    = trade_plan.get("tp",    0)
        entry = trade_plan.get("entry", 0)  # Gardé pour le calcul des pips

        # ✅ Pip correct selon symbole avec conversion BTC/XAU
        if "JPY" in symbol:
            pip = 0.01
            sl_pips = round(abs(entry - sl) / pip) if entry and sl else 0
            tp_pips = round(abs(tp - entry) / pip) if entry and tp else 0
            sl_pips_text = f"(-{sl_pips} pips)"
            tp_pips_text = f"(+{tp_pips} pips)"
        elif "XAU" in symbol or "GOLD" in symbol:
            pip = 0.1
            # 🎯 Norme corrigée XAU : SL = 300 points (30$), TP = 600 points (60$)
            sl_points = abs(entry - sl) if entry and sl else 300  # Valeur par défaut
            tp_points = abs(tp - entry) if entry and tp else 600  # Valeur par défaut
            sl_pips = round(sl_points / pip)  # Pips réels
            tp_pips = round(tp_points / pip)  # Pips réels
            # Conversion en dollars pour clarté
            sl_usd = round(sl_points, 1)
            tp_usd = round(tp_points, 1)
            sl_pips_text = f"(-{sl_pips} pips/{sl_usd}$)"
            tp_pips_text = f"(+{tp_pips} pips/{tp_usd}$)"
        elif "BTC" in symbol:
            pip = 0.1
            # 🎯 Norme corrigée BTC : SL = 500 points (50$), TP = 1000 points (100$) - plus volatil
            sl_points = abs(entry - sl) if entry and sl else 500  # Valeur par défaut
            tp_points = abs(tp - entry) if entry and tp else 1000  # Valeur par défaut
            sl_pips = round(sl_points / pip)  # Pips réels
            tp_pips = round(tp_points / pip)  # Pips réels
            # Conversion en dollars pour clarté
            sl_usd = round(sl_points, 1)
            tp_usd = round(tp_points, 1)
            sl_pips_text = f"(-{sl_pips} pips/{sl_usd}$)"
            tp_pips_text = f"(+{tp_pips} pips/{tp_usd}$)"
        else:
            pip = 0.0001
            sl_pips = round(abs(entry - sl) / pip) if entry and sl else 0
            tp_pips = round(abs(tp - entry) / pip) if entry and tp else 0
            sl_pips_text = f"(-{sl_pips} pips)"
            tp_pips_text = f"(+{tp_pips} pips)"

        # Couleur SL rouge / TP vert
        self.labels["sl"].config(
            text=f"{sl}",
            fg="#EF4444"
        )
        self.labels["tp"].config(
            text=f"{tp}",
            fg="#22C55E"
        )

        # ✅ RR et Score avec texte (pas d'emoji)
        rr    = trade_plan.get("rr",    0)
        score = trade_plan.get("score", 0)

        self.rr_label.config(
            text=f"RR    :  1:{rr}"
        )
        self.score_label.config(
            text=f"Score :  {score}/100"
        )

    def start_clock(self):
        """Démarre l'horloge dynamique dans un thread séparé"""
        def update_clock():
            while self.clock_running:
                try:
                    # Calculer le temps écoulé
                    current_time = datetime.utcnow()
                    elapsed = current_time - self.signal_time
                    
                    # Formater le temps écoulé
                    if elapsed.total_seconds() < 60:
                        elapsed_str = f"{int(elapsed.total_seconds())}s"
                    elif elapsed.total_seconds() < 3600:
                        elapsed_str = f"{int(elapsed.total_seconds() // 60)}m {int(elapsed.total_seconds() % 60)}s"
                    else:
                        hours = int(elapsed.total_seconds() // 3600)
                        minutes = int((elapsed.total_seconds() % 3600) // 60)
                        elapsed_str = f"{hours}h {minutes}m"
                    
                    # Mettre à jour le label
                    time_text = f"Tendance détectée : {self.signal_time.strftime('%H:%M UTC')} | Actuel : {current_time.strftime('%H:%M UTC')} | Écoulé : {elapsed_str}"
                    
                    # Changer la couleur selon le temps écoulé
                    if elapsed.total_seconds() < 300:  # Moins de 5 minutes
                        color = "#22C55E"  # Vert - OK pour entrer
                    elif elapsed.total_seconds() < 900:  # Moins de 15 minutes
                        color = "#FACC15"  # Jaune - Attention
                    else:  # Plus de 15 minutes
                        color = "#EF4444"  # Rouge - Trop tard
                    
                    self.time_label.config(text=time_text, fg=color)
                    
                except Exception as e:
                    print(f"Erreur horloge: {e}")
                
                # Attendre 1 seconde avant la prochaine mise à jour
                threading.Event().wait(1)
        
        # Lancer dans un thread séparé pour ne pas bloquer l'interface
        clock_thread = threading.Thread(target=update_clock, daemon=True)
        clock_thread.start()

    def safe_close(self):
        """Arrête l'horloge et ferme la fenêtre"""
        self.clock_running = False
        try:
            self.destroy()
        except:
            pass