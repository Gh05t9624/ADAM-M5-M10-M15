"""
Sélecteur simple de marchés pour l'interface Tkinter d'ADAM
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional

class SymbolSelector:
    """Interface simple pour choisir 1-5 marchés"""
    
    def __init__(self, parent, main_ui):
        self.parent = parent
        self.main_ui = main_ui
        self.window = None
        self.selected_symbols = []
        self.max_selection = 5
        
        # Liste des marchés disponibles (cohérent avec users_config.json)
        self.available_symbols = [
            "BTCUSD", "XAUUSD", "EURUSD", "GBPUSD", "USDJPY",
            "AUDUSD", "USDCAD", "NZDUSD", "EURJPY", "GBPJPY",
            "EURGBP", "EURCHF", "USDCHF", "XAGUSD", "US30",
            "UK100", "US500", "US2000", "ETHUSD", "EURCAD"
        ]
        
        # Marchés actuellement sélectionnés (prioritaires selon config)
        self.current_selection = ["BTCUSD", "XAUUSD", "EURUSD"]
    
    def show_selector(self):
        """Afficher la fenêtre de sélection de marchés"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title("ADAM - Sélection des Marchés")
        self.window.geometry("600x500")
        self.window.configure(bg='#1e1e1e')
        self.window.resizable(False, False)
        
        # Rendre la fenêtre modale
        self.window.transient(self.parent)
        self.window.grab_set()
        
        self.create_widgets()
        
        # Centrer la fenêtre
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.window.winfo_screenheight() // 2) - (500 // 2)
        self.window.geometry(f"600x500+{x}+{y}")
    
    def create_widgets(self):
        """Créer les widgets de la fenêtre"""
        
        # Header
        header_frame = tk.Frame(self.window, bg='#2d2d2d', height=80)
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="Choisir 1 à 5 marchés à analyser", 
                font=('Arial', 16, 'bold'), fg='white', bg='#2d2d2d').pack(pady=15)
        
        tk.Label(header_frame, text=f"Sélectionnés: {len(self.current_selection)}/{self.max_selection}", 
                font=('Arial', 12), fg='#4CAF50', bg='#2d2d2d').pack()
        
        # Frame principal
        main_frame = tk.Frame(self.window, bg='#1e1e1e')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Frame gauche - Disponibles
        left_frame = tk.Frame(main_frame, bg='#2d2d2d')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        tk.Label(left_frame, text="Marchés Disponibles", 
                font=('Arial', 12, 'bold'), fg='white', bg='#2d2d2d').pack(pady=10)
        
        # Listbox des marchés disponibles
        self.available_listbox = tk.Listbox(left_frame, bg='#1e1e1e', fg='white', 
                                           font=('Arial', 10), selectmode='single',
                                           height=15, width=25)
        self.available_listbox.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Ajouter les symboles disponibles
        for symbol in self.available_symbols:
            if symbol not in self.current_selection:
                self.available_listbox.insert(tk.END, symbol)
        
        # Frame droite - Sélectionnés
        right_frame = tk.Frame(main_frame, bg='#2d2d2d')
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        tk.Label(right_frame, text="Marchés Sélectionnés", 
                font=('Arial', 12, 'bold'), fg='white', bg='#2d2d2d').pack(pady=10)
        
        # Listbox des marchés sélectionnés
        self.selected_listbox = tk.Listbox(right_frame, bg='#1e1e1e', fg='#4CAF50',
                                          font=('Arial', 10, 'bold'), selectmode='single',
                                          height=15, width=25)
        self.selected_listbox.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Ajouter les symboles actuellement sélectionnés
        for symbol in self.current_selection:
            self.selected_listbox.insert(tk.END, symbol)
        
        # Boutons centraux
        buttons_frame = tk.Frame(main_frame, bg='#1e1e1e')
        buttons_frame.pack(fill='x', pady=10)
        
        tk.Button(buttons_frame, text="Ajouter >>", command=self.add_symbol,
                 bg='#4CAF50', fg='white', font=('Arial', 10), width=15).pack(side='left', padx=5)
        tk.Button(buttons_frame, text="<< Retirer", command=self.remove_symbol,
                 bg='#f44336', fg='white', font=('Arial', 10), width=15).pack(side='right', padx=5)
        
        # Boutons en bas
        bottom_frame = tk.Frame(self.window, bg='#1e1e1e')
        bottom_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tk.Button(bottom_frame, text="Appliquer", command=self.apply_selection,
                 bg='#2196F3', fg='white', font=('Arial', 12, 'bold'), width=15).pack(side='left', padx=5)
        tk.Button(bottom_frame, text="Réinitialiser", command=self.reset_selection,
                 bg='#FF9800', fg='white', font=('Arial', 10), width=15).pack(side='left', padx=5)
        tk.Button(bottom_frame, text="Fermer", command=self.window.destroy,
                 bg='#666666', fg='white', font=('Arial', 10), width=15).pack(side='right', padx=5)
        
        # Bind events
        self.available_listbox.bind('<Double-1>', lambda e: self.add_symbol())
        self.selected_listbox.bind('<Double-1>', lambda e: self.remove_symbol())
    
    def add_symbol(self):
        """Ajouter un symbole à la sélection"""
        if len(self.current_selection) >= self.max_selection:
            messagebox.showwarning("Limite atteinte", f"Maximum {self.max_selection} marchés autorisés")
            return
        
        selection = self.available_listbox.curselection()
        if not selection:
            return
        
        symbol = self.available_listbox.get(selection[0])
        
        if symbol not in self.current_selection:
            self.current_selection.append(symbol)
            self.selected_listbox.insert(tk.END, symbol)
            self.available_listbox.delete(selection[0])
            self.update_counter()
    
    def remove_symbol(self):
        """Retirer un symbole de la sélection"""
        selection = self.selected_listbox.curselection()
        if not selection:
            return
        
        symbol = self.selected_listbox.get(selection[0])
        
        if symbol in self.current_selection:
            self.current_selection.remove(symbol)
            self.available_listbox.insert(tk.END, symbol)
            self.selected_listbox.delete(selection[0])
            self.update_counter()
    
    def reset_selection(self):
        """Réinitialiser la sélection"""
        self.current_selection = []
        self.selected_listbox.delete(0, tk.END)
        self.available_listbox.delete(0, tk.END)
        
        # Remettre tous les symboles disponibles
        for symbol in self.available_symbols:
            self.available_listbox.insert(tk.END, symbol)
        
        self.update_counter()
    
    def update_counter(self):
        """Mettre à jour le compteur"""
        counter_label = None
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Frame) and widget.winfo_y() == 10:
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label) and "Sélectionnés:" in child.cget("text"):
                        counter_label = child
                        break
        
        if counter_label:
            counter_label.config(text=f"Sélectionnés: {len(self.current_selection)}/{self.max_selection}")
    
    def apply_selection(self):
        """Appliquer la sélection et fermer"""
        if len(self.current_selection) == 0:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner au moins 1 marché")
            return
        
        if len(self.current_selection) > self.max_selection:
            messagebox.showwarning("Limite atteinte", f"Maximum {self.max_selection} marchés autorisés")
            return
        
        # Sauvegarder la sélection dans le main_ui
        if hasattr(self.main_ui, 'selected_symbols'):
            self.main_ui.selected_symbols = self.current_selection.copy()
        else:
            setattr(self.main_ui, 'selected_symbols', self.current_selection.copy())
        
        # Afficher confirmation
        messagebox.showinfo("Succès", f"Analyse limitée à {len(self.current_selection)} marchés:\n" + 
                          "\n".join(f"  - {symbol}" for symbol in self.current_selection))
        
        self.window.destroy()
    
    def get_current_selection(self) -> List[str]:
        """Récupérer la sélection actuelle"""
        return self.current_selection.copy()
    
    def set_current_selection(self, symbols: List[str]):
        """Définir la sélection actuelle"""
        # Valider les symboles
        valid_symbols = [s for s in symbols if s in self.available_symbols]
        self.current_selection = valid_symbols[:self.max_selection]
