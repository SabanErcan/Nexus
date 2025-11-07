"""
Schemas Pydantic pour Rating
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from app.schemas.movie import MovieResponse


class RatingCreate(BaseModel):
    """Schema pour créer/modifier une note"""
    movie_id: int
    rating: int = Field(..., ge=1, le=5, description="Note entre 1 et 5")


class RatingUpdate(BaseModel):
    """Schema pour mettre à jour une note"""
    rating: int = Field(..., ge=1, le=5)


class RatingResponse(BaseModel):
    """Schema de réponse pour une note"""
    id: int
    user_id: int
    movie_id: int
    rating: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class RatingWithMovie(RatingResponse):
    """Schema de réponse avec les détails du film"""
    movie: MovieResponse


class UserRatingStats(BaseModel):
    """Schema pour les statistiques de notation d'un utilisateur"""
    total_ratings: int
    average_rating: float
    highly_rated_count: int  # Films notés 4-5
    rating_distribution: dict  # {1: count, 2: count, ...}
    favorite_genres: Optional[dict] = None
    last_rating_date: Optional[datetime] = None