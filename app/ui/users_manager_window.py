# app/ui/users_manager_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from app.config.users_manager import get_users_manager

class UsersManagerWindow:
    """Fenêtre de gestion des utilisateurs et leurs abonnements"""
    
    def __init__(self, parent):
        self.parent = parent
        self.users_manager = get_users_manager()
        
        # Créer la fenêtre
        self.window = tk.Toplevel(parent)
        self.window.title("Gestion des Utilisateurs Telegram")
        self.window.geometry("800x600")
        self.window.configure(bg="#0B0F14")
        
        self._build_ui()
        self._refresh_users_list()
    
    def _build_ui(self):
        """Construit l'interface utilisateur"""
        # Header
        header = tk.Frame(self.window, bg="#1F2937", height=60)
        header.pack(fill="x", padx=10, pady=10)
        
        title = tk.Label(
            header,
            text="👥 Gestion des Utilisateurs Telegram",
            fg="#E5E7EB",
            bg="#1F2937",
            font=("Segoe UI", 16, "bold")
        )
        title.pack(pady=15)
        
        # Zone principale
        main_frame = tk.Frame(self.window, bg="#0B0F14")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Liste des utilisateurs (gauche)
        list_frame = tk.Frame(main_frame, bg="#111827", width=400)
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        tk.Label(
            list_frame,
            text="Utilisateurs",
            fg="#E5E7EB",
            bg="#111827",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=10)
        
        # Treeview pour la liste
        columns = ("name", "chat_id", "symbols_count", "enabled")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("name", text="Nom")
        self.tree.heading("chat_id", text="Chat ID")
        self.tree.heading("symbols_count", text="Symboles")
        self.tree.heading("enabled", text="Actif")
        
        self.tree.column("name", width=150)
        self.tree.column("chat_id", width=150)
        self.tree.column("symbols_count", width=80)
        self.tree.column("enabled", width=60)
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self._on_user_select)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Boutons (bas gauche)
        buttons_frame = tk.Frame(list_frame, bg="#111827")
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(
            buttons_frame,
            text="➕ Ajouter",
            command=self._add_user,
            bg="#22C55E",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=20
        ).pack(side="left", padx=5)
        
        tk.Button(
            buttons_frame,
            text="✏️ Modifier",
            command=self._edit_user,
            bg="#3B82F6",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=20
        ).pack(side="left", padx=5)
        
        tk.Button(
            buttons_frame,
            text="🗑️ Supprimer",
            command=self._delete_user,
            bg="#EF4444",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=20
        ).pack(side="left", padx=5)
        
        # Détails utilisateur (droite)
        details_frame = tk.Frame(main_frame, bg="#111827", width=350)
        details_frame.pack(side="right", fill="both", padx=(5, 0))
        
        tk.Label(
            details_frame,
            text="Détails de l'utilisateur",
            fg="#E5E7EB",
            bg="#111827",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=10)
        
        # Formulaire
        self._build_form(details_frame)
        
        # Liste des symboles
        self._build_symbols_list(details_frame)
    
    def _build_form(self, parent):
        """Construit le formulaire de détails"""
        form_frame = tk.Frame(parent, bg="#111827")
        form_frame.pack(fill="x", padx=10, pady=5)
        
        # Nom
        tk.Label(
            form_frame,
            text="Nom:",
            fg="#9CA3AF",
            bg="#111827",
            font=("Segoe UI", 10)
        ).grid(row=0, column=0, sticky="w", pady=5)
        
        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(
            form_frame,
            textvariable=self.name_var,
            bg="#1F2937",
            fg="#E5E7EB",
            insertbackground="#E5E7EB",
            font=("Segoe UI", 10),
            relief="flat",
            width=30
        )
        self.name_entry.grid(row=0, column=1, pady=5, padx=5)
        
        # Chat ID
        tk.Label(
            form_frame,
            text="Chat ID:",
            fg="#9CA3AF",
            bg="#111827",
            font=("Segoe UI", 10)
        ).grid(row=1, column=0, sticky="w", pady=5)
        
        self.chat_id_var = tk.StringVar()
        self.chat_id_entry = tk.Entry(
            form_frame,
            textvariable=self.chat_id_var,
            bg="#1F2937",
            fg="#E5E7EB",
            insertbackground="#E5E7EB",
            font=("Segoe UI", 10),
            relief="flat",
            width=30
        )
        self.chat_id_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Timeframes
        tk.Label(
            form_frame,
            text="Timeframes:",
            fg="#9CA3AF",
            bg="#111827",
            font=("Segoe UI", 10)
        ).grid(row=2, column=0, sticky="w", pady=5)
        
        self.m5_var = tk.BooleanVar(value=True)
        self.m10_var = tk.BooleanVar(value=True)
        self.m15_var = tk.BooleanVar(value=True)
        
        timeframe_frame = tk.Frame(form_frame, bg="#111827")
        timeframe_frame.grid(row=2, column=1, sticky="w", pady=5, padx=5)
        
        tk.Checkbutton(
            timeframe_frame,
            text="M5",
            variable=self.m5_var,
            bg="#111827",
            fg="#E5E7EB",
            selectcolor="#1F2937",
            font=("Segoe UI", 10)
        ).pack(side="left", padx=5)

        tk.Checkbutton(
            timeframe_frame,
            text="M10",
            variable=self.m10_var,
            bg="#111827",
            fg="#E5E7EB",
            selectcolor="#1F2937",
            font=("Segoe UI", 10)
        ).pack(side="left", padx=5)

        tk.Checkbutton(
            timeframe_frame,
            text="M15",
            variable=self.m15_var,
            bg="#111827",
            fg="#E5E7EB",
            selectcolor="#1F2937",
            font=("Segoe UI", 10)
        ).pack(side="left", padx=5)
        
        # Actif
        self.enabled_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            form_frame,
            text="Utilisateur actif",
            variable=self.enabled_var,
            bg="#111827",
            fg="#E5E7EB",
            selectcolor="#1F2937",
            font=("Segoe UI", 10)
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
        
        # Bouton sauvegarder
        tk.Button(
            form_frame,
            text="💾 Sauvegarder",
            command=self._save_user,
            bg="#10B981",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=20
        ).grid(row=4, column=0, columnspan=2, pady=10)
    
    def _build_symbols_list(self, parent):
        """Construit la liste des symboles"""
        symbols_frame = tk.Frame(parent, bg="#111827")
        symbols_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        tk.Label(
            symbols_frame,
            text="Symboles abonnés (séparés par virgule):",
            fg="#9CA3AF",
            bg="#111827",
            font=("Segoe UI", 10)
        ).pack(anchor="w")
        
        self.symbols_text = tk.Text(
            symbols_frame,
            bg="#1F2937",
            fg="#E5E7EB",
            insertbackground="#E5E7EB",
            font=("Segoe UI", 10),
            relief="flat",
            height=10,
            width=40
        )
        self.symbols_text.pack(fill="both", expand=True, pady=5)
        
        # Scrollbar
        symbols_scrollbar = ttk.Scrollbar(symbols_frame, orient="vertical", command=self.symbols_text.yview)
        symbols_scrollbar.pack(side="right", fill="y")
        self.symbols_text.configure(yscrollcommand=symbols_scrollbar.set)
    
    def _refresh_users_list(self):
        """Rafraîchit la liste des utilisateurs"""
        # Vider la liste
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Ajouter les utilisateurs
        for user in self.users_manager.get_users():
            symbols_count = len(user.get("symbols", []))
            enabled = "✅" if user.get("enabled", True) else "❌"
            
            self.tree.insert(
                "",
                "end",
                values=(
                    user.get("name", ""),
                    user.get("chat_id", ""),
                    symbols_count,
                    enabled
                ),
                tags=(user["id"],)
            )
    
    def _on_user_select(self, event):
        """Gestion de la sélection d'un utilisateur"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        user_id = self.tree.item(item, "tags")[0]
        
        # Trouver l'utilisateur
        user = next((u for u in self.users_manager.get_users() if u["id"] == user_id), None)
        if user:
            self._populate_form(user)
    
    def _populate_form(self, user):
        """Remplit le formulaire avec les données de l'utilisateur"""
        self.name_var.set(user.get("name", ""))
        self.chat_id_var.set(user.get("chat_id", ""))
        self.enabled_var.set(user.get("enabled", True))
        
        # Timeframes
        timeframes = user.get("timeframes", ["M5", "M10", "M15"])
        self.m5_var.set("M5" in timeframes)
        self.m10_var.set("M10" in timeframes)
        self.m15_var.set("M15" in timeframes)
        
        symbols = user.get("symbols", [])
        self.symbols_text.delete("1.0", tk.END)
        self.symbols_text.insert("1.0", ", ".join(symbols))
    
    def _clear_form(self):
        """Vide le formulaire"""
        self.name_var.set("")
        self.chat_id_var.set("")
        self.enabled_var.set(True)
        self.m5_var.set(True)
        self.m10_var.set(True)
        self.m15_var.set(True)
        self.symbols_text.delete("1.0", tk.END)
    
    def _add_user(self):
        """Ajoute un nouvel utilisateur"""
        self._clear_form()
        self.current_user_id = None
    
    def _edit_user(self):
        """Modifie l'utilisateur sélectionné"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Avertissement", "Sélectionnez un utilisateur à modifier")
            return
        
        item = selection[0]
        self.current_user_id = self.tree.item(item, "tags")[0]
    
    def _delete_user(self):
        """Supprime l'utilisateur sélectionné"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Avertissement", "Sélectionnez un utilisateur à supprimer")
            return
        
        item = selection[0]
        user_id = self.tree.item(item, "tags")[0]
        
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cet utilisateur?"):
            self.users_manager.remove_user(user_id)
            self._refresh_users_list()
            self._clear_form()
    
    def _save_user(self):
        """Sauvegarde l'utilisateur"""
        name = self.name_var.get().strip()
        chat_id = self.chat_id_var.get().strip()
        symbols_text = self.symbols_text.get("1.0", tk.END).strip()
        enabled = self.enabled_var.get()
        
        # Parser les timeframes
        timeframes = []
        if self.m5_var.get():
            timeframes.append("M5")
        if self.m10_var.get():
            timeframes.append("M10")
        if self.m15_var.get():
            timeframes.append("M15")
        
        if not timeframes:
            messagebox.showerror("Erreur", "Au moins un timeframe doit être sélectionné")
            return
        
        if not name or not chat_id:
            messagebox.showerror("Erreur", "Le nom et le Chat ID sont obligatoires")
            return
        
        # Parser les symboles
        symbols = [s.strip() for s in symbols_text.split(",") if s.strip()]
        
        if hasattr(self, 'current_user_id') and self.current_user_id:
            # Modifier utilisateur existant
            self.users_manager.update_user(self.current_user_id, name=name, chat_id=chat_id, symbols=symbols, timeframes=timeframes)
            self.users_manager.enable_user(self.current_user_id, enabled)
        else:
            # Ajouter nouvel utilisateur
            self.users_manager.add_user(name, chat_id, symbols, timeframes)
        
        self._refresh_users_list()
        self._clear_form()
        messagebox.showinfo("Succès", "Utilisateur sauvegardé avec succès")
