def is_range(highs, lows, tolerance=0.002):
    if not highs or not lows:
        return True

    return abs(max(highs) - min(highs)) / max(highs) < tolerance


def is_inert(df):
    body = abs(df['close'] - df['open'])
    return body.tail(20).mean() < body.mean() * 0.3
