# app/engine/scoring.py

def score_market(direction, has_impulse, pullback_ok, exclusions):
    score = 0

    # Direction claire
    if direction in ("HAUSSIER", "BAISSIER"):
        score += 30

    # Impulsion récente
    if has_impulse:
        score += 25

    # Pullback propre
    if pullback_ok:
        score += 25

    # Aucune règle bloquante
    if not exclusions:
        score += 20

    return score
