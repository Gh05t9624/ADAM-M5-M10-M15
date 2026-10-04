def multi_tf_filter(m10_result, m5_result):
    m10_dir = m10_result["direction"]
    m5_dir = m5_result["direction"]

    if m10_dir == "NEUTRE":
        return False, "M10 neutre → marché interdit"

    if m10_dir != m5_dir:
        return False, "Conflit M10 / M5"

    return True, "Alignement multi-timeframe confirmé"