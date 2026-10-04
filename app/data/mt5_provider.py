import MetaTrader5 as mt5
import pandas as pd
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MT5Provider:

    def __init__(self):
        self.is_connected = False
        self.connection_attempts = 0
        self.max_attempts = 3
        
        try:
            self.is_connected = mt5.initialize()
            if not self.is_connected:
                logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                raise RuntimeError(f"MT5 non initialisé: {mt5.last_error()}")
            else:
                logger.info("MT5 initialized successfully")
        except Exception as e:
            logger.error(f"Exception during MT5 initialization: {e}")
            raise RuntimeError(f"Erreur lors de l'initialisation MT5: {e}")

    def __del__(self):
        if self.is_connected:
            try:
                mt5.shutdown()
                logger.info("MT5 shutdown completed")
            except Exception as e:
                logger.error(f"Error during MT5 shutdown: {e}")

    def _check_connection(self):
        """Vérifie et tente de rétablir la connexion si nécessaire"""
        if not self.is_connected:
            if self.connection_attempts < self.max_attempts:
                self.connection_attempts += 1
                logger.info(f"Attempting to reconnect to MT5 (attempt {self.connection_attempts})")
                self.is_connected = mt5.initialize()
                if self.is_connected:
                    logger.info("MT5 reconnection successful")
                    self.connection_attempts = 0
                    return True
                else:
                    logger.error(f"MT5 reconnection failed: {mt5.last_error()}")
            else:
                logger.error("Max reconnection attempts reached")
            return False
        return True

    def get_all_markets(self):
        if not self._check_connection():
            logger.warning("Cannot get markets: MT5 not connected")
            return {}

        try:
            symbols_info = mt5.symbols_get()
            if not symbols_info:
                logger.warning("No symbols retrieved from MT5")
                return {}

            symbols = [s.name for s in symbols_info if s.visible]
            logger.info(f"Found {len(symbols)} visible symbols")

            # S'assurer que XAUUSD est inclus en priorité
            priority_symbols = ["XAUUSD", "BTCUSD", "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "EURJPY", "GBPJPY", "AUDCHF"]
            selected_symbols = []
            
            # Ajouter d'abord les symboles prioritaires s'ils sont disponibles
            for priority_symbol in priority_symbols:
                if priority_symbol in symbols:
                    selected_symbols.append(priority_symbol)
            
            # Ajouter les autres symboles jusqu'à atteindre 50
            for symbol in symbols:
                if symbol not in selected_symbols and len(selected_symbols) < 50:
                    selected_symbols.append(symbol)
            
            logger.info(f"Selected symbols: {selected_symbols}")
            markets = {}
            errors = 0
            
            for symbol in selected_symbols:
                try:
                    df = self.get_candles(symbol)
                    if df is not None and len(df) >= 100:
                        markets[symbol] = df
                except Exception as e:
                    errors += 1
                    logger.warning(f"Error getting candles for {symbol}: {e}")
                    if errors > 5:  # Arrêter après 5 erreurs
                        logger.error("Too many errors, stopping market retrieval")
                        break

            logger.info(f"Successfully retrieved {len(markets)} markets")
            return markets

        except Exception as e:
            logger.error(f"Error getting all markets: {e}")
            return {}

    def get_candles(self, symbol, timeframe=None, count=500):
        """Récupère les bougies pour un symbole et un timeframe donné"""
        if timeframe is None:
            timeframe = mt5.TIMEFRAME_M10  # Par défaut M10
            
        if not self._check_connection():
            logger.warning(f"Cannot get candles for {symbol}: MT5 not connected")
            return None

        try:
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
            if rates is None or len(rates) == 0:
                logger.warning(f"No rates retrieved for {symbol}: {mt5.last_error()}")
                return None

            df = pd.DataFrame(rates)
            df["time"] = pd.to_datetime(df["time"], unit="s")
            return df

        except Exception as e:
            logger.error(f"Exception getting candles for {symbol}: {e}")
            return None

    def get_candles_multi_timeframe(self, symbol, timeframes=None, count=500):
        """Récupère les bougies pour plusieurs timeframes"""
        if timeframes is None:
            timeframes = [mt5.TIMEFRAME_M5, mt5.TIMEFRAME_M10, mt5.TIMEFRAME_M15]
        
        result = {}
        for tf in timeframes:
            df = self.get_candles(symbol, timeframe=tf, count=count)
            if df is not None:
                result[tf] = df
        
        return result
    
    def get_account_info(self):
        """Récupère les informations du compte MT5"""
        if not self._check_connection():
            logger.warning("Cannot get account info: MT5 not connected")
            return None
        
        try:
            account = mt5.account_info()
            if account is None:
                logger.error(f"Failed to get account info: {mt5.last_error()}")
                return None
            
            return account
        except Exception as e:
            logger.error(f"Exception getting account info: {e}")
            return None
    
    def get_trade_history(self, days=1):
        """Récupère l'historique des trades pour les derniers jours"""
        if not self._check_connection():
            logger.warning("Cannot get trade history: MT5 not connected")
            return None
        
        try:
            # Calculer la date de début
            from_date = datetime.now() - timedelta(days=days)
            to_date = datetime.now()
            
            # Récupérer les deals (trades)
            deals = mt5.history_deals_get(from_date, to_date)
            
            if deals is None or len(deals) == 0:
                logger.warning(f"No trades found in the last {days} days")
                return []
            
            # Convertir en DataFrame
            df = pd.DataFrame(list(deals), columns=[deals[0]._asdict().keys()])
            
            # Filtrer pour ne garder que les trades fermés (profit != 0)
            df = df[df['profit'] != 0]
            
            logger.info(f"Found {len(df)} trades in the last {days} days")
            return df
            
        except Exception as e:
            logger.error(f"Exception getting trade history: {e}")
            return None
