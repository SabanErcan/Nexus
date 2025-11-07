"""
Schemas Pydantic pour Movie
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, List


class GenreResponse(BaseModel):
    """Schema pour un genre"""
    id: int
    name: str
    
    model_config = ConfigDict(from_attributes=True)


class MovieBase(BaseModel):
    """Schema de base pour un film"""
    id: int
    title: str
    original_title: Optional[str] = None
    overview: Optional[str] = None
    release_date: Optional[date] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    popularity: Optional[float] = None
    original_language: Optional[str] = None


class MovieCreate(MovieBase):
    """Schema pour créer un film (depuis TMDB)"""
    runtime: Optional[int] = None
    budget: Optional[int] = None
    revenue: Optional[int] = None
    status: Optional[str] = None
    tagline: Optional[str] = None


class MovieResponse(MovieBase):
    """Schema de réponse pour un film simple"""
    genres: List[GenreResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class MovieDetail(MovieResponse):
    """Schema détaillé d'un film"""
    runtime: Optional[int] = None
    budget: Optional[int] = None
    revenue: Optional[int] = None
    status: Optional[str] = None
    tagline: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Statistiques supplémentaires (calculées)
    user_rating: Optional[int] = None  # Note de l'utilisateur connecté
    total_user_ratings: Optional[int] = 0
    avg_user_rating: Optional[float] = None


class MovieSearchResponse(BaseModel):
    """Schema pour les résultats de recherche TMDB"""
    page: int
    total_results: int
    total_pages: int
    results: List[MovieResponse]