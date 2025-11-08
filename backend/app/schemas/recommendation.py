"""
Schemas Pydantic pour Recommendation
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.schemas.movie import MovieResponse
from app.schemas.music import TrackResponse


class RecommendationBase(BaseModel):
    """Schema de base pour les recommandations"""
    id: int
    user_id: int
    score: float
    created_at: datetime
    is_viewed: bool = False
    is_dismissed: bool = False

    model_config = ConfigDict(from_attributes=True)


class RecommendationResponse(RecommendationBase):
    """Schema de réponse pour une recommandation de film"""
    movie_id: int
    movie: MovieResponse


class MusicRecommendationResponse(RecommendationBase):
    """Schema de réponse pour une recommandation musicale"""
    track_id: int
    track: TrackResponse


class RecommendationExplanation(BaseModel):
    """Schema pour expliquer une recommandation"""
    movie_id: int
    movie_title: str
    score: float
    reasons: List[str]
    similar_rated_movies: List[dict]  # [{id, title, rating}, ...]
    genres_match: Optional[dict] = None  # {genre: score, ...}
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
