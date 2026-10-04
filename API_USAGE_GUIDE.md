# Guide d'Utilisation de l'API ADAM

**Version**: 1.0.0  
**Date**: 22 Juin 2026  
**Base URL**: `http://localhost:8000`

---

## 📋 Table des Matières

1. [Installation](#installation)
2. [Démarrage](#démarrage)
3. [Documentation Interactive](#documentation-interactive)
4. [Endpoints](#endpoints)
5. [Modèles de Données](#modèles-de-données)
6. [Exemples de Requêtes](#exemples-de-requêtes)
7. [Intégration Flutter](#intégration-flutter)
8. [Gestion des Erreurs](#gestion-des-erreurs)
9. [WebSocket (Futur)](#websocket-futur)

---

## 🚀 Installation

### Prérequis

- Python 3.8+
- pip (gestionnaire de paquets Python)

### Installation des Dépendances

```bash
# Activer l'environnement virtuel
source ghost_virtuel/Scripts/activate

# Installer les dépendances FastAPI
pip install fastapi uvicorn pydantic
```

---

## 🎯 Démarrage

### Lancer le Serveur

```bash
# Option 1: Avec uvicorn directement
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

# Option 2: Avec le module Python
python -m app.api.main
```

### Vérifier le Statut

```bash
# Endpoint racine
curl http://localhost:8000/

# Health check
curl http://localhost:8000/health
```

**Réponse attendue**:
```json
{
  "status": "healthy",
  "service": "ADAM API",
  "version": "1.0.0"
}
```

---

## 📚 Documentation Interactive

L'API ADAM inclut une documentation interactive automatique générée par FastAPI.

### Swagger UI (Recommandé)

**URL**: `http://localhost:8000/docs`

- Interface interactive pour tester les endpoints
- Documentation complète des paramètres
- Exemples de requêtes/réponses
- Bouton "Try it out" pour tester directement

### ReDoc

**URL**: `http://localhost:8000/redoc`

- Documentation alternative avec un design différent
- Plus adaptée pour la lecture et la référence

---

## 🔌 Endpoints

### Structure Actuelle

> **Note**: Les endpoints sont préparés mais pas encore implémentés. La structure est prête pour l'implémentation future.

### Endpoints Planifiés

#### 1. Liste des Marchés
```
GET /api/markets
```

**Description**: Retourne la liste des marchés disponibles.

**Réponse**:
```json
{
  "markets": ["EURUSD", "GBPUSD", "XAUUSD", ...],
  "count": 27,
  "timestamp": "2026-06-22T23:20:00.000Z"
}
```

#### 2. Analyse d'un Marché
```
GET /api/markets/{symbol}?timeframe=H4
```

**Paramètres**:
- `symbol` (string, requis): Symbole du marché (ex: EURUSD)
- `timeframe` (string, optionnel): Timeframe d'analyse (M30, H1, H4) - défaut: H4

**Réponse**:
```json
{
  "symbol": "EURUSD",
  "timeframe": "H4",
  "statut": "AUTORISÉ",
  "direction": "HAUSSIER",
  "score": 78,
  "confidence": 0.85,
  "has_impulse": true,
  "impulse_strength": 1.8,
  "pullback_ok": true,
  "trend_continuation": true,
  "ema_dir": "HAUSSIER",
  "st_dir": "HAUSSIER",
  "rsi_dir": "HAUSSIER",
  "zone": {
    "low": 1.0850,
    "high": 1.0920
  },
  "exclusions": [],
  "confirmed": true,
  "timestamp": "2026-06-22T23:20:00.000Z"
}
```

#### 3. Générer un Plan de Trade
```
POST /api/markets/{symbol}/trade-plan
```

**Corps de la requête**:
```json
{
  "symbol": "EURUSD",
  "direction": "HAUSSIER",
  "score": 78,
  "trend_continuation": true,
  "pullback_active": true,
  "has_impulse": true,
  "min_score": 55
}
```

**Réponse**:
```json
{
  "symbol": "EURUSD",
  "type": "TREND_CONTINUATION",
  "direction": "HAUSSIER",
  "entry": 1.0875,
  "sl": 1.0845,
  "tp": 1.0945,
  "rr": 2.33,
  "score": 85,
  "timestamp": "2026-06-22T23:20:00.000Z"
}
```

---

## 📊 Modèles de Données

### MarketAnalysisRequest

```python
{
  "symbol": str,        # Symbole du marché (ex: "EURUSD")
  "timeframe": str,    # Timeframe (M30, H1, H4)
  "context": dict      # Contexte optionnel
}
```

### MarketAnalysisResponse

```python
{
  "symbol": str,              # Symbole du marché
  "timeframe": str,           # Timeframe d'analyse
  "statut": str,              # AUTORISÉ, SURVEILLANCE, INTERDIT
  "direction": str,           # HAUSSIER, BAISSIER, NEUTRE
  "score": int,              # Score 0-100
  "confidence": float,        # Confiance 0-1
  "has_impulse": bool,       # Présence d'impulsion
  "impulse_strength": float,  # Force de l'impulsion
  "pullback_ok": bool,       # Pullback validé
  "trend_continuation": bool,# Continuation de tendance
  "ema_dir": str,            # Direction EMA
  "st_dir": str,             # Direction SuperTrend
  "rsi_dir": str,            # Direction RSI
  "zone": {                  # Zone de prix
    "low": float,
    "high": float
  },
  "exclusions": list,        # Liste des exclusions
  "confirmed": bool,         # Confirmation du signal
  "timestamp": datetime      # Horodatage
}
```

### TradePlanRequest

```python
{
  "symbol": str,              # Symbole du marché
  "direction": str,          # HAUSSIER, BAISSIER
  "score": int,              # Score de l'analyse
  "trend_continuation": bool,# Continuation de tendance
  "pullback_active": bool,   # Pullback actif
  "has_impulse": bool,       # Présence d'impulsion
  "min_score": int           # Score minimum
}
```

### TradePlanResponse

```python
{
  "symbol": str,       # Symbole du marché
  "type": str,         # Type de plan
  "direction": str,    # Direction du trade
  "entry": float,      # Prix d'entrée
  "sl": float,         # Stop Loss
  "tp": float,         # Take Profit
  "rr": float,         # Risk/Reward ratio
  "score": int,        # Score du plan
  "timestamp": datetime # Horodatage
}
```

---

## 💻 Exemples de Requêtes

### Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Obtenir la liste des marchés
response = requests.get(f"{BASE_URL}/api/markets")
markets = response.json()
print(f"Marchés disponibles: {markets['count']}")

# 2. Analyser un marché
symbol = "EURUSD"
response = requests.get(f"{BASE_URL}/api/markets/{symbol}?timeframe=H4")
analysis = response.json()
print(f"Direction: {analysis['direction']}")
print(f"Score: {analysis['score']}")
print(f"Statut: {analysis['statut']}")

# 3. Générer un plan de trade
trade_request = {
    "symbol": symbol,
    "direction": analysis['direction'],
    "score": analysis['score'],
    "trend_continuation": analysis['trend_continuation'],
    "pullback_active": analysis['pullback_ok'],
    "has_impulse": analysis['has_impulse'],
    "min_score": 55
}
response = requests.post(f"{BASE_URL}/api/markets/{symbol}/trade-plan", json=trade_request)
trade_plan = response.json()
print(f"Entry: {trade_plan['entry']}")
print(f"SL: {trade_plan['sl']}")
print(f"TP: {trade_plan['tp']}")
print(f"R/R: {trade_plan['rr']}")
```

### cURL

```bash
# 1. Liste des marchés
curl http://localhost:8000/api/markets

# 2. Analyse d'un marché
curl "http://localhost:8000/api/markets/EURUSD?timeframe=H4"

# 3. Générer un plan de trade
curl -X POST http://localhost:8000/api/markets/EURUSD/trade-plan \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "EURUSD",
    "direction": "HAUSSIER",
    "score": 78,
    "trend_continuation": true,
    "pullback_active": true,
    "has_impulse": true,
    "min_score": 55
  }'
```

### JavaScript (fetch)

```javascript
const BASE_URL = "http://localhost:8000";

// 1. Obtenir la liste des marchés
async function getMarkets() {
  const response = await fetch(`${BASE_URL}/api/markets`);
  const markets = await response.json();
  console.log(`Marchés disponibles: ${markets.count}`);
  return markets;
}

// 2. Analyser un marché
async function analyzeMarket(symbol, timeframe = "H4") {
  const response = await fetch(`${BASE_URL}/api/markets/${symbol}?timeframe=${timeframe}`);
  const analysis = await response.json();
  console.log(`Direction: ${analysis.direction}`);
  console.log(`Score: ${analysis.score}`);
  console.log(`Statut: ${analysis.statut}`);
  return analysis;
}

// 3. Générer un plan de trade
async function generateTradePlan(symbol, analysis) {
  const tradeRequest = {
    symbol: symbol,
    direction: analysis.direction,
    score: analysis.score,
    trend_continuation: analysis.trend_continuation,
    pullback_active: analysis.pullback_ok,
    has_impulse: analysis.has_impulse,
    min_score: 55
  };
  
  const response = await fetch(`${BASE_URL}/api/markets/${symbol}/trade-plan`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(tradeRequest)
  });
  
  const tradePlan = await response.json();
  console.log(`Entry: ${tradePlan.entry}`);
  console.log(`SL: ${tradePlan.sl}`);
  console.log(`TP: ${tradePlan.tp}`);
  console.log(`R/R: ${tradePlan.rr}`);
  return tradePlan;
}

// Utilisation
(async () => {
  const markets = await getMarkets();
  const analysis = await analyzeMarket("EURUSD");
  const tradePlan = await generateTradePlan("EURUSD", analysis);
})();
```

---

## 📱 Intégration Flutter

### Installation des Dépendances

Ajouter à `pubspec.yaml`:

```yaml
dependencies:
  http: ^1.1.0
  web_socket_channel: ^2.4.0
```

### Service API Flutter

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class AdamApiService {
  final String baseUrl = 'http://localhost:8000';

  // Obtenir la liste des marchés
  Future<List<String>> getMarkets() async {
    final response = await http.get(Uri.parse('$baseUrl/api/markets'));
    
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return List<String>.from(data['markets']);
    } else {
      throw Exception('Failed to load markets');
    }
  }

  // Analyser un marché
  Future<Map<String, dynamic>> analyzeMarket(String symbol, String timeframe) async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/markets/$symbol?timeframe=$timeframe'),
    );
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to analyze market');
    }
  }

  // Générer un plan de trade
  Future<Map<String, dynamic>> generateTradePlan(
    String symbol,
    Map<String, dynamic> analysis,
  ) async {
    final tradeRequest = {
      'symbol': symbol,
      'direction': analysis['direction'],
      'score': analysis['score'],
      'trend_continuation': analysis['trend_continuation'],
      'pullback_active': analysis['pullback_ok'],
      'has_impulse': analysis['has_impulse'],
      'min_score': 55,
    };

    final response = await http.post(
      Uri.parse('$baseUrl/api/markets/$symbol/trade-plan'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(tradeRequest),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to generate trade plan');
    }
  }
}
```

### Utilisation dans Flutter

```dart
import 'package:flutter/material.dart';
import 'adam_api_service.dart';

class MarketAnalysisScreen extends StatefulWidget {
  @override
  _MarketAnalysisScreenState createState() => _MarketAnalysisScreenState();
}

class _MarketAnalysisScreenState extends State<MarketAnalysisScreen> {
  final AdamApiService _apiService = AdamApiService();
  List<String> _markets = [];
  Map<String, dynamic>? _currentAnalysis;

  @override
  void initState() {
    super.initState();
    _loadMarkets();
  }

  Future<void> _loadMarkets() async {
    try {
      final markets = await _apiService.getMarkets();
      setState(() {
        _markets = markets;
      });
    } catch (e) {
      print('Error loading markets: $e');
    }
  }

  Future<void> _analyzeMarket(String symbol) async {
    try {
      final analysis = await _apiService.analyzeMarket(symbol, 'H4');
      setState(() {
        _currentAnalysis = analysis;
      });
    } catch (e) {
      print('Error analyzing market: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('ADAM API')),
      body: Column(
        children: [
          // Liste des marchés
          Expanded(
            child: ListView.builder(
              itemCount: _markets.length,
              itemBuilder: (context, index) {
                final symbol = _markets[index];
                return ListTile(
                  title: Text(symbol),
                  onTap: () => _analyzeMarket(symbol),
                );
              },
            ),
          ),
          // Analyse courante
          if (_currentAnalysis != null)
            Container(
              padding: EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Direction: ${_currentAnalysis!['direction']}'),
                  Text('Score: ${_currentAnalysis!['score']}'),
                  Text('Statut: ${_currentAnalysis!['statut']}'),
                ],
              ),
            ),
        ],
      ),
    );
  }
}
```

---

## ⚠️ Gestion des Erreurs

### Codes d'Erreur

| Code | Description |
|------|-------------|
| 200 | Succès |
| 400 | Requête invalide |
| 404 | Ressource non trouvée |
| 500 | Erreur serveur interne |

### Format de Réponse d'Erreur

```json
{
  "error": "Message d'erreur",
  "detail": "Détails supplémentaires",
  "timestamp": "2026-06-22T23:20:00.000Z"
}
```

### Exemple de Gestion d'Erreur (Python)

```python
import requests

try:
    response = requests.get("http://localhost:8000/api/markets/INVALID")
    response.raise_for_status()
    data = response.json()
except requests.exceptions.HTTPError as e:
    error_data = response.json()
    print(f"Erreur: {error_data['error']}")
    print(f"Détail: {error_data['detail']}")
except requests.exceptions.ConnectionError:
    print("Impossible de se connecter au serveur")
except requests.exceptions.Timeout:
    print("Délai d'attente dépassé")
except requests.exceptions.RequestException as e:
    print(f"Erreur de requête: {e}")
```

---

## 🔌 WebSocket (Futur)

### Structure Préparée

L'API est préparée pour supporter les connexions WebSocket pour les mises à jour en temps réel.

### Endpoint WebSocket Planifié

```
ws://localhost:8000/ws/stream
```

### Exemple d'Implémentation Future (Python)

```python
import asyncio
import websockets

async def stream_market_updates():
    uri = "ws://localhost:8000/ws/stream"
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            market_data = json.loads(data)
            print(f"Mise à jour: {market_data['symbol']} - Score: {market_data['result']['score']}")

# Lancer
asyncio.run(stream_market_updates())
```

### Exemple d'Implémentation Future (Flutter)

```dart
import 'package:web_socket_channel/web_socket_channel.dart';

class MarketStreamService {
  final String wsUrl = 'ws://localhost:8000/ws/stream';
  WebSocketChannel? _channel;
  final _marketController = StreamController<Map<String, dynamic>>();

  Stream<Map<String, dynamic>> get marketStream => _marketController.stream;

  void connect() {
    _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
    _channel!.stream.listen(
      (data) {
        final marketData = json.decode(data);
        _marketController.add(marketData);
      },
      onError: (error) {
        print('WebSocket error: $error');
      },
    );
  }

  void disconnect() {
    _channel?.sink.close();
  }

  void dispose() {
    _marketController.close();
    disconnect();
  }
}
```

---

## 🔒 Sécurité (Futur)

### Configuration CORS

Le CORS est actuellement configuré pour accepter toutes les origines (`allow_origins=["*"]`). Pour la production, configurez les origines autorisées:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Origines spécifiques
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Authentification (Futur)

Pour ajouter l'authentification, utilisez FastAPI Security:

```python
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == "your-secret-api-key":
        return api_key_header
    raise HTTPException(status_code=403, detail="Invalid API Key")

# Utiliser dans les endpoints
@app.get("/api/markets", dependencies=[Depends(get_api_key)])
async def get_markets():
    ...
```

---

## 📊 Monitoring (Futur)

### Logs

Les logs sont configurés au niveau INFO. Pour le développement, utilisez:

```bash
uvicorn app.api.main:app --log-level debug
```

### Metrics (Futur)

Pour ajouter des métriques, utilisez Prometheus:

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

---

## 🎯 Bonnes Pratiques

### 1. Gestion des Timeouts

```python
response = requests.get(url, timeout=10)  # 10 secondes
```

### 2. Retry Logic

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
```

### 3. Cache (Futur)

Pour réduire la charge, implémentez un cache:

```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

FastAPICache.init(RedisBackend(redis_client))
```

---

## 📞 Support

Pour toute question ou problème, consultez:
- Documentation Swagger: `http://localhost:8000/docs`
- Rapport de préparation: `API_PREPARATION_REPORT.md`
- Code source: `app/api/`

---

**Version**: 1.0.0  
**Dernière mise à jour**: 22 Juin 2026
