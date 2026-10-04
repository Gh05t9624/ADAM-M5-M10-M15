import tkinter as tk


class StatsPanel(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg="#111827")

        self.labels = {}

        self._add_label("total_trades", "Total trades : 0")
        self._add_label("authorized", "Autorisé : 0")
        self._add_label("winrate", "Direction dominante : -")

    def _add_label(self, key, text):
        lbl = tk.Label(
            self,
            text=text,
            fg="#E5E7EB",
            bg="#111827",
            font=("Segoe UI", 11)
            
        )
        lbl.pack(anchor="w", pady=0, padx=100, side="right")
        self.labels[key] = lbl

    # 🔥 C’EST ICI QUE VA TON CODE
    def update(self, stats):
        self.labels["total_trades"].config(
            text=f"Total trades : {stats['total_trades']}"
        )

        self.labels["authorized"].config(
            text=f"Autorisé : {stats['authorized']}"
        )

        direction = max(
            stats["by_direction"],
            key=stats["by_direction"].get,
            default="-"
        )

        self.labels["winrate"].config(
            text=f"Direction dominante : {direction}"
        )
