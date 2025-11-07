"""
Configuration globale de l'application
Gestion des variables d'environnement et paramètres
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Configuration de l'application avec validation Pydantic
    """
    
    # Application
    app_name: str = "Nexus Recommendations"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Base de données
    database_url: str
    
    # TMDB API
    tmdb_api_key: str
    tmdb_base_url: str = "https://api.themoviedb.org/3"
    tmdb_image_base_url: str = "https://image.tmdb.org/t/p"
    
    # Sécurité JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://frontend:3000"
    ]
    
    # Recommandations
    min_ratings_for_recommendations: int = 3  # Nombre minimum de notes avant recommandations
    recommendations_count: int = 20  # Nombre de recommandations à générer
    collaborative_weight: float = 0.6  # Poids du filtrage collaboratif (60%)
    content_weight: float = 0.4  # Poids du filtrage basé contenu (40%)
    min_similarity_score: float = 0.3  # Score minimum de similarité
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Crée et cache une instance unique de Settings
    lru_cache = évite de recharger les variables à chaque appel
    """
    return Settings()


# Instance globale accessible partout
settings = get_settings()