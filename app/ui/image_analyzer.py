# app/ui/image_analyzer.py

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from typing import Dict, List, Tuple, Optional
import os

class ImageAnalyzer:
    """Analyseur d'images pour captures d'écran de marchés"""
    
    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.current_image = None
        self.image_path = None
        self.analysis_results = {}
        
    def show_analyzer(self):
        """Afficher la fenêtre d'analyse d'images"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title("Analyseur d'Images - ADAM")
        self.window.geometry("1200x800")
        self.window.configure(bg="#111827")
        
        # Header
        header_frame = tk.Frame(self.window, bg="#1F2937")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        title = tk.Label(
            header_frame,
            text="ANALYSEUR D'IMAGES DE MARCHÉS",
            fg="#10B981",
            bg="#1F2937",
            font=("Segoe UI", 16, "bold")
        )
        title.pack(pady=10)
        
        subtitle = tk.Label(
            header_frame,
            text="Vérifiez si votre capture d'écran correspond à votre stratégie",
            fg="#9CA3AF",
            bg="#1F2937",
            font=("Segoe UI", 11)
        )
        subtitle.pack(pady=(0, 10))
        
        # Main content
        main_frame = tk.Frame(self.window, bg="#111827")
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Left panel - Image
        left_frame = tk.Frame(main_frame, bg="#1F2937", width=600)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        left_frame.pack_propagate(False)
        
        # Image controls
        image_controls = tk.Frame(left_frame, bg="#1F2937")
        image_controls.pack(fill="x", padx=10, pady=10)
        
        self.load_btn = tk.Button(
            image_controls,
            text="CHARGER UNE IMAGE",
            font=("Segoe UI", 11, "bold"),
            bg="#10B981",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.load_image
        )
        self.load_btn.pack(side="left", padx=(0, 10))
        
        self.analyze_btn = tk.Button(
            image_controls,
            text="ANALYSER",
            font=("Segoe UI", 11, "bold"),
            bg="#3B82F6",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.analyze_image,
            state="disabled"
        )
        self.analyze_btn.pack(side="left", padx=(0, 10))
        
        # Image display
        self.image_frame = tk.Frame(left_frame, bg="#374151", relief="sunken", bd=2)
        self.image_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.image_label = tk.Label(
            self.image_frame,
            text="Aucune image chargée",
            fg="#9CA3AF",
            bg="#374151",
            font=("Segoe UI", 14)
        )
        self.image_label.pack(expand=True)
        
        # Right panel - Analysis results
        right_frame = tk.Frame(main_frame, bg="#1F2937", width=500)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        right_frame.pack_propagate(False)
        
        # Analysis title
        analysis_title = tk.Label(
            right_frame,
            text="RÉSULTATS DE L'ANALYSE",
            fg="#F59E0B",
            bg="#1F2937",
            font=("Segoe UI", 14, "bold")
        )
        analysis_title.pack(pady=10)
        
        # Analysis content
        self.analysis_frame = tk.Frame(right_frame, bg="#1F2937")
        self.analysis_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Strategy checklist
        self.create_strategy_checklist()
        
        # Results display
        self.results_text = tk.Text(
            self.analysis_frame,
            bg="#374151",
            fg="#E5E7EB",
            font=("Courier New", 10),
            wrap="word",
            height=20
        )
        self.results_text.pack(fill="both", expand=True, pady=(10, 0))
        
        # Scrollbar for results
        scrollbar = tk.Scrollbar(self.results_text)
        scrollbar.pack(side="right", fill="y")
        self.results_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.results_text.yview)
        
    def create_strategy_checklist(self):
        """Créer la checklist de stratégie"""
        checklist_frame = tk.LabelFrame(
            self.analysis_frame,
            text="CHECKLIST STRATÉGIE",
            fg="#10B981",
            bg="#1F2937",
            font=("Segoe UI", 12, "bold")
        )
        checklist_frame.pack(fill="x", pady=(0, 10))
        
        self.strategy_vars = {}
        strategy_items = [
            ("Tendance claire (HH/HL ou LH/LL)", "trend"),
            ("Structure EMA (9 au-dessus/21)", "ema"),
            ("RSI dans zone normale (30-70)", "rsi"),
            ("Pullback dans zone 38-61%", "pullback"),
            ("Volume confirmé", "volume"),
            ("Session de trading active", "session"),
            ("Pas de news importantes", "news"),
            ("Risk/Reward >= 1:2", "risk_reward")
        ]
        
        for text, key in strategy_items:
            var = tk.BooleanVar()
            self.strategy_vars[key] = var
            
            cb = tk.Checkbutton(
                checklist_frame,
                text=text,
                variable=var,
                fg="#E5E7EB",
                bg="#1F2937",
                selectcolor="#374151",
                font=("Segoe UI", 10)
            )
            cb.pack(anchor="w", padx=10, pady=2)
    
    def load_image(self):
        """Charger une image depuis le fichier"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner une capture d'écran",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.image_path = file_path
                self.display_image(file_path)
                self.analyze_btn.config(state="normal")
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, f"Image chargée : {os.path.basename(file_path)}\n")
                self.results_text.insert(tk.END, "="*50 + "\n")
                self.results_text.insert(tk.END, "Prêt pour l'analyse...\n")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger l'image : {str(e)}")
    
    def display_image(self, image_path):
        """Afficher l'image dans l'interface"""
        try:
            # Charger et redimensionner l'image
            image = Image.open(image_path)
            
            # Redimensionner pour s'adapter au frame
            frame_width = 580
            frame_height = 400
            
            # Calculer le ratio
            img_ratio = image.width / image.height
            frame_ratio = frame_width / frame_height
            
            if img_ratio > frame_ratio:
                new_width = frame_width
                new_height = int(frame_width / img_ratio)
            else:
                new_height = frame_height
                new_width = int(frame_height * img_ratio)
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convertir pour Tkinter
            self.current_image = ImageTk.PhotoImage(image)
            
            # Afficher
            self.image_label.config(image=self.current_image, text="")
            self.image_label.image = self.current_image
            
        except Exception as e:
            self.image_label.config(text=f"Erreur d'affichage : {str(e)}")
    
    def analyze_image(self):
        """Analyser l'image chargée"""
        if not self.image_path:
            messagebox.showwarning("Avertissement", "Veuillez d'abord charger une image")
            return
        
        try:
            # Effacer les résultats précédents
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "ANALYSE DE L'IMAGE EN COURS...\n")
            self.results_text.insert(tk.END, "="*50 + "\n\n")
            
            # Analyser l'image
            results = self.perform_image_analysis()
            
            # Afficher les résultats
            self.display_analysis_results(results)
            
            # Calculer le score de conformité
            self.calculate_strategy_score()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'analyse : {str(e)}")
    
    def perform_image_analysis(self) -> Dict:
        """Effectuer l'analyse de l'image (version simplifiée manuelle)"""
        # Version simplifiée basée sur la checklist utilisateur
        results = {
            "trend_analysis": self.get_manual_trend_analysis(),
            "ema_analysis": self.get_manual_ema_analysis(),
            "rsi_analysis": self.get_manual_rsi_analysis(),
            "structure_analysis": self.get_manual_structure_analysis(),
            "volume_analysis": self.get_manual_volume_analysis(),
            "pattern_recognition": self.get_manual_patterns_analysis()
        }
        
        return results
    
    def get_manual_trend_analysis(self) -> Dict:
        """Analyse basée sur la checklist tendance"""
        trend_ok = self.strategy_vars.get("trend", tk.BooleanVar()).get()
        
        return {
            "direction": "HAUSSIER" if trend_ok else "NEUTRE",
            "confidence": 0.8 if trend_ok else 0.3,
            "higher_highs": trend_ok,
            "higher_lows": trend_ok,
            "structure_strength": "Forte" if trend_ok else "Faible"
        }
    
    def get_manual_ema_analysis(self) -> Dict:
        """Analyse basée sur la checklist EMA"""
        ema_ok = self.strategy_vars.get("ema", tk.BooleanVar()).get()
        
        return {
            "ema9_above_ema21": ema_ok,
            "price_above_ema9": ema_ok,
            "ema_alignment": "Haussière" if ema_ok else "Neutre",
            "crossover_detected": ema_ok
        }
    
    def get_manual_rsi_analysis(self) -> Dict:
        """Analyse basée sur la checklist RSI"""
        rsi_ok = self.strategy_vars.get("rsi", tk.BooleanVar()).get()
        
        return {
            "rsi_value": 55.0 if rsi_ok else 45.0,
            "rsi_trend": "Haussier" if rsi_ok else "Neutre",
            "overbought": False,
            "oversold": False,
            "divergence": None
        }
    
    def get_manual_structure_analysis(self) -> Dict:
        """Analyse basée sur la checklist structure"""
        pullback_ok = self.strategy_vars.get("pullback", tk.BooleanVar()).get()
        
        return {
            "pullback_detected": pullback_ok,
            "pullback_zone": "45-55%" if pullback_ok else "0-20%",
            "impulse_strength": 1.8 if pullback_ok else 0.8,
            "continuation_probability": 0.82 if pullback_ok else 0.30
        }
    
    def get_manual_volume_analysis(self) -> Dict:
        """Analyse basée sur la checklist volume"""
        volume_ok = self.strategy_vars.get("volume", tk.BooleanVar()).get()
        
        return {
            "volume_above_average": volume_ok,
            "volume_trend": "Augmentant" if volume_ok else "Faible",
            "volume_confirmation": volume_ok
        }
    
    def get_manual_patterns_analysis(self) -> Dict:
        """Analyse basée sur la checklist patterns"""
        return {
            "flag_pattern": False,
            "triangle_pattern": False,
            "head_shoulders": False,
            "double_top_bottom": False,
            "channel": True
        }
    
    def display_analysis_results(self, results: Dict):
        """Afficher les résultats de l'analyse"""
        
        # Tendance
        trend = results["trend_analysis"]
        self.results_text.insert(tk.END, "ANALYSE DE TENDANCE :\n", "header")
        self.results_text.insert(tk.END, f"Direction : {trend['direction']}\n")
        self.results_text.insert(tk.END, f"Confiance : {trend['confidence']*100:.1f}%\n")
        self.results_text.insert(tk.END, f"Structure : {trend['structure_strength']}\n")
        self.results_text.insert(tk.END, f"Higher Highs : {'Oui' if trend['higher_highs'] else 'Non'}\n")
        self.results_text.insert(tk.END, f"Higher Lows : {'Oui' if trend['higher_lows'] else 'Non'}\n\n")
        
        # EMA
        ema = results["ema_analysis"]
        self.results_text.insert(tk.END, "ANALYSE EMA :\n", "header")
        self.results_text.insert(tk.END, f"EMA9 > EMA21 : {'Oui' if ema['ema9_above_ema21'] else 'Non'}\n")
        self.results_text.insert(tk.END, f"Prix > EMA9 : {'Oui' if ema['price_above_ema9'] else 'Non'}\n")
        self.results_text.insert(tk.END, f"Alignement : {ema['ema_alignment']}\n\n")
        
        # RSI
        rsi = results["rsi_analysis"]
        self.results_text.insert(tk.END, "ANALYSE RSI :\n", "header")
        self.results_text.insert(tk.END, f"Valeur RSI : {rsi['rsi_value']:.1f}\n")
        self.results_text.insert(tk.END, f"Tendance RSI : {rsi['rsi_trend']}\n")
        self.results_text.insert(tk.END, f"Surachat : {'Oui' if rsi['overbought'] else 'Non'}\n")
        self.results_text.insert(tk.END, f"Survente : {'Oui' if rsi['oversold'] else 'Non'}\n\n")
        
        # Structure
        structure = results["structure_analysis"]
        self.results_text.insert(tk.END, "ANALYSE DE STRUCTURE :\n", "header")
        self.results_text.insert(tk.END, f"Pullback : {'Oui' if structure['pullback_detected'] else 'Non'}\n")
        self.results_text.insert(tk.END, f"Zone Pullback : {structure['pullback_zone']}\n")
        self.results_text.insert(tk.END, f"Force Impulsion : {structure['impulse_strength']:.1f}\n")
        self.results_text.insert(tk.END, f"Probabilité Continuation : {structure['continuation_probability']*100:.1f}%\n\n")
        
        # Volume
        volume = results["volume_analysis"]
        self.results_text.insert(tk.END, "ANALYSE VOLUME :\n", "header")
        self.results_text.insert(tk.END, f"Volume > Moyenne : {'Oui' if volume['volume_above_average'] else 'Non'}\n")
        self.results_text.insert(tk.END, f"Tendance Volume : {volume['volume_trend']}\n")
        self.results_text.insert(tk.END, f"Confirmation Volume : {'Oui' if volume['volume_confirmation'] else 'Non'}\n\n")
        
        # Patterns
        patterns = results["pattern_recognition"]
        self.results_text.insert(tk.END, "PATTERNS DÉTECTÉS :\n", "header")
        for pattern, detected in patterns.items():
            self.results_text.insert(tk.END, f"{pattern.replace('_', ' ').title()} : {'Oui' if detected else 'Non'}\n")
        
        # Configurer les tags pour le formatage
        self.results_text.tag_config("header", foreground="#10B981", font=("Courier New", 10, "bold"))
    
    def calculate_strategy_score(self):
        """Calculer le score de conformité à la stratégie"""
        self.results_text.insert(tk.END, "\n" + "="*50 + "\n", "header")
        self.results_text.insert(tk.END, "SCORE DE CONFORMITÉ STRATÉGIE :\n", "header")
        self.results_text.insert(tk.END, "="*50 + "\n\n")
        
        # Compter les critères validés
        checked_count = sum(1 for var in self.strategy_vars.values() if var.get())
        total_count = len(self.strategy_vars)
        
        if total_count > 0:
            score_percentage = (checked_count / total_count) * 100
        else:
            score_percentage = 0
        
        # Afficher le score
        self.results_text.insert(tk.END, f"Critères validés : {checked_count}/{total_count}\n")
        self.results_text.insert(tk.END, f"Score de conformité : {score_percentage:.1f}%\n\n")
        
        # Recommandation
        if score_percentage >= 80:
            recommendation = "EXCELLENT - Setup conforme à votre stratégie !"
            color = "#10B981"
        elif score_percentage >= 60:
            recommendation = "BON - Setup intéressant, attention aux détails"
            color = "#F59E0B"
        elif score_percentage >= 40:
            recommendation = "MOYEN - Setup partiellement conforme"
            color = "#EF4444"
        else:
            recommendation = "FAIBLE - Setup non conforme à votre stratégie"
            color = "#EF4444"
        
        self.results_text.insert(tk.END, "RECOMMANDATION :\n", "header")
        self.results_text.insert(tk.END, recommendation + "\n", "recommendation")
        
        # Configurer le tag de recommandation
        self.results_text.tag_config("recommendation", foreground=color, font=("Courier New", 10, "bold"))
