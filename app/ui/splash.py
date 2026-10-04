import tkinter as tk
from PIL import Image, ImageTk
import os


class SplashScreen(tk.Toplevel):

    def __init__(self, master):
        super().__init__(master)

        self.overrideredirect(True)
        self.configure(bg="black")

        width, height = 400, 300
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Logo
        logo_path = os.path.join("assets", "logo.png")
        img = Image.open(logo_path).resize((150, 150))
        self.logo = ImageTk.PhotoImage(img)

        tk.Label(self, image=self.logo, bg="black").pack(pady=20)

        tk.Label(
            self,
            text="Produit de l'entreprise PQLab.",
            fg="white",
            bg="black",
            font=("Arial", 12, "bold")
        ).pack()
