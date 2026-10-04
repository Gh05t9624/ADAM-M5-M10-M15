# app/api/main.py
"""Point d'entrée FastAPI pour ADAM - Structure préparée pour future implémentation"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import markets

# Création de l'application FastAPI
app = FastAPI(
    title="ADAM API",
    description="API pour le système d'analyse de marché ADAM",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS pour permettre les requêtes depuis Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À configurer selon les besoins de production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrement des routes (à implémenter dans le futur)
# app.include_router(markets.router)

@app.get("/")
async def root():
    """Endpoint racine - API prête pour implémentation"""
    return {
        "message": "ADAM API - Structure préparée pour future implémentation",
        "status": "ready",
        "note": "Les endpoints seront implémentés dans le futur"
    }

@app.get("/health")
async def health_check():
    """Vérification de santé de l'API"""
    return {
        "status": "healthy",
        "service": "ADAM API",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
