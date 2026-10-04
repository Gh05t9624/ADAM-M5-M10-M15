from app.engine.cache import get_cached, set_cache
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta

SYMBOLS = [
    "EURUSD", "GBPUSD", "USDJPY", "XAUUSD",
    "AUDUSD", "USDCAD", "USDCHF",
    "NAS100", "SP500", "GER40", "BTCUSD"
]

class DataProvider:
    def __init__(self):
        self.mt5_connected = False
        self._connect_mt5()
    
    def _connect_mt5(self):
        """Connexion à MT5"""
        try:
            print("🔍 [MT5] Tentative de connexion...")
            if mt5.initialize():
                self.mt5_connected = True
                print("✅ MT5 connecté pour DataProvider")
                
                # Vérifier les symboles disponibles
                symbols = mt5.symbols_get()
                if symbols:
                    btc_available = any("BTCUSD" in s.name for s in symbols)
                    print(f"📊 [MT5] {len(symbols)} symboles disponibles, BTCUSD: {'✅' if btc_available else '❌'}")
                    
                    if btc_available:
                        btc_symbols = [s.name for s in symbols if "BTC" in s.name]
                        print(f"🔍 [MT5] Symboles BTC trouvés: {btc_symbols}")
                else:
                    print("⚠️ [MT5] Aucun symbole disponible")
                
                return True
            else:
                print("❌ Échec connexion MT5 pour DataProvider")
                return False
        except Exception as e:
            print(f"❌ Erreur connexion MT5: {e}")
            return False
    
    def get_markets(self):
        return [
            "EURUSD",
            "GBPUSD", 
            "USDJPY",
            "XAUUSD",
            "BTCUSD",
            "ETHUSD",
        ]
    
    def get_candles(self, symbol, timeframe=None, count=500):
        """Récupère les bougies depuis MT5 uniquement - PAS DE DONNÉES FICTIVES"""
        if not self.mt5_connected:
            print(f"❌ MT5 non connecté - impossible de récupérer {symbol}")
            return None
        
        # Vérifier le cache d'abord
        cache_key = f"{symbol}_{timeframe}_{count}"
        cached = get_cached(cache_key)
        if cached is not None:
            return cached
        
        try:
            # Déterminer le timeframe
            if timeframe is None:
                mt5_timeframe = mt5.TIMEFRAME_M5
            elif timeframe == mt5.TIMEFRAME_M30:
                mt5_timeframe = mt5.TIMEFRAME_M30
            elif timeframe == mt5.TIMEFRAME_M5:
                mt5_timeframe = mt5.TIMEFRAME_M5
            elif timeframe == mt5.TIMEFRAME_M10:
                mt5_timeframe = mt5.TIMEFRAME_M10
            else:
                mt5_timeframe = mt5.TIMEFRAME_M5
            
            # Récupérer les bougies depuis MT5
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            
            if rates is not None and len(rates) > 0:
                df = pd.DataFrame(rates)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                
                # Mettre en cache
                set_cache(cache_key, df)
                
                # Logging pour tous les symboles
                print(f"📊 [MT5] {symbol}: {len(df)} bougies récupérées")
                
                return df
            else:
                print(f"❌ [MT5] {symbol}: Aucune donnée disponible")
                return None
                
        except Exception as e:
            print(f"❌ [MT5 ERROR] {symbol}: {e}")
            return None

def get_symbols():
    return SYMBOLS

def get_candles(symbol):
    """Fonction legacy pour compatibilité"""
    provider = DataProvider()
    return provider.get_candles(symbol)
