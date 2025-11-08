"""
Schemas Pydantic pour les jeux vidéo (RAWG)
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
from datetime import datetime, date


class GameBase(BaseModel):
    """Schema de base pour un jeu vidéo"""
    rawg_id: int = Field(..., description="ID RAWG du jeu")
    title: str = Field(..., description="Titre du jeu")
    description: Optional[str] = Field(None, description="Description du jeu")
    released: Optional[date] = Field(None, description="Date de sortie")
    background_image: Optional[str] = Field(None, description="Image de fond")
    metacritic: Optional[int] = Field(None, ge=0, le=100, description="Score Metacritic")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Note RAWG")
    ratings_count: Optional[int] = Field(None, ge=0, description="Nombre de notes")
    playtime: Optional[int] = Field(None, ge=0, description="Temps de jeu moyen (heures)")
    website: Optional[str] = Field(None, description="Site officiel")
    
    # Relations et métadonnées
    genres: List[Dict[str, str]] = Field(default_factory=list, description="Genres du jeu")
    platforms: List[Dict[str, Dict[str, str]]] = Field(default_factory=list, description="Plateformes")
    developers: List[Dict[str, str]] = Field(default_factory=list, description="Développeurs")
    publishers: List[Dict[str, str]] = Field(default_factory=list, description="Éditeurs")
    esrb_rating: Optional[Dict[str, str]] = Field(None, description="Classification ESRB")
    tags: List[str] = Field(default_factory=list, description="Tags")


class GameCreate(GameBase):
    """Schema pour créer un jeu"""
    pass


class GameResponse(GameBase):
    """Schema de réponse pour un jeu"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GameRatingBase(BaseModel):
    """Schema de base pour une note de jeu"""
    rating: int = Field(..., ge=1, le=5, description="Note de 1 à 5")
    playtime: Optional[int] = Field(None, ge=0, description="Temps de jeu personnel (heures)")
    status: Optional[str] = Field(
        None,
        description="Statut (playing, completed, abandoned, wishlist)"
    )
    completion_rate: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="Pourcentage de complétion"
    )
    platform: Optional[str] = Field(None, description="Plateforme de jeu")
    review: Optional[str] = Field(None, max_length=1000, description="Avis personnel")


class GameRatingCreate(GameRatingBase):
    """Schema pour créer une note de jeu"""
    game_id: int = Field(..., description="ID du jeu à noter")


class GameRatingUpdate(GameRatingBase):
    """Schema pour mettre à jour une note de jeu"""
    pass


class GameRatingResponse(GameRatingBase):
    """Schema de réponse pour une note de jeu"""
    id: int
    user_id: int
    game_id: int
    game: GameResponse
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RAWGSearchResponse(BaseModel):
    """Schema de réponse pour une recherche RAWG"""
    items: List[GameResponse]
    total: int
    next_page: Optional[str] = None
    previous_page: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)