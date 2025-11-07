"""
Main FastAPI Application
Point d'entrée de Nexus Recommendations Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.api import api_router


# Lifespan event pour initialiser la base de données
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestion du cycle de vie de l'application
    Exécuté au démarrage et à l'arrêt
    """
    # Startup
    print("🚀 Starting Nexus Recommendations API...")
    print(f"📊 Database: {settings.database_url.split('@')[-1]}")  # Affiche juste l'host/db
    print(f"🎬 TMDB API: {'Configured' if settings.tmdb_api_key else 'Missing API Key!'}")
    
    # Créer les tables (optionnel, car init.sql le fait déjà)
    # Base.metadata.create_all(bind=engine)
    
    yield
    
    # Shutdown
    print("👋 Shutting down Nexus Recommendations API...")


# Créer l'application FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    🎬 **Nexus Recommendations API**
    
    Système de recommandation intelligent multi-domaines utilisant des algorithmes hybrides.
    
    ## Fonctionnalités
    
    * **Authentification** - JWT Bearer Token
    * **Films** - Recherche, découverte via TMDB API
    * **Notations** - Système 5 étoiles
    * **Recommandations** - Algorithme hybride (collaboratif + contenu)
    
    ## Authentification
    
    1. Créer un compte : `POST /api/auth/register`
    2. Se connecter : `POST /api/auth/login`
    3. Utiliser le token dans le header : `Authorization: Bearer <token>`
    
    ## Phase 1: Films
    
    Module actuel fonctionnel avec TMDB API
    
    ## Phases futures
    
    * Musique (Spotify/Last.fm)
    * Livres (Google Books)
    * Jeux vidéo (RAWG)
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Liste des origines autorisées
    allow_credentials=True,
    allow_methods=["*"],  # Autoriser toutes les méthodes HTTP
    allow_headers=["*"],  # Autoriser tous les headers
)


# Inclure tous les routers API
app.include_router(api_router, prefix="/api")


# Route de base pour tester que l'API fonctionne
@app.get("/")
async def root():
    """
    Route racine - Check que l'API est en ligne
    """
    return {
        "message": "Welcome to Nexus Recommendations API",
        "version": settings.app_version,
        "status": "online",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint pour Docker/monitoring
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


# Point d'entrée pour uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )