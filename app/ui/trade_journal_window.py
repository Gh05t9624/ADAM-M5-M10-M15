# app/ui/trade_journal_window.py
# Fenêtre de journal de trade manuel pour l'apprentissage du bot

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timezone
import json
import os

class TradeJournalWindow:
    """Fenêtre de journal de trade manuel"""
    
    def __init__(self, parent, available_markets=None):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("📊 Journal de Trade - A.D.A.M")
        self.window.geometry("600x700")
        self.window.configure(bg="#0B0F14")
        
        # Liste des marchés disponibles
        self.available_markets = available_markets or self._get_available_markets()
        
        # Fichier de sauvegarde
        self.journal_file = "manual_trade_journal.json"
        self.journal_data = self._load_journal()
        
        # Créer l'interface
        self._create_widgets()
        self._load_journal_display()
    
    def _get_available_markets(self):
        """Récupère la liste des marchés disponibles depuis le data provider"""
        try:
            if hasattr(self.parent, 'data_provider') and self.parent.data_provider:
                markets = self.parent.data_provider.get_all_markets()
                return list(markets.keys())
        except Exception as e:
            print(f"⚠️ Erreur récupération marchés: {e}")
        
        # Liste par défaut
        return ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"]
    
    def _load_journal(self) -> list:
        """Charge le journal depuis le fichier"""
        if os.path.exists(self.journal_file):
            try:
                with open(self.journal_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Erreur chargement journal: {e}")
                return []
        return []
    
    def _save_journal(self):
        """Sauvegarde le journal dans le fichier"""
        try:
            with open(self.journal_file, 'w', encoding='utf-8') as f:
                json.dump(self.journal_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Erreur sauvegarde journal: {e}")
    
    def _create_widgets(self):
        """Crée les widgets de la fenêtre"""
        # Titre
        title = tk.Label(
            self.window,
            text="📊 JOURNAL DE TRADE MANUEL",
            font=("Segoe UI", 16, "bold"),
            fg="#FFFFFF",
            bg="#0B0F14"
        )
        title.pack(pady=10)
        
        # Frame de saisie
        input_frame = tk.Frame(self.window, bg="#111827", padx=20, pady=20)
        input_frame.pack(fill="x", padx=20, pady=10)
        
        # Marché
        tk.Label(
            input_frame,
            text="Marché:",
            fg="#FFFFFF",
            bg="#111827",
            font=("Segoe UI", 10)
        ).grid(row=0, column=0, sticky="w", pady=5)
        
        self.market_var = tk.StringVar()
        market_combo = ttk.Combobox(
            input_frame,
            textvariable=self.market_var,
            values=self.available_markets,
            state="readonly",
            width=27
        )
        market_combo.grid(row=0, column=1, pady=5, padx=5)
        if self.available_markets:
            market_combo.current(0)
        
        # Tendance
        tk.Label(
            input_frame,
            text="Tendance:",
            fg="#FFFFFF",
            bg="#111827",
            font=("Segoe UI", 10)
        ).grid(row=1, column=0, sticky="w", pady=5)
        
        self.trend_var = tk.StringVar()
        trend_combo = ttk.Combobox(
            input_frame,
            textvariable=self.trend_var,
            values=["HAUSSIER", "BAISSIER", "NEUTRE"],
            state="readonly",
            width=27
        )
        trend_combo.grid(row=1, column=1, pady=5, padx=5)
        trend_combo.current(0)
        
        # Stop Loss
        tk.Label(
            input_frame,
            text="Stop Loss (prix):",
            fg="#FFFFFF",
            bg="#111827",
            font=("Segoe UI", 10)
        ).grid(row=2, column=0, sticky="w", pady=5)
        
        self.sl_var = tk.StringVar()
        sl_entry = tk.Entry(
            input_frame,
            textvariable=self.sl_var,
            bg="#1F2937",
            fg="#FFFFFF",
            font=("Segoe UI", 10),
            width=30
        )
        sl_entry.grid(row=2, column=1, pady=5, padx=5)
        sl_entry.bind('<KeyRelease>', lambda e: self._validate_price(self.sl_var))
        
        # Take Profit
        tk.Label(
            input_frame,
            text="Take Profit (prix):",
            fg="#FFFFFF",
            bg="#111827",
            font=("Segoe UI", 10)
        ).grid(row=3, column=0, sticky="w", pady=5)
        
        self.tp_var = tk.StringVar()
        tp_entry = tk.Entry(
            input_frame,
            textvariable=self.tp_var,
            bg="#1F2937",
            fg="#FFFFFF",
            font=("Segoe UI", 10),
            width=30
        )
        tp_entry.grid(row=3, column=1, pady=5, padx=5)
        tp_entry.bind('<KeyRelease>', lambda e: self._validate_price(self.tp_var))
        
        # Prix d'entrée
        tk.Label(
            input_frame,
            text="Prix d'entrée:",
            fg="#FFFFFF",
            bg="#111827",
            font=("Segoe UI", 10)
        ).grid(row=4, column=0, sticky="w", pady=5)
        
        self.entry_price_var = tk.StringVar()
        entry_price_entry = tk.Entry(
            input_frame,
            textvariable=self.entry_price_var,
            bg="#1F2937",
            fg="#FFFFFF",
            font=("Segoe UI", 10),
            width=30
        )
        entry_price_entry.grid(row=4, column=1, pady=5, padx=5)
        
        # Date d'entrée
        tk.Label(
            input_frame,
            text="Date d'entrée:",
            fg="#FFFFFF",
            bg="#111827",
            font=("Segoe UI", 10)
        ).grid(row=5, column=0, sticky="w", pady=5)
        
        self.entry_date_var = tk.StringVar()
        entry_date_entry = tk.Entry(
            input_frame,
            textvariable=self.entry_date_var,
            bg="#1F2937",
            fg="#FFFFFF",
            font=("Segoe UI", 10),
            width=30
        )
        entry_date_entry.grid(row=5, column=1, pady=5, padx=5)
        entry_date_entry.insert(0, datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        
        # Heure d'entrée
        tk.Label(
            input_frame,
            text="Heure d'entrée:",
            fg="#FFFFFF",
            bg="#111827",
            font=("Segoe UI", 10)
        ).grid(row=6, column=0, sticky="w", pady=5)
        
        self.entry_time_var = tk.StringVar()
        entry_time_entry = tk.Entry(
            input_frame,
            textvariable=self.entry_time_var,
            bg="#1F2937",
            fg="#FFFFFF",
            font=("Segoe UI", 10),
            width=30
        )
        entry_time_entry.grid(row=6, column=1, pady=5, padx=5)
        entry_time_entry.insert(0, datetime.now(timezone.utc).strftime("%H:%M:%S"))
        
        # Date de sortie
        tk.Label(
            input_frame,
            text="Date de sortie:",
            fg="#FFFFFF",
            bg="#111827",
            font=("Segoe UI", 10)
        ).grid(row=7, column=0, sticky="w", pady=5)
        
        self.exit_date_var = tk.StringVar()
        exit_date_entry = tk.Entry(
            input_frame,
            textvariable=self.exit_date_var,
            bg="#1F2937",
            fg="#FFFFFF",
            font=("Segoe UI", 10),
            width=30
        )
        exit_date_entry.grid(row=7, column=1, pady=5, padx=5)
        
        # Heure de sortie
        tk.Label(
            input_frame,
            text="Heure de sortie:",
            fg="#FFFFFF",
            bg="#111827",
            font=("Segoe UI", 10)
        ).grid(row=8, column=0, sticky="w", pady=5)
        
        self.exit_time_var = tk.StringVar()
        exit_time_entry = tk.Entry(
            input_frame,
            textvariable=self.exit_time_var,
            bg="#1F2937",
            fg="#FFFFFF",
            font=("Segoe UI", 10),
            width=30
        )
        exit_time_entry.grid(row=8, column=1, pady=5, padx=5)
        
        # Profit/Perte
        tk.Label(
            input_frame,
            text="Résultat:",
            fg="#FFFFFF",
            bg="#111827",
            font=("Segoe UI", 10)
        ).grid(row=9, column=0, sticky="w", pady=5)
        
        self.pnl_var = tk.StringVar()
        pnl_combo = ttk.Combobox(
            input_frame,
            textvariable=self.pnl_var,
            values=["Profit", "Perte"],
            state="readonly",
            width=27
        )
        pnl_combo.grid(row=9, column=1, pady=5, padx=5)
        pnl_combo.current(0)
        
        # Boutons
        button_frame = tk.Frame(input_frame, bg="#111827")
        button_frame.grid(row=10, column=0, columnspan=2, pady=15)
        
        add_btn = tk.Button(
            button_frame,
            text="➕ Ajouter Trade",
            font=("Segoe UI", 10, "bold"),
            bg="#22C55E",
            fg="#FFFFFF",
            relief="flat",
            cursor="hand2",
            command=self._add_trade,
            width=15
        )
        add_btn.pack(side="left", padx=5)
        
        clear_btn = tk.Button(
            button_frame,
            text="🗑️ Effacer",
            font=("Segoe UI", 10),
            bg="#EF4444",
            fg="#FFFFFF",
            relief="flat",
            cursor="hand2",
            command=self._clear_form,
            width=10
        )
        clear_btn.pack(side="left", padx=5)
        
        # Frame d'affichage du journal
        display_frame = tk.Frame(self.window, bg="#111827", padx=20, pady=20)
        display_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        tk.Label(
            display_frame,
            text="📋 HISTORIQUE DES TRADES",
            font=("Segoe UI", 12, "bold"),
            fg="#FFFFFF",
            bg="#111827"
        ).pack(pady=5)
        
        # Treeview pour l'affichage
        columns = ("Marché", "Tendance", "SL", "TP", "Entrée", "Sortie", "P/L")
        self.tree = ttk.Treeview(display_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor="center")
        
        self.tree.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(display_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
    
    def _add_trade(self):
        """Ajoute un trade au journal"""
        try:
            # Validation des champs
            if not self.market_var.get():
                messagebox.showerror("Erreur", "Veuillez sélectionner un marché")
                return
            
            if not self.sl_var.get():
                messagebox.showerror("Erreur", "Veuillez entrer un Stop Loss")
                return
            
            if not self.tp_var.get():
                messagebox.showerror("Erreur", "Veuillez entrer un Take Profit")
                return
            
            # Convertir SL et TP
            sl_value = float(self.sl_var.get()) if self.sl_var.get() else 0
            tp_value = float(self.tp_var.get()) if self.tp_var.get() else 0
            
            # Déterminer si c'est un profit ou une perte
            is_profit = self.pnl_var.get() == "Profit"
            
            # Combiner date et heure d'entrée
            entry_datetime = f"{self.entry_date_var.get()} {self.entry_time_var.get()}" if self.entry_date_var.get() and self.entry_time_var.get() else datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            
            # Combiner date et heure de sortie
            exit_datetime = f"{self.exit_date_var.get()} {self.exit_time_var.get()}" if self.exit_date_var.get() and self.exit_time_var.get() else None
            
            # Créer l'entrée de trade
            trade = {
                "market": self.market_var.get().upper(),
                "trend": self.trend_var.get(),
                "stop_loss": sl_value,
                "take_profit": tp_value,
                "entry_price": float(self.entry_price_var.get()) if self.entry_price_var.get() else None,
                "entry_date": self.entry_date_var.get(),
                "entry_time": self.entry_time_var.get(),
                "entry_datetime": entry_datetime,
                "exit_date": self.exit_date_var.get(),
                "exit_time": self.exit_time_var.get(),
                "exit_datetime": exit_datetime,
                "is_profit": is_profit,
                "profit_loss": abs(sl_value) if not is_profit else tp_value,  # Valeur pour l'apprentissage
                "added_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Ajouter au journal
            self.journal_data.append(trade)
            self._save_journal()
            
            # Rafraîchir l'affichage
            self._load_journal_display()
            
            # Effacer le formulaire
            self._clear_form()
            
            messagebox.showinfo("Succès", "Trade ajouté au journal!")
            
            # Informer le système d'apprentissage
            self._notify_learning_system(trade)
            
        except ValueError as e:
            messagebox.showerror("Erreur", f"Valeur invalide: {e}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {e}")
    
    def _clear_form(self):
        """Efface le formulaire"""
        self.market_var.set("")
        self.trend_var.set("HAUSSIER")
        self.sl_var.set("")
        self.tp_var.set("")
        self.entry_price_var.set("")
        self.entry_date_var.set(datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        self.entry_time_var.set(datetime.now(timezone.utc).strftime("%H:%M:%S"))
        self.exit_date_var.set("")
        self.exit_time_var.set("")
        self.pnl_var.set("Profit")
    
    def _validate_price(self, var):
        """Valide que seul chiffres, point décimal et signes + et - sont autorisés"""
        current_text = var.get()
        # Garder seulement les chiffres, le point décimal et les signes + et -
        filtered_text = ''.join(c for c in current_text if c.isdigit() or c in '+-.')
        # S'assurer qu'il n'y a qu'un seul point décimal
        if filtered_text.count('.') > 1:
            # Garder seulement le premier point
            parts = filtered_text.split('.')
            filtered_text = parts[0] + '.' + ''.join(parts[1:])
        var.set(filtered_text)
    
    def _load_journal_display(self):
        """Charge et affiche le journal"""
        # Effacer l'arbre
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Afficher les trades (plus récents en premier)
        for trade in reversed(self.journal_data):
            pnl_text = "Profit" if trade.get('is_profit') else "Perte"
            
            # Afficher la date et heure d'entrée combinées
            entry_display = trade.get('entry_datetime', trade.get('entry_time', 'N/A'))
            exit_display = trade.get('exit_datetime') or "En cours"
            
            self.tree.insert("", "end", values=(
                trade['market'],
                trade['trend'],
                trade['stop_loss'],
                trade['take_profit'],
                entry_display,
                exit_display,
                pnl_text
            ))
    
    def _notify_learning_system(self, trade: dict):
        """Informe le système d'apprentissage du nouveau trade"""
        try:
            from app.utils.trade_learning import TradeLearningSystem
            
            learning_system = TradeLearningSystem()
            learning_system.learn_from_trade(trade)
            
            print(f"🧠 Système d'apprentissage informé du trade: {trade['market']}")
        except Exception as e:
            print(f"⚠️ Erreur notification système d'apprentissage: {e}")

def open_trade_journal_window(parent):
    """Ouvre la fenêtre de journal de trade"""
    TradeJournalWindow(parent)
