# 🤖 ADAM - Adaptive Deep Analysis Machine

**ADAM** est une intelligence artificielle d'analyse de marchés financiers avancée conçue pour aider les traders à **identifier rapidement les opportunités**, filtrer les marchés à risque et rester discipliné.

Développé par **GH05T** en l'honneur de sa mère **Adama** ❤️

---
## 🚀 Installation Rapide

```bash
# Activer l'environnement virtuel
source ghost_virtuel/Scripts/activate

# Lancer l'application
python -m app.master
```
---
Fin octobre (autour du 25 au 31 octobre)
Fin mars (autour du 14 au 28 mars)
Nous sommes le [date]. Je suis au Sénégal. Quels sont aujourd'hui les meilleurs horaires pour surveiller XAU/USD, GBP/USD et EUR/AUD ? ?

| Horaire            | Marchés                          |
| -----------        | -------------------------------- |
| **07h00 - 12h 00** | XAU/USD - GBP/USD - EUR/AUD      |
| **12h00 - 16h00**  | XAU/USD - GBP/USD                |
| **22h00 - 00h00**  | EUR/AUD                          |
| **00h00 - 07h00**  | EUR/AUD                          |

| Instrument  | Créneau principal au Sénégal           | Créneau secondaire |
| ----------- | -------------------------------------- | ------------------ |
| **XAU/USD** | 12h00 – 16h00                          | 07h00 – 12h00      |
| **GBP/USD** | 07h00 – 11h00                          | 12h00 – 16h00      |
| **EUR/AUD** | 22h00 – 00h00 et 00h00 – 07h00         | 07h00 – 09h00      |


## 🎯 Objectif

ADAM a été conçu pour le **day trading structurel** et le **swing trading** :

- Scanner **27+ marchés** automatiquement en temps réel (Forex, Gold, Crypto)
- Classer les marchés par **tendance** : Haussier, Baissier, Neutre
- Déterminer un **statut opérationnel** : Interdit, Surveillance, Autorisé, Opportunité
- Journaliser les opportunités détectées
- **Filtrer intelligent** pour ne présenter que les meilleurs setups
- Envoyer des signaux Telegram avec Trade Plans détaillés

## 📊 Les 9 Indicateurs Techniques

### Indicateurs Principaux
- **EMA** - Moyennes mobiles exponentielles adaptées par timeframe (M30: 9/21, H1: 21/50, H4: 50/200)
- **Super Trend** - Confirmation de tendance robuste basée sur ATR (période 10, multiplicateur 3)
- **RSI 14** - Relative Strength Index avec niveaux surachat/survente et divergences
- **Swings** - Structure de marché (Higher Highs/Lower Lows) selon théorie de Dow

### Indicateurs Avancés
- **Volume** - Validation de la force des signaux
- **Multi-timeframe** - Analyse simultanée sur M30, H1, H4
- **Volatilité (ATR)** - Filtrage pour éviter les marchés extrêmes
- **Pullback** - Détection des zones d'entrée optimales avec validation
- **Market Regime** - Classification du contexte (trending/range/volatile)

## ⚡ Fonctionnalités Avancées

### Système de Scoring Composite
- **Score de base (0-100)** : Direction (+30), Impulsion (+25), Pullback (+25), Pas d'exclusions (+20)
- **Score de confirmation (0-140+)** : Bougies, EMA, Structure, Super Trend
- **Score total** : Minimum 55 pour signal, 85+ pour Best Trade VIP

### Filtrage Intelligent
- **Statuts automatiques** : INTERDIT, SURVEILLANCE, AUTORISÉ, OPPORTUNITÉ
- **Filtrage VIP ultra-sélectif** : Seuls les signaux AUTORISÉ avec score ≥ 85
- **Exclusion des trade plans non disponibles** pour le canal VIP
- **Conversion pips normalisée** : -30 pips FOREX = -3000 pips XAU/BTC

### Telegram Multi-Canaux
- **Canaux configurables** : Forex, Gold, utilisateurs personnalisés, VIP
- **Messages structurés** : Symbole, Direction, Timeframe, Entry, SL, TP, RR, Score, Statut
- **Sessions de trading** : Messages d'ouverture/fermeture de session (Asia, London, New York)
- **Filtrage par symbole** : Chaque canal reçoit uniquement les symboles configurés

## 🔄 Workflow de Trading

1. **Récupération des données** - Connexion MetaTrader 5, 27+ symboles, 3 timeframes (M30, H1, H4)
2. **Calcul des indicateurs** - EMA, Super Trend, RSI, Swings, Volatilité, Pullback
3. **Détermination de direction** - EMA + Swings + RSI avec lissage EMA 9
4. **Détection de pullback** - Zone structurelle + validation price action
5. **Confirmation de tendance** - Score multi-niveaux (bougies, EMA, structure, Super Trend)
6. **Scoring composite** - Score de base + Score de confirmation (0-140+)
7. **Classification du statut** - INTERDIT, SURVEILLANCE, AUTORISÉ, OPPORTUNITÉ
8. **Génération de Trade Plan** - Entry, SL (-30 pips FOREX / -3000 pips XAU), TP dynamique, RR
9. **Envoi de signaux Telegram** - Formatage + Filtrage VIP + Routage par canal
10. **Vous décidez** - Analyse visuelle finale et exécution manuelle

## 📈 Timeframes

- **M30 (Rapide)** - Signaux rapides, EMA 9/21
- **H1 (Équilibré)** - Signaux équilibrés, EMA 21/50
- **H4 (Fiable)** - Signaux fiables, EMA 50/200

## 🕐 Sessions de Trading

- **Asia** : 00:00 - 08:00 UTC (Bonus +5 points)
- **London** : 08:00 - 12:00 UTC (Bonus +10 points)
- **New York** : 13:00 - 17:00 UTC (Bonus +8 points)
- **Overlap** : 12:00 - 13:00 UTC (Bonus +15 points)

## 📊 Performance Cible

- **Winrate** : 65-75% (vs 45-55% sans optimisations)
- **Trades/jour** : 4-8 (vs 2-4 sans optimisations)
- **Profit Factor** : 1.8-2.2 (vs 1.2 sans optimisations)

## 💻 Interface Utilisateur

### Header
- Titre : "ADAM - Adaptive Deep Analysis Machine"
- Horloge live en UTC
- Statut du système

### Cartes de Statut
- **INTERDIT** (Rouge) - Marchés à éviter
- **SURVEILLANCE** (Orange) - Marchés sous observation
- **AUTORISÉ** (Vert) - Marchés valides pour trading

### Liste des Marchés
- Symbole + Direction + Score
- Indicateur Best Trade (score ≥ 85)
- Bouton pour voir le Trade Plan détaillé

### Boutons d'Action
- 🔄 Analyser les marchés
- ⭐ Gérer les favoris
- 👥 Gérer les utilisateurs Telegram
- 📊 Voir les statistiques

## 📡 Messages Telegram

### Format Signal
```
🤖 ADAM — SIGNAL
━━━━━━━━━━━━━━━━━━
⚡ EURUSD | TREND | H1 (Équilibré)
📈 Direction : HAUSSIER
✅ Statut : AUTORISÉ
🎯 Entry : 1.0850
🛑 SL : 1.0820 (-30 pips)
💰 TP : 1.0910 (+60 pips)
⚖️ RR : 1:2.0
⭐ Score : 78/100
```

### Filtres VIP
- **Canal VIP** : Reçoit uniquement AUTORISÉ + Score ≥ 85 + Trade Plan disponible
- **Canaux standards** : Reçoivent AUTORISÉ + Score ≥ 55
- **Exclusions** : INTERDIT/SURVEILLANCE jamais envoyés au VIP

## ⚙️ Configuration

### Fichiers de Configuration
- `users_config.json` - Canaux Telegram, symboles, timeframes, statut enabled/disabled
- `favorites.py` - Marchés favoris, niveaux de priorité, marchés ciblés
- `optimization_config.py` - Paramètres indicateurs, seuils de scoring

### Personnalisation
- Scores adaptatifs par session
- Seuils de trading dynamiques
- Filtrage par corrélation pour éviter trades redondants
- Validation multi-critères avec score composite pondéré

---

**ADAM n'est pas un robot de trading.** Il vous fournit une analyse intelligente pour que vous preniez les meilleures décisions de trading manuel.

## 🧠 Philosophie

> *“Un bon trader ne cherche pas plus de trades,  
> il cherche de meilleurs trades.”*

ADAM agit comme un **filtre intelligent**, pas comme un signal aveugle.

Il est pensé pour :
- Le **day trading**
- Le **swing trading**
- Les traders qui veulent **survivre sur le long terme**

---

## 🛠️ Fonctionnalités Principales

- 📊 Analyse multi-marchés (27+ symboles)
- 🧭 Classification automatique des tendances
- 🚦 Système de statut (INTERDIT / SURVEILLANCE / AUTORISÉ / OPPORTUNITÉ)
- 🔔 Alertes Telegram en temps réel
- 📓 Journal des opportunités
- 📈 Statistiques globales
- 🖥️ Interface graphique moderne (Tkinter)
- 💎 Canal VIP ultra-filtré (score ≥ 85)
- � Multi-timeframe (M30, H1, H4)
- 🎯 Trade Plans dynamiques avec RR
- 🔄 Sessions de trading automatiques

---

## 🔗 Plateformes

- 📉 Analyse via **MetaTrader 5**
- 💼 Trading manuel possible sur **Exness** ou tout autre broker

👉 ADAM **n'exécute aucun ordre**.

---

## 🔐 Sécurité & Propriété intellectuelle

- Le logiciel est distribué sous forme **exécutable (EXE)**
- Le code source n’est **ni inclus ni accessible**
- Toute tentative de rétro-ingénierie est interdite

---

## ⚠️ Avertissement

ADAM est un **outil d'aide à la décision**.

- Il ne garantit aucun profit
- Le trading comporte des risques
- L’utilisateur reste **seul responsable** de ses décisions

---

## 📚 Documentation

- `ALGORITHME_ADAM.md` - Algorithme complet du bot
- `FORMULES_MATHEMATIQUES_ADAM.md` - Toutes les formules mathématiques

---

## 👤 Auteur

Développé par **GH05T**  
Projet indépendant – usage éducatif et personnel

**En l'honneur de ma mère Adama** ❤️

---

## 📌 Version

**Version actuelle : v1.0 – Stable**
