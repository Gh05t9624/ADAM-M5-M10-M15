"""
Panel de gestion des favoris dans l'interface ADAM
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional
from app.config.favorites import favorites_manager, MarketFavorite, PriorityLevel

class FavoritesPanel:
    """Panel pour gérer les favoris et marchés ciblés"""
    
    def __init__(self, parent, main_ui):
        self.parent = parent
        self.main_ui = main_ui
        self.window = None
        self.favorites_list = None
        self.current_favorite = None
        
    def show_favorites_window(self):
        """Afficher la fenêtre de gestion des favoris"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title("Ghost Analyzer - Gestion des Favoris")
        self.window.geometry("900x600")
        self.window.configure(bg='#1e1e1e')
        
        # Rendre la fenêtre modale
        self.window.transient(self.parent)
        self.window.grab_set()
        
        self.create_widgets()
        self.refresh_favorites_list()
        
        # Centrer la fenêtre
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"900x600+{x}+{y}")
    
    def create_widgets(self):
        """Créer les widgets de la fenêtre"""
        
        # Header
        header_frame = tk.Frame(self.window, bg='#2d2d2d', height=60)
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="Gestion des Favoris", 
                font=('Arial', 16, 'bold'), fg='white', bg='#2d2d2d').pack(side='left', padx=20, pady=15)
        
        # Boutons d'action
        btn_frame = tk.Frame(header_frame, bg='#2d2d2d')
        btn_frame.pack(side='right', padx=20, pady=10)
        
        tk.Button(btn_frame, text="Ajouter", command=self.add_favorite_dialog,
                 bg='#4CAF50', fg='white', font=('Arial', 10), padx=15).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Modifier", command=self.edit_favorite,
                 bg='#2196F3', fg='white', font=('Arial', 10), padx=15).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Supprimer", command=self.delete_favorite,
                 bg='#f44336', fg='white', font=('Arial', 10), padx=15).pack(side='left', padx=5)
        
        # Panneau principal
        main_frame = tk.Frame(self.window, bg='#1e1e1e')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Liste des favoris
        list_frame = tk.Frame(main_frame, bg='#2d2d2d')
        list_frame.pack(fill='both', expand=True)
        
        # Colonnes
        columns = ('Symbol', 'Priorité', 'Sessions', 'Score Min', 'Actif', 'Description')
        self.favorites_list = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configuration des colonnes
        column_widths = {'Symbol': 80, 'Priorité': 80, 'Sessions': 150, 'Score Min': 80, 'Actif': 60, 'Description': 300}
        for col in columns:
            self.favorites_list.heading(col, text=col)
            self.favorites_list.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.favorites_list.yview)
        self.favorites_list.configure(yscrollcommand=scrollbar.set)
        
        self.favorites_list.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Style pour la liste
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background='#2d2d2d', foreground='white', fieldbackground='#2d2d2d')
        style.configure('Treeview.Heading', background='#3d3d3d', foreground='white')
        
        # Panel de détails
        details_frame = tk.Frame(main_frame, bg='#2d2d2d', height=200)
        details_frame.pack(fill='x', pady=(10, 0))
        details_frame.pack_propagate(False)
        
        tk.Label(details_frame, text="Détails du marché sélectionné", 
                font=('Arial', 12, 'bold'), fg='white', bg='#2d2d2d').pack(pady=10)
        
        self.details_text = tk.Text(details_frame, height=8, bg='#1e1e1e', fg='white', 
                                   font=('Courier', 10), wrap='word')
        self.details_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Bind events
        self.favorites_list.bind('<<TreeviewSelect>>', self.on_favorite_select)
        self.favorites_list.bind('<Double-1>', lambda e: self.edit_favorite())
        
        # Boutons en bas
        bottom_frame = tk.Frame(self.window, bg='#1e1e1e')
        bottom_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tk.Button(bottom_frame, text="Activer/Désactiver", command=self.toggle_favorite,
                 bg='#FF9800', fg='white', font=('Arial', 10)).pack(side='left')
        tk.Button(bottom_frame, text="Exporter", command=self.export_favorites,
                 bg='#9C27B0', fg='white', font=('Arial', 10)).pack(side='left', padx=5)
        tk.Button(bottom_frame, text="Importer", command=self.import_favorites,
                 bg='#9C27B0', fg='white', font=('Arial', 10)).pack(side='left', padx=5)
        tk.Button(bottom_frame, text="Fermer", command=self.window.destroy,
                 bg='#666666', fg='white', font=('Arial', 10)).pack(side='right')
    
    def refresh_favorites_list(self):
        """Rafraîchir la liste des favoris"""
        # Vider la liste
        for item in self.favorites_list.get_children():
            self.favorites_list.delete(item)
        
        # Ajouter les favoris
        favorites = favorites_manager.get_active_favorites()
        for favorite in favorites:
            sessions_str = ', '.join(favorite.session_focus)
            active_str = "Oui" if favorite.active else "Non"
            
            self.favorites_list.insert('', 'end', values=(
                favorite.symbol,
                favorite.priority.value,
                sessions_str,
                favorite.min_score,
                active_str,
                favorite.description
            ))
    
    def on_favorite_select(self, event):
        """Quand un favori est sélectionné"""
        selection = self.favorites_list.selection()
        if not selection:
            return
        
        item = self.favorites_list.item(selection[0])
        symbol = item['values'][0]
        
        favorite = favorites_manager.get_favorite(symbol)
        if favorite:
            self.current_favorite = favorite
            self.show_favorite_details(favorite)
    
    def show_favorite_details(self, favorite: MarketFavorite):
        """Afficher les détails d'un favori"""
        self.details_text.delete(1.0, tk.END)
        
        details = f"""SYMBOL: {favorite.symbol}
PRIORITÉ: {favorite.priority.value}
DESCRIPTION: {favorite.description}
SCORE MINIMUM: {favorite.min_score}
ACTIF: {'Oui' if favorite.active else 'Non'}

SESSIONS OPTIMALES:
{chr(10).join(f'  - {session}' for session in favorite.session_focus)}

PARAMÈTRES PERSONNALISÉS:
"""
        for key, value in favorite.custom_settings.items():
            details += f"  {key}: {value}\n"
        
        self.details_text.insert(1.0, details)
    
    def add_favorite_dialog(self):
        """Dialog pour ajouter un nouveau favori"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Ajouter un favori")
        dialog.geometry("500x400")
        dialog.configure(bg='#1e1e1e')
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Variables
        symbol_var = tk.StringVar()
        priority_var = tk.StringVar(value="medium")
        min_score_var = tk.IntVar(value=65)
        description_var = tk.StringVar()
        active_var = tk.BooleanVar(value=True)
        
        # Formulaire
        tk.Label(dialog, text="Symbole:", fg='white', bg='#1e1e1e').grid(row=0, column=0, padx=10, pady=5, sticky='w')
        tk.Entry(dialog, textvariable=symbol_var, bg='#2d2d2d', fg='white').grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="Priorité:", fg='white', bg='#1e1e1e').grid(row=1, column=0, padx=10, pady=5, sticky='w')
        priority_combo = ttk.Combobox(dialog, textvariable=priority_var, 
                                     values=["critical", "high", "medium", "low", "watch"])
        priority_combo.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="Score Minimum:", fg='white', bg='#1e1e1e').grid(row=2, column=0, padx=10, pady=5, sticky='w')
        tk.Entry(dialog, textvariable=min_score_var, bg='#2d2d2d', fg='white').grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="Description:", fg='white', bg='#1e1e1e').grid(row=3, column=0, padx=10, pady=5, sticky='w')
        tk.Entry(dialog, textvariable=description_var, bg='#2d2d2d', fg='white', width=40).grid(row=3, column=1, padx=10, pady=5)
        
        tk.Checkbutton(dialog, text="Actif", variable=active_var, 
                      bg='#1e1e1e', fg='white', selectcolor='#1e1e1e').grid(row=4, column=0, columnspan=2, pady=10)
        
        # Boutons
        btn_frame = tk.Frame(dialog, bg='#1e1e1e')
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        def save_favorite():
            symbol = symbol_var.get().upper()
            if not symbol:
                messagebox.showerror("Erreur", "Veuillez entrer un symbole")
                return
            
            try:
                favorite = MarketFavorite(
                    symbol=symbol,
                    priority=PriorityLevel(priority_var.get()),
                    session_focus=["London", "New York"],  # Par défaut
                    min_score=min_score_var.get(),
                    custom_settings={},
                    description=description_var.get() or f"{symbol} - Personnalisé",
                    active=active_var.get()
                )
                
                favorites_manager.add_favorite(favorite)
                self.refresh_favorites_list()
                dialog.destroy()
                messagebox.showinfo("Succès", f"Favori {symbol} ajouté avec succès")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'ajout: {str(e)}")
        
        tk.Button(btn_frame, text="Ajouter", command=save_favorite,
                 bg='#4CAF50', fg='white').pack(side='left', padx=5)
        tk.Button(btn_frame, text="Annuler", command=dialog.destroy,
                 bg='#666666', fg='white').pack(side='left', padx=5)
    
    def edit_favorite(self):
        """Modifier le favori sélectionné"""
        if not self.current_favorite:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un favori")
            return
        
        # Implémenter le dialog de modification
        messagebox.showinfo("Info", f"Modification de {self.current_favorite.symbol} - À implémenter")
    
    def delete_favorite(self):
        """Supprimer le favori sélectionné"""
        if not self.current_favorite:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un favori")
            return
        
        if messagebox.askyesno("Confirmation", f"Supprimer {self.current_favorite.symbol}?"):
            del favorites_manager.favorites[self.current_favorite.symbol]
            self.refresh_favorites_list()
            self.details_text.delete(1.0, tk.END)
            self.current_favorite = None
    
    def toggle_favorite(self):
        """Activer/désactiver le favori sélectionné"""
        if not self.current_favorite:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un favori")
            return
        
        new_state = favorites_manager.toggle_favorite(self.current_favorite.symbol)
        self.refresh_favorites_list()
        messagebox.showinfo("Info", f"{self.current_favorite.symbol} est maintenant {'actif' if new_state else 'désactivé'}")
    
    def export_favorites(self):
        """Exporter la configuration des favoris"""
        try:
            import json
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                data = favorites_manager.export_favorites()
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                messagebox.showinfo("Succès", f"Favoris exportés dans {filename}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")
    
    def import_favorites(self):
        """Importer une configuration de favoris"""
        try:
            import json
            from tkinter import filedialog
            
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                favorites_manager.import_favorites(data)
                self.refresh_favorites_list()
                messagebox.showinfo("Succès", f"Favoris importés depuis {filename}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'import: {str(e)}")
