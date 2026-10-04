# app/data/provider.py

import pandas as pd
import MetaTrader5 as mt5

class DataProvider:
    """
    Fournisseur de données marché MT5 - DONNÉES RÉELLES UNIQUEMENT
    Plus aucune donnée fictive
    """
    
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

    def get_all_markets(self):
        """Récupère tous les marchés depuis MT5 uniquement"""
        if not self.mt5_connected:
            print("❌ MT5 non connecté - impossible de récupérer les marchés")
            return {}
        
        symbols = [
            "EURUSD", "GBPUSD", "USDJPY", "XAUUSD",
            "AUDUSD", "USDCAD", "USDCHF", "BTCUSD"
        ]
        
        data = {}
        for symbol in symbols:
            try:
                df = self._get_candles_mt5(symbol)
                if df is not None:
                    data[symbol] = df
                    print(f"📊 [MT5] {symbol}: {len(df)} bougies récupérées")
                else:
                    print(f"❌ [MT5] {symbol}: Aucune donnée disponible")
            except Exception as e:
                print(f"❌ [MT5 ERROR] {symbol}: {e}")
        
        print(f"📊 [MARKETS] {len(data)} marchés récupérés: {list(data.keys())}")
        return data
    
    def _get_candles_mt5(self, symbol, count=500):
        """Récupère les bougies depuis MT5"""
        try:
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, count)
            
            if rates is not None and len(rates) > 0:
                df = pd.DataFrame(rates)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                return df
            else:
                return None
                
        except Exception as e:
            print(f"❌ Erreur MT5 pour {symbol}: {e}")
            return None
