def compute_priority(result, stats):
    score = result["score"]

    # bonus pullback
    if result["statut"] == "AUTORISÉ":
        score += 3

    # bonus direction dominante
    dominant = max(
        stats["by_direction"],
        key=stats["by_direction"].get,
        default=None
    )

    if result["direction"] == dominant:
        score += 2

    # bonus historique
    if stats["winrate"] >= 55:
        score += 2
    elif stats["winrate"] >= 65:
        score += 3

    return score
