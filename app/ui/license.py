import tkinter as tk
from tkinter import messagebox
import sys


LICENSE_KEY = "GH05T 1968"


class LicenseWindow(tk.Toplevel):

    def __init__(self, master):
        super().__init__(master)

        self.validated = False  # 🔑 signal

        self.title("Activation requise")
        self.geometry("300x150")
        self.resizable(False, False)

        tk.Label(
            self,
            text="Clé d'activation requise",
            font=("Arial", 11, "bold")
        ).pack(pady=10)

        self.entry = tk.Entry(self, justify="center")
        self.entry.pack(pady=5)
        
        # Lier la touche Enter à la validation
        self.entry.bind("<Return>", lambda event: self.validate())
        self.entry.bind("<KP_Enter>", lambda event: self.validate())

        tk.Button(
            self,
            text="Valider",
            cursor="hand2",
            command=self.validate
        ).pack(pady=10)

        self.protocol("WM_DELETE_WINDOW", self.block_exit)

    def validate(self):
        if self.entry.get().strip() == LICENSE_KEY:
            self.validated = True
            self.destroy()
        else:
            messagebox.showerror(
                "Accès refusé",
                "Clé invalide. Le logiciel va se fermer."
            )
            sys.exit(0)

    def block_exit(self):
        sys.exit(0)
