# app/engine/extreme_event.py

def detect_extreme_market_event(
    *,
    direction: str,
    has_impulse: bool,
    pullback_ok: bool,
    volatility_ratio: float,
    context_ok: bool
) -> bool:
    """
    Détecte un marché exceptionnel pouvant justifier
    une gestion à TP indéfini.
    """

    if not context_ok:
        return False

    if not has_impulse:
        return False

    if pullback_ok:
        return False  # trop sain = pas extrême

    if volatility_ratio < 1.7:
        return False

    if direction not in ("HAUSSIER", "BAISSIER"):
        return False

    return True