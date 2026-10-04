from app.engine.data_provider import get_symbols, get_candles
from app.engine.analyzer import analyze_market


def batch_analyze():
    results = {
        "AUTORISÉ": [],
        "SURVEILLANCE": [],
        "INTERDIT": []
    }

    for symbol in get_symbols():
        df = get_candles(symbol)
        if df is None or len(df) < 200:
            continue

        status, direction, score = analyze_market(df)
        results[status].append({
            "symbol": symbol,
            "direction": direction,
            "score": score
        })

    results["AUTORISÉ"].sort(key=lambda x: x["score"], reverse=True)
    return results
