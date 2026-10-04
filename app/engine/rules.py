def is_range(highs, lows, tolerance=0.002):
    if len(highs) < 3 or len(lows) < 3:
        return True

    h_levels = [h[1] for h in highs[-3:]]
    l_levels = [l[1] for l in lows[-3:]]

    return (
        max(h_levels) - min(h_levels) < tolerance and
        max(l_levels) - min(l_levels) < tolerance
    )


def extreme_trend(df, max_bars=8):
    closes = df['close']
    last_moves = closes.diff().tail(max_bars)

    return all(last_moves > 0) or all(last_moves < 0)