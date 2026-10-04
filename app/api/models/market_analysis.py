# app/api/models/market_analysis.py
"""Modèles Pydantic pour l'analyse de marché"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class MarketAnalysisRequest(BaseModel):
    """Modèle de requête pour l'analyse d'un marché"""
    symbol: str = Field(..., description="Symbole du marché (ex: EURUSD)")
    timeframe: str = Field(default="M10", description="Timeframe d'analyse (M5, M10, M15)")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Contexte de marché optionnel")


class MarketZone(BaseModel):
    """Zone de prix (support/résistance)"""
    low: Optional[float] = Field(default=None, description="Prix bas de la zone")
    high: Optional[float] = Field(default=None, description="Prix haut de la zone")


class MarketAnalysisResponse(BaseModel):
    """Modèle de réponse pour l'analyse d'un marché"""
    symbol: str = Field(..., description="Symbole du marché")
    timeframe: str = Field(..., description="Timeframe d'analyse")
    statut: str = Field(..., description="Statut du marché (AUTORISÉ, SURVEILLANCE, INTERDIT)")
    direction: str = Field(..., description="Direction (HAUSSIER, BAISSIER, NEUTRE)")
    score: int = Field(..., description="Score de qualité (0-100)")
    confidence: float = Field(..., description="Niveau de confiance (0-1)")
    has_impulse: bool = Field(..., description="Présence d'une impulsion")
    impulse_strength: float = Field(..., description="Force de l'impulsion")
    pullback_ok: bool = Field(..., description="Pullback validé")
    trend_continuation: bool = Field(..., description="Continuation de tendance")
    ema_dir: str = Field(..., description="Direction EMA")
    st_dir: str = Field(..., description="Direction SuperTrend")
    rsi_dir: str = Field(..., description="Direction RSI")
    zone: Optional[MarketZone] = Field(default=None, description="Zone de prix")
    exclusions: List[str] = Field(default_factory=list, description="Liste des exclusions")
    confirmed: bool = Field(..., description="Confirmation du signal")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Horodatage de l'analyse")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TradePlanRequest(BaseModel):
    """Modèle de requête pour la génération d'un plan de trade"""
    symbol: str = Field(..., description="Symbole du marché")
    direction: str = Field(..., description="Direction du trade (HAUSSIER, BAISSIER)")
    score: int = Field(..., description="Score de l'analyse")
    trend_continuation: bool = Field(default=False, description="Continuation de tendance")
    pullback_active: bool = Field(default=False, description="Pullback actif")
    has_impulse: bool = Field(default=False, description="Présence d'impulsion")
    min_score: int = Field(default=55, description="Score minimum pour générer un plan")


class TradePlanResponse(BaseModel):
    """Modèle de réponse pour un plan de trade"""
    symbol: str = Field(..., description="Symbole du marché")
    type: str = Field(..., description="Type de plan (TREND_CONTINUATION, PULLBACK, MICRO_BREAKOUT)")
    direction: str = Field(..., description="Direction du trade")
    entry: float = Field(..., description="Prix d'entrée")
    sl: float = Field(..., description="Stop Loss")
    tp: float = Field(..., description="Take Profit")
    rr: float = Field(..., description="Risk/Reward ratio")
    score: int = Field(..., description="Score du plan")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Horodatage")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MarketListResponse(BaseModel):
    """Modèle de réponse pour la liste des marchés"""
    markets: List[str] = Field(..., description="Liste des symboles disponibles")
    count: int = Field(..., description="Nombre de marchés")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Horodatage")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseModel):
    """Modèle de réponse d'erreur"""
    error: str = Field(..., description="Message d'erreur")
    detail: Optional[str] = Field(default=None, description="Détails de l'erreur")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Horodatage")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
