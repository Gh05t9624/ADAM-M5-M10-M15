import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class UserMarketsManager:
    """Interface pour gérer les marchés de l'utilisateur Oumar Thioubou"""
    
    def __init__(self, parent, main_ui):
        self.parent = parent
        self.main_ui = main_ui
        self.window = None
        self.config_file = "app/config/users_config.json"
        self.user_id = "Oumar_Thioubou"
        
        # Liste des marchés disponibles (cohérent avec MT5)
        self.available_symbols = [
            "BTCUSD", "XAUUSD", "EURUSD", "GBPUSD", "USDJPY",
            "AUDUSD", "USDCAD", "NZDUSD", "EURJPY", "GBPJPY",
            "EURGBP", "EURCHF", "USDCHF", "XAGUSD", "US30",
            "UK100", "US500", "US2000", "ETHUSD", "EURCAD",
            "GBPAUD", "GBPCAD", "EURAUD", "EURNZD", "AUDJPY",
            "CADJPY", "CHFJPY", "AUDNZD", "NZDJPY", "GBPNZD",
            "AUDCHF", "NZDCAD", "USDAUD", "USDCAD", "USDCHF"
        ]
        
        self.current_selection = []
        self.load_user_symbols()
    
    def load_user_symbols(self):
        """Charge les symboles actuels de l'utilisateur depuis le fichier de configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                for user in config.get("users", []):
                    if user.get("id") == self.user_id:
                        self.current_selection = user.get("symbols", [])
                        break
        except Exception as e:
            print(f"Erreur chargement configuration: {e}")
            self.current_selection = []
    
    def save_user_symbols(self):
        """Sauvegarde les symboles de l'utilisateur dans le fichier de configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Mettre à jour les symboles de l'utilisateur
                for user in config.get("users", []):
                    if user.get("id") == self.user_id:
                        user["symbols"] = self.current_selection.copy()
                        break
                
                # Sauvegarder
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                return True
        except Exception as e:
            print(f"Erreur sauvegarde configuration: {e}")
            return False
    
    def show(self):
        """Affiche la fenêtre de gestion des marchés"""
        if self.window is not None:
            self.window.destroy()
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("Gestion des marchés - Oumar Thioubou")
        self.window.geometry("600x500")
        self.window.configure(bg="#1E1E2F")
        self.window.resizable(False, False)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#1E1E2F")
        style.configure("TLabel", background="#1E1E2F", foreground="white", font=("Arial", 10))
        style.configure("TButton", background="#4CAF50", foreground="white", font=("Arial", 10, "bold"))
        style.configure("Header.TLabel", background="#1E1E2F", foreground="#4CAF50", font=("Arial", 14, "bold"))
        
        # Header
        header_frame = ttk.Frame(self.window)
        header_frame.pack(fill="x", padx=20, pady=20)
        
        ttk.Label(header_frame, text="📊 Gestion des marchés", style="Header.TLabel").pack()
        ttk.Label(header_frame, text="Oumar Thioubou").pack()
        
        # Liste des marchés disponibles
        list_frame = ttk.Frame(self.window)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Listbox
        self.listbox = tk.Listbox(list_frame, selectmode="multiple", 
                                   bg="#2D2D44", fg="white", 
                                   selectbackground="#4CAF50",
                                   selectforeground="white",
                                   font=("Arial", 10),
                                   yscrollcommand=scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # Remplir la liste
        for symbol in self.available_symbols:
            self.listbox.insert(tk.END, symbol)
            if symbol in self.current_selection:
                self.listbox.selection_set(tk.END)
        
        # Boutons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        ttk.Button(button_frame, text="✓ Appliquer", command=self.apply_selection).pack(side="left", padx=5)
        ttk.Button(button_frame, text="✗ Annuler", command=self.close).pack(side="left", padx=5)
        
        # Info
        info_label = ttk.Label(self.window, text=f"Marchés sélectionnés: {len(self.current_selection)}")
        info_label.pack(pady=5)
    
    def apply_selection(self):
        """Applique la sélection et sauvegarde"""
        selected_indices = self.listbox.curselection()
        self.current_selection = [self.listbox.get(i) for i in selected_indices]
        
        if len(self.current_selection) == 0:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner au moins 1 marché")
            return
        
        # Sauvegarder
        if self.save_user_symbols():
            messagebox.showinfo("Succès", f"Configuration sauvegardée pour {len(self.current_selection)} marchés")
            self.close()
        else:
            messagebox.showerror("Erreur", "Erreur lors de la sauvegarde")
    
    def close(self):
        """Ferme la fenêtre"""
        if self.window:
            self.window.destroy()
            self.window = None
