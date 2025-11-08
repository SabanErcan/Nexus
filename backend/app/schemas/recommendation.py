"""
Schemas Pydantic pour Recommendation
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.schemas.movie import MovieResponse


class RecommendationResponse(BaseModel):
    """Schema de réponse pour une recommandation"""
    id: int
    user_id: int
    movie_id: int
    score: float
    created_at: datetime
    movie: MovieResponse

    model_config = ConfigDict(from_attributes=True)


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
