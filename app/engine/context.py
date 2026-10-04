# app/engine/context.py

from dataclasses import dataclass
from typing import List, Optional, Literal
from dataclasses import field

Bias = Literal["HAUSSIER", "BAISSIER", "NEUTRE"]


@dataclass
class EconomicEvent:
    currency: str
    impact: str                # LOW / MEDIUM / HIGH
    category: str              # INFLATION, RATES, etc.
    timestamp: str
    bias: Optional[Bias] = None


@dataclass
class MarketContext:
    trading_allowed: bool = True
    news_events: List[EconomicEvent] = field(default_factory=list)
    volatility_expected: bool = False
    bias: Bias = "NEUTRE"
    bias_strength: float = 0.0


def context_status(context: MarketContext):
    reasons = []

    if not context.trading_allowed:
        reasons.append("Trading désactivé par le contexte")

    high_impact_news = [
        e for e in (context.news_events or [])
        if e.impact == "HIGH"
    ]

    if high_impact_news:
        reasons.append("News économiques à fort impact détectées")

    if context.volatility_expected:
        reasons.append("Volatilité excessive attendue")

    if reasons:
        return "INTERDIT", reasons

    return "OK", []