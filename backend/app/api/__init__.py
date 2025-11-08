"""
Routes API
Endpoints FastAPI organisés par domaine
"""

from fastapi import APIRouter

# Import des routers individuels
from app.api import auth, movies, ratings, recommendations

# Router principal qui regroupe tous les sous-routers
api_router = APIRouter()

# Inclure les routers de chaque module
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(movies.router, prefix="/movies", tags=["Movies"])
api_router.include_router(ratings.router, prefix="/ratings", tags=["Ratings"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
