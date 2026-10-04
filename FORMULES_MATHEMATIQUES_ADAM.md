# 📐 FORMULES MATHÉMATIQUES D'ADAM
## Adaptive Deep Analysis Machine

---

## 📊 INDICATEURS TECHNIQUES

### 1. EMA (Exponential Moving Average)

**Formule générale :**
```
EMA_t = α × Prix_t + (1 - α) × EMA_{t-1}
```

**Où :**
- `α` (alpha) = 2 / (période + 1)
- `Prix_t` = Prix de clôture actuel
- `EMA_{t-1}` = EMA précédente

**Périodes selon timeframe :**
```
M30 : α₁ = 2/(9+1) = 0.2  → EMA_9
      α₂ = 2/(21+1) = 0.091 → EMA_21

H1  : α₁ = 2/(21+1) = 0.091 → EMA_21
      α₂ = 2/(50+1) = 0.039 → EMA_50

H4  : α₁ = 2/(50+1) = 0.039 → EMA_50
      α₂ = 2/(200+1) = 0.01 → EMA_200
```

**Détection de direction :**
```
Si Prix > EMA_rapide > EMA_lente → HAUSSIER
Si Prix < EMA_rapide < EMA_lente → BAISSIER
Sinon → NEUTRE
```

---

### 2. SUPER TREND

**True Range (TR) :**
```
TR = max(
    High_t - Low_t,
    |High_t - Close_{t-1}|,
    |Low_t - Close_{t-1}|
)
```

**Average True Range (ATR) :**
```
ATR = moyenne(TR sur n périodes)
n = 10 (période Super Trend)
```

**Bandes Super Trend :**
```
Upper_Band = (High_t + Low_t) / 2 + (m × ATR)
Lower_Band = (High_t + Low_t) / 2 - (m × ATR)

Où m = 3 (multiplicateur)
```

**Direction Super Trend :**
```
Si Close_t > Upper_Band_{t-1} → ST_Direction = +1 (HAUSSIER)
Si Close_t < Lower_Band_{t-1} → ST_Direction = -1 (BAISSIER)
Sinon → ST_Direction = ST_Direction_{t-1}
```

---

### 3. RSI (Relative Strength Index)

**Calcul du gain et de la perte :**
```
Gain_t = max(Close_t - Close_{t-1}, 0)
Perte_t = max(Close_{t-1} - Close_t, 0)

Moyenne_Gain = moyenne(Gain sur 14 périodes)
Moyenne_Perte = moyenne(Perte sur 14 périodes)
```

**Relative Strength (RS) :**
```
RS = Moyenne_Gain / Moyenne_Perte
```

**RSI :**
```
RSI = 100 - (100 / (1 + RS))
```

**Interprétation :**
```
RSI ≥ 70 → SURACHAT
RSI ≤ 30 → SURVENTE
RSI > 50 + tendance haussière → HAUSSIER_RSI
RSI < 50 + tendance baissière → BAISSIER_RSI
```

---

### 4. SWINGS (Structure de Marché)

**Détection des sommets (Highs) :**
```
High_i est un sommet si :
High_i = max(High_{i-lookback} ... High_{i+lookback})

Où lookback = 3
```

**Détection des creux (Lows) :**
```
Low_i est un creux si :
Low_i = min(Low_{i-lookback} ... Low_{i+lookback})
```

**Analyse de structure (Théorie de Dow) :**
```
Higher High (HH) : High_dernier > High_précédent
Higher Low (HL)  : Low_dernier > Low_précédent
Lower High (LH)  : High_dernier < High_précédent
Lower Low (LL)   : Low_dernier < Low_précédent
```

**Tendance :**
```
Si HH ∧ HL → Tendance HAUSSIÈRE
Si LH ∧ LL → Tendance BAISSIÈRE
Si HH → HAUSSIER
Si LL → BAISSIER
Sinon → NEUTRE
```

---

### 5. VOLATILITÉ (ATR)

**True Range (TR) :**
```
TR_t = max(
    High_t - Low_t,
    |High_t - Close_{t-1}|,
    |Low_t - Close_{t-1}|
)
```

**Average True Range (ATR) :**
```
ATR = moyenne(TR sur 14 périodes)
```

**Ratio de volatilité :**
```
Ratio = Volatilité_Récente / Volatilité_Moyenne

Où :
Volatilité_Récente = moyenne(High - Low sur 20 dernières périodes)
Volatilité_Moyenne = moyenne(High - Low sur toutes les périodes)
```

---

### 6. PULLBACK

**Zone de pullback :**
```
Si direction = HAUSSIER :
  Zone_Low = min(Low_{-2}, Low_{-1})
  Zone_High = max(Low_{-2}, Low_{-1})

Si direction = BAISSIER :
  Zone_Low = min(High_{-2}, High_{-1})
  Zone_High = max(High_{-2}, High_{-1})
```

**Détection de pullback actif :**
```
Prix_actuel ∈ [Zone_Low - tolérance, Zone_High + tolérance]

Où tolérance = 10 × pip
pip = 0.0001 (Forex standard)
pip = 0.01 (JPY)
pip = 0.1 (XAU/GOLD/BTC)
```

**Validation du rejet (Price Action) :**
```
Pour direction HAUSSIER :
  Si Close_t > Close_{t-1} ∧ Close_{t-1} ≤ Close_{t-2}
  → Rejet haussier validé

Pour direction BAISSIER :
  Si Close_t < Close_{t-1} ∧ Close_{t-1} ≥ Close_{t-2}
  → Rejet baissier validé
```

---

### 7. MARKET REGIME (Range Detection)

**Test de range :**
```
Range = (max(Highs_derniers_3) - min(Highs_derniers_3) < tolérance)
     ∧ (max(Lows_derniers_3) - min(Lows_derniers_3) < tolérance)

Où tolérance = 0.002% du prix
```

---

## 🎯 SYSTÈME DE SCORING

### Score de Base (0-100)

```
Score_Base = 0

+30 si Direction ∈ {HAUSSIER, BAISSIER}
+25 si Impulsion_Récente = True
+25 si Pullback_Propre = True
+20 si Exclusions = ∅

Score_Base_Max = 100
```

### Score de Confirmation (0-140+)

**Taille des bougies :**
```
Body_i = |Close_i - Open_i|
ATR_14 = moyenne(High - Low sur 14 périodes)

Grande bougie : Body ≥ 1.2 × ATR
Moyenne bougie : Body ≥ 0.5 × ATR
Petite bougie : Body ≥ 0.3 × ATR
```

**Scoring pour direction HAUSSIÈRE :**
```
Score_Confirmation = 0

+40 si (Bougie_0 verte ∧ Body_0 ≥ 1.2×ATR)
+30 si (Bougie_0 verte ∧ Bougie_1 verte ∧ Body_0,1 ≥ 0.5×ATR)
+20 si (Bougie_0,1,2 vertes ∧ Body_0,1,2 ≥ 0.3×ATR)
+25 si Prix > EMA_9
+20 si (HH ∧ HL)
+15 si Super_Trend = +1
```

**Scoring pour direction BAISSIÈRE :**
```
Score_Confirmation = 0

+40 si (Bougie_0 rouge ∧ Body_0 ≥ 1.2×ATR)
+30 si (Bougie_0 rouge ∧ Bougie_1 rouge ∧ Body_0,1 ≥ 0.5×ATR)
+20 si (Bougie_0,1,2 rouges ∧ Body_0,1,2 ≥ 0.3×ATR)
+25 si Prix < EMA_9
+20 si (LH ∧ LL)
+15 si Super_Trend = -1
```

**Validation du signal :**
```
Signal_Confirmé = (Score_Confirmation ≥ 55)
                ∧ (Signal_Bougies ∨ Signal_EMA)

Où :
Signal_Bougies = (Grande_bougie ∨ 2_bougies_moyennes ∨ 3_petites_bougies)
Signal_EMA = (Prix > EMA_9 pour HAUSSIER ∨ Prix < EMA_9 pour BAISSIER)
```

### Score Total

```
Score_Total = Score_Base + Score_Confirmation

Minimum pour signal : 55
Best Trade (VIP) : Score_Base ≥ 85
```

---

## 📈 GÉNÉRATION DE TRADE PLAN

### Entry

```
Si Pullback_Actif ∧ Zone_Valide :
  Entry = Moyenne(Zone_Low, Zone_High)
Sinon :
  Entry = Prix_Actuel
```

### Stop Loss (SL)

**Forex Standard :**
```
SL = Entry - (30 × 0.0001)  pour HAUSSIER
SL = Entry + (30 × 0.0001)  pour BAISSIER
```

**JPY :**
```
SL = Entry - (30 × 0.01)  pour HAUSSIER
SL = Entry + (30 × 0.01)  pour BAISSIER
```

**XAU/GOLD/BTC (Norme Fixe) :**
```
SL = Entry - 300.0  pour HAUSSIER (3000 pips)
SL = Entry + 300.0  pour BAISSIER (3000 pips)
```

### Take Profit (TP)

**Calcul ATR :**
```
ATR = moyenne(High - Low sur 14 périodes)
```

**Multiplicateur selon contexte :**
```
Si (Trend_Continuation ∧ Impulsion > 1.5) :
  Multiplicateur = 2.0
Sinon si Impulsion > 1.2 :
  Multiplicateur = 1.5
Sinon si Pullback_Actif :
  Multiplicateur = 1.2
Sinon :
  Multiplicateur = 0.8
```

**TP brut :**
```
TP_brut = ATR × Multiplicateur
```

**Limites dynamiques par symbole :**

**JPY :**
```
TP = max(0.8 × ATR, min(3.0 × ATR, TP_brut))
```

**XAU/GOLD :**
```
XAUAUD : TP = max(1.0 × ATR, min(4.0 × ATR, TP_brut))
XAUGBP : TP = max(1.2 × ATR, min(3.5 × ATR, TP_brut))
XAUCHF : TP = max(1.5 × ATR, min(3.0 × ATR, TP_brut))
XAUUSD : TP = max(1.5 × ATR, min(3.0 × ATR, TP_brut))
```

**Autres paires :**
```
TP = max(0.8 × ATR, min(2.5 × ATR, TP_brut))
```

**TP final :**
```
TP = Entry + TP_brut  pour HAUSSIER
TP = Entry - TP_brut  pour BAISSIER
```

### Risk/Reward (RR)

```
RR = |TP - Entry| / |SL - Entry|
```

### Score Composite (Pondéré)

```
Score_Composite = (0.40 × Score_Base)
                + (0.20 × Score_MultiTimeframe)
                + (0.15 × Score_Volume)
                + (0.10 × Score_RSI)
                + (0.10 × Score_ML_Prediction)
                + (0.05 × Score_Time_Optimization)
```

---

## 🔄 CONVERSION PIPS

### Forex Standard
```
1 pip = 0.0001
Distance_pips = |Prix_1 - Prix_2| / 0.0001
```

### JPY
```
1 pip = 0.01
Distance_pips = |Prix_1 - Prix_2| / 0.01
```

### XAU/GOLD/BTC (Norme Fixe)
```
1 pip = 0.1
Distance_pips = |Prix_1 - Prix_2| / 0.1

Conversion FOREX :
Pips_FOREX = Pips_XAU / 100

Exemple :
3000 pips XAU = 30 pips FOREX
```

---

## 📊 STATISTIQUES

### Winrate
```
Winrate = (Nombre_Trades_Gagnants / Nombre_Trades_Totaux) × 100
```

### Profit Factor
```
Profit_Factor = Somme_Gains / Somme_Pertes
```

### Moyenne Gain/Perte
```
Moyenne_Gain = Somme_Gains / Nombre_Trades_Gagnants
Moyenne_Perte = Somme_Pertes / Nombre_Trades_Perdants
```

### Score de Session (Bonus)
```
Bonus_ASIA = +5
Bonus_LONDON = +10
Bonus_NEW_YORK = +8
Bonus_OVERLAP = +15
```

---

## 🧮 FIBONACCI

**Niveaux de retracement :**
```
0.236, 0.382, 0.447, 0.500, 0.618, 0.786, 0.886
```

**Niveaux d'extension :**
```
1.272, 1.414, 1.618, 2.000, 2.618
```

**Calcul des niveaux :**
```
Niveau_Retracement = Swing_High - (Ratio × (Swing_High - Swing_Low))
Niveau_Extension = Swing_Low + (Ratio × (Swing_High - Swing_Low))
```

---

## 🔢 FORMULES DE Lissage

### Lissage par EMA 9
```
EMA_9 = α × Prix + (1 - α) × EMA_9_précédent
Où α = 2/(9+1) = 0.2
```

### Lissage par Moyenne Mobile
```
MA_n = moyenne(Prix sur n périodes)
```

---

## 📐 CALCULS DE POSITION

### Taille de position (Risk Management)
```
Taille_Position = (Capital × Risk_Percent) / |SL - Entry|

Où :
Capital = Capital total du compte
Risk_Percent = 0.01 (1% de risque par trade)
```

### Valeur du pip
```
Valeur_Pip = Taille_Position × Taille_Contrat × Valeur_Pip_Standard

Où :
Taille_Contrat = 100000 pour Forex standard
Valeur_Pip_Standard = 0.0001
```

---

## 🎲 PROBABILITÉS

### Probabilité de succès (Score)
```
P_Succès = Score / 100

Si Score ≥ 85 : P_Succès ≥ 85%
Si Score ≥ 70 : P_Succès ≥ 70%
Si Score ≥ 55 : P_Succès ≥ 55%
```

### Espérance mathématique
```
E = (P_Gain × Gain_Moyen) - (P_Perte × Perte_Moyenne)

Où :
P_Gain = Winrate / 100
P_Perte = 1 - P_Gain
```

---

## 📈 INDICATEURS AVANCÉS

### Momentum
```
Momentum_t = Prix_t - Prix_{t-n}

Où n = période (ex: 14)
```

### Rate of Change (ROC)
```
ROC_t = ((Prix_t - Prix_{t-n}) / Prix_{t-n}) × 100
```

### MACD (Moving Average Convergence Divergence)
```
MACD_Ligne = EMA_12 - EMA_26
Signal_Ligne = EMA_9(MACD_Ligne)
Histogramme = MACD_Ligne - Signal_Ligne
```

---

## 🔍 FILTRES

### Corrélation entre paires
```
Corrélation = Covariance(X, Y) / (σ_X × σ_Y)

Où :
Covariance(X, Y) = moyenne((X - μ_X) × (Y - μ_Y))
σ_X = écart_type(X)
σ_Y = écart_type(Y)
```

### Distance de marché
```
Distance = √(Σ(Prix_i - Prix_j)²)

Où i et j sont deux paires différentes
```

---

*Ce document contient toutes les formules mathématiques utilisées dans ADAM.*
