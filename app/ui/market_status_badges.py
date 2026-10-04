# app/ui/market_status_badges.py

import tkinter as tk
from datetime import datetime

class MarketStatusBadges:
    """
    Crée des badges visuels pour le statut des marchés dans l'interface UI
    Indique clairement si un marché est ouvert, fermé, bloqué par news, etc.
    """
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.badges = {}
        
        # Configuration des couleurs et styles
        self.colors = {
            'OPEN': {
                'bg': '#22C55E',      # Vert
                'fg': 'white',
                'text': '🟢 OUVERT',
                'description': 'Session active'
            },
            'CLOSED': {
                'bg': '#EF4444',      # Rouge
                'fg': 'white',
                'text': '🔴 FERMÉ',
                'description': 'Session fermée'
            },
            'BLOCKED_BY_NEWS': {
                'bg': '#F59E0B',      # Orange
                'fg': 'white',
                'text': '🟡 NEWS',
                'description': 'Bloqué par news'
            },
            'CONDITIONAL': {
                'bg': '#6B7280',      # Gris
                'fg': 'white',
                'text': '⚪ LIMITÉ',
                'description': 'Conditions limitées'
            },
            'ACTIVE': {
                'bg': '#10B981',      # Vert émeraude
                'fg': 'white',
                'text': '🟢 ACTIF',
                'description': 'Activité normale'
            },
            'BLOCKED': {
                'bg': '#DC2626',      # Rouge foncé
                'fg': 'white',
                'text': '🚫 BLOQUÉ',
                'description': 'Complètement bloqué'
            }
        }
    
    def create_badge(self, symbol, market_status, session_info=None, recommendations=None):
        """
        Crée un badge de statut pour un marché spécifique
        
        Args:
            symbol: Symbole du marché
            market_status: Statut du marché (OPEN, CLOSED, BLOCKED_BY_NEWS, etc.)
            session_info: Information de session (optionnel)
            recommendations: Liste de recommandations (optionnel)
        
        Returns:
            tk.Frame: Frame contenant le badge
        """
        # Supprimer le badge existant s'il y en a un
        if symbol in self.badges:
            self.badges[symbol].destroy()
        
        # Créer le frame principal du badge
        badge_frame = tk.Frame(self.parent_frame, relief=tk.RAISED, bd=1)
        
        # Obtenir la configuration de couleur
        # Par défaut utiliser OPEN si le statut n'est pas reconnu
        if market_status not in self.colors:
            market_status = 'OPEN'
        status_config = self.colors.get(market_status, self.colors['OPEN'])
        
        # Badge principal
        badge_label = tk.Label(
            badge_frame,
            text=status_config['text'],
            bg=status_config['bg'],
            fg=status_config['fg'],
            font=('Arial', 8, 'bold'),
            padx=4,
            pady=2
        )
        badge_label.pack(side=tk.LEFT)
        
        # Badge de session si disponible
        if session_info and session_info != 'UNKNOWN':
            session_badge = tk.Label(
                badge_frame,
                text=session_info[:3].upper(),  # Premiers 3 caractères
                bg='#4B5563',  # Gris foncé
                fg='white',
                font=('Arial', 7),
                padx=2,
                pady=1
            )
            session_badge.pack(side=tk.LEFT, padx=(1, 0))
        
        # Tooltip avec description
        self._create_tooltip(badge_frame, status_config['description'], recommendations)
        
        # Stocker le badge
        self.badges[symbol] = badge_frame
        
        return badge_frame
    
    def create_compact_badge(self, symbol, market_status, size='small'):
        """
        Crée un badge compact pour les espaces réduits
        
        Args:
            symbol: Symbole du marché
            market_status: Statut du marché
            size: Taille du badge ('small', 'tiny')
        
        Returns:
            tk.Label: Label du badge compact
        """
        # Supprimer le badge existant
        if symbol in self.badges:
            self.badges[symbol].destroy()
        
        # Configuration selon la taille
        if size == 'tiny':
            font_size = 6
            padx, pady = 2, 1
        else:  # small
            font_size = 7
            padx, pady = 3, 1
        
        status_config = self.colors.get(market_status, self.colors['OPEN'])
        
        badge = tk.Label(
            self.parent_frame,
            text=status_config['text'],
            bg=status_config['bg'],
            fg=status_config['fg'],
            font=('Arial', font_size, 'bold'),
            padx=padx,
            pady=pady,
            relief=tk.RAISED,
            bd=1
        )
        
        # Tooltip
        self._create_tooltip(badge, status_config['description'])
        
        self.badges[symbol] = badge
        return badge
    
    def create_status_indicator(self, symbol, market_status):
        """
        Crée un indicateur de statut simple (point coloré)
        
        Args:
            symbol: Symbole du marché
            market_status: Statut du marché
        
        Returns:
            tk.Frame: Frame avec indicateur
        """
        # Supprimer l'indicateur existant
        if symbol in self.badges:
            self.badges[symbol].destroy()
        
        indicator_frame = tk.Frame(self.parent_frame)
        
        status_config = self.colors.get(market_status, self.colors['OPEN'])
        
        # Point coloré
        indicator = tk.Canvas(
            indicator_frame,
            width=8,
            height=8,
            bg=status_config['bg'],
            highlightthickness=0
        )
        indicator.create_oval(2, 2, 6, 6, fill=status_config['bg'], outline='')
        indicator.pack(side=tk.LEFT)
        
        # Texte de statut
        status_text = tk.Label(
            indicator_frame,
            text=market_status.replace('_', ' '),
            fg=status_config['bg'],
            font=('Arial', 7),
            bg=self.parent_frame.cget('bg')
        )
        status_text.pack(side=tk.LEFT, padx=(2, 0))
        
        # Tooltip
        self._create_tooltip(indicator_frame, status_config['description'])
        
        self.badges[symbol] = indicator_frame
        return indicator_frame
    
    def _create_tooltip(self, widget, text, additional_info=None):
        """
        Crée un tooltip pour un widget
        
        Args:
            widget: Widget cible
            text: Texte principal du tooltip
            additional_info: Informations supplémentaires (optionnel)
        """
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            # Texte principal
            label = tk.Label(
                tooltip,
                text=text,
                background="#1F2937",
                foreground="white",
                font=('Arial', 9),
                relief=tk.SOLID,
                borderwidth=1,
                padx=5,
                pady=3
            )
            label.pack()
            
            # Informations supplémentaires si disponibles
            if additional_info and isinstance(additional_info, list):
                for info in additional_info[:3]:  # Top 3
                    info_label = tk.Label(
                        tooltip,
                        text=f"• {info}",
                        background="#1F2937",
                        foreground="#D1D5DB",
                        font=('Arial', 8),
                        relief=tk.SOLID,
                        borderwidth=1,
                        padx=5,
                        pady=1
                    )
                    info_label.pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def update_badge(self, symbol, market_status, session_info=None, recommendations=None):
        """
        Met à jour un badge existant
        
        Args:
            symbol: Symbole du marché
            market_status: Nouveau statut du marché
            session_info: Information de session (optionnel)
            recommendations: Nouvelles recommandations (optionnel)
        """
        if symbol in self.badges:
            self.badges[symbol].destroy()
        
        return self.create_badge(symbol, market_status, session_info, recommendations)
    
    def get_status_color(self, market_status):
        """
        Retourne la couleur associée à un statut
        
        Args:
            market_status: Statut du marché
        
        Returns:
            str: Code couleur hexadécimal
        """
        return self.colors.get(market_status, self.colors['OPEN'])['bg']
    
    def get_all_badges(self):
        """Retourne tous les badges créés"""
        return self.badges
    
    def clear_all_badges(self):
        """Supprime tous les badges"""
        for badge in self.badges.values():
            try:
                badge.destroy()
            except:
                pass
        self.badges.clear()
    
    def create_legend(self, parent_frame):
        """
        Crée une légende des statuts
        
        Args:
            parent_frame: Frame parent pour la légende
        
        Returns:
            tk.Frame: Frame de la légende
        """
        legend_frame = tk.Frame(parent_frame, relief=tk.GROOVE, bd=1)
        
        tk.Label(
            legend_frame,
            text="LÉGENDE:",
            font=('Arial', 9, 'bold'),
            bg=parent_frame.cget('bg')
        ).pack(padx=5, pady=2)
        
        for status, config in self.colors.items():
            item_frame = tk.Frame(legend_frame, bg=parent_frame.cget('bg'))
            
            # Indicateur coloré
            indicator = tk.Canvas(
                item_frame,
                width=10,
                height=10,
                bg=config['bg'],
                highlightthickness=0
            )
            indicator.create_oval(2, 2, 8, 8, fill=config['bg'], outline='')
            indicator.pack(side=tk.LEFT, padx=(5, 2))
            
            # Texte
            tk.Label(
                item_frame,
                text=config['text'],
                font=('Arial', 8),
                bg=parent_frame.cget('bg')
            ).pack(side=tk.LEFT)
            
            item_frame.pack(anchor=tk.W, padx=5)
        
        return legend_frame


# Fonctions utilitaires pour l'intégration rapide
def create_market_badge(parent, symbol, result):
    """
    Fonction utilitaire pour créer rapidement un badge de marché
    
    Args:
        parent: Widget parent
        symbol: Symbole du marché
        result: Résultat d'analyse avec informations de statut
    
    Returns:
        tk.Frame ou tk.Label: Badge créé
    """
    badge_manager = MarketStatusBadges(parent)
    
    market_status = result.get('market_status', 'OPEN')
    session_info = result.get('session_info', 'UNKNOWN')
    recommendations = result.get('recommendations', [])
    
    return badge_manager.create_badge(symbol, market_status, session_info, recommendations)


def get_market_status_text(market_status):
    """
    Retourne le texte formaté pour un statut de marché
    
    Args:
        market_status: Statut du marché
    
    Returns:
        str: Texte formaté
    """
    status_texts = {
        'OPEN_FOR_TRADING': '🟢 OUVERT AU TRADING',
        'BLOCKED_BY_NEWS': '🟡 BLOQUÉ PAR NEWS',
        'SESSION_CLOSED': '🔴 SESSION FERMÉE',
        'CONDITIONAL': '⚪ CONDITIONNEL',
        'ACTIVE': '🟢 ACTIF',
        'BLOCKED': '🚫 BLOQUÉ'
    }
    
    return status_texts.get(market_status, '❓ INCONNU')
