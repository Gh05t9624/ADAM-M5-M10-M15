import tkinter as tk
from app.ui.layout import GhostUI
from app.ui.splash import SplashScreen
from app.ui.license import LicenseWindow
import sys, os
from app.engine.context import MarketContext


def main():
    root = tk.Tk()
    root.iconbitmap("assets/icon.ico")
    root.title("ADAM M5-M10-M15 - Adaptive Deep Analysis Machine")
    root.geometry("1200x700")
    root.configure(bg="#0B0F14")

    # Anti-debug basique
    if hasattr(sys, 'gettrace') and sys.gettrace():
        sys.exit(0)

    if getattr(sys, 'frozen', False):
        os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

    # Splash
    splash = SplashScreen(root)
    splash.iconbitmap("assets/icon.ico")
    root.update()
    root.after(2500)
    splash.destroy()

    # Licence
    license_window = LicenseWindow(root)
    license_window.iconbitmap("assets/icon.ico")
    root.wait_window(license_window)

    if not license_window.validated:
        return

    # ===============================
    # 1️⃣ PROGRAMME PRINCIPAL
    # ===============================
    app = GhostUI(root)
    app.pack(fill="both", expand=True)



    # ➜ Création du contexte
    context = MarketContext(
        trading_allowed=True,
        volatility_expected=False
    )

    root.mainloop()


if __name__ == "__main__":
    main()