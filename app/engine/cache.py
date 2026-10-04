import time

CACHE = {}
TTL = 60  # secondes

def get_cached(symbol):
    if symbol in CACHE:
        data, ts = CACHE[symbol]
        if time.time() - ts < TTL:
            return data
    return None

def set_cache(symbol, df):
    CACHE[symbol] = (df, time.time())
