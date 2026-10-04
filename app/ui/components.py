import tkinter as tk


class GhostButton(tk.Canvas):
    """
    Bouton custom – style ADAM
    - flat
    - hover clean
    - stable
    - arrondi avec border-radius
    """

    def __init__(self, parent, text, command=None, smaller=False):
        super().__init__(parent, bg="#0B0F14", highlightthickness=0)

        self.command = command
        self.bg_color = "#22C55E"
        self.hover_color = "#16A34A"
        self.text_color = "#020617"
        self.corner_radius = 8
        
        # Taille réduite si demandé
        if smaller:
            self.font_size = 9
            self.pad_x = 12
            self.pad_y = 6
        else:
            self.font_size = 10
            self.pad_x = 15
            self.pad_y = 8

        # Calculer la largeur nécessaire
        temp_label = tk.Label(parent, text=text, font=("Segoe UI", self.font_size, "bold"))
        temp_label.update_idletasks()
        text_width = temp_label.winfo_reqwidth()
        temp_label.destroy()
        
        new_width = text_width + self.pad_x * 2
        self.config(width=new_width, height=25)

        # Créer le rectangle arrondi
        self.rect_id = self.create_rounded_rect(
            0, 0, new_width, 25, 
            radius=self.corner_radius, 
            fill=self.bg_color
        )
        
        # Texte centré
        self.text_id = self.create_text(
            new_width/2, 12.5,
            text=text,
            fill=self.text_color,
            font=("Segoe UI", self.font_size, "bold")
        )

        # Events
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def create_rounded_rect(self, x1, y1, x2, y2, radius=8, **kwargs):
        """Crée un rectangle avec coins arrondis"""
        points = [
            x1 + radius, y1,
            x1 + radius, y1,
            x2 - radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, **kwargs, smooth=True)

    def _on_hover(self, event):
        self.itemconfig(self.rect_id, fill=self.hover_color)

    def _on_leave(self, event):
        self.itemconfig(self.rect_id, fill=self.bg_color)

    def _on_click(self, event):
        if self.command:
            self.command()
