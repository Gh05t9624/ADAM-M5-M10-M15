# app/engine/volatility.py

def volatility_ratio(df, window: int = 20) -> float:
    """
    Calcule un ratio de volatilité robuste
    basé sur (high - low), sans dépendance externe.
    """
    if not {"high", "low"}.issubset(df.columns):
        return 0.0

    ranges = df["high"] - df["low"]

    if len(ranges) < window:
        return 0.0

    recent = ranges.tail(window).mean()
    baseline = ranges.mean()

    if baseline == 0:
        return 0.0

    return recent / baseline