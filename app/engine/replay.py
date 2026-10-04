def evaluate_outcome(df, direction, lookahead=20, rr=2):
    """
    df : DataFrame
    direction : HAUSSIER / BAISSIER
    """

    entry = df.iloc[-1]
    entry_price = entry["close"]

    risk = abs(entry["high"] - entry["low"])
    if risk == 0:
        return "NEUTRE"

    if direction == "HAUSSIER":
        sl = entry_price - risk
        tp = entry_price + risk * rr
    else:
        sl = entry_price + risk
        tp = entry_price - risk * rr

    future = df.iloc[-lookahead:]

    for _, row in future.iterrows():
        if direction == "HAUSSIER":
            if row["low"] <= sl:
                return "PERTE"
            if row["high"] >= tp:
                return "GAIN"
        else:
            if row["high"] >= sl:
                return "PERTE"
            if row["low"] <= tp:
                return "GAIN"

    return "NEUTRE"
