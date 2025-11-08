"""
Schemas Pydantic pour les séries TV (TMDB)
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
from datetime import datetime, date


class TVShowBase(BaseModel):
    """Schema de base pour une série TV"""
    title: str = Field(..., description="Titre de la série")
    original_title: Optional[str] = Field(None, description="Titre original")
    overview: Optional[str] = Field(None, description="Synopsis")
    first_air_date: Optional[date] = Field(None, description="Date de première diffusion")
    last_air_date: Optional[date] = Field(None, description="Date de dernière diffusion")
    poster_path: Optional[str] = Field(None, description="Chemin de l'affiche")
    backdrop_path: Optional[str] = Field(None, description="Chemin de l'image de fond")
    popularity: Optional[float] = Field(None, ge=0, description="Score de popularité")
    vote_average: Optional[float] = Field(None, ge=0, le=10, description="Note moyenne TMDB")
    vote_count: Optional[int] = Field(None, ge=0, description="Nombre de votes")
    number_of_seasons: Optional[int] = Field(None, ge=0, description="Nombre de saisons")
    number_of_episodes: Optional[int] = Field(None, ge=0, description="Nombre d'épisodes")
    status: Optional[str] = Field(None, description="Statut de la série")
    genres: List[Dict[str, str]] = Field(default_factory=list, description="Genres de la série")
    networks: List[Dict[str, str]] = Field(default_factory=list, description="Networks de diffusion")


class TVShowCreate(TVShowBase):
    """Schema pour créer une série TV"""
    pass


class TVShowResponse(TVShowBase):
    """Schema de réponse pour une série TV"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TVRatingBase(BaseModel):
    """Schema de base pour une note de série TV"""
    rating: int = Field(..., ge=1, le=5, description="Note de 1 à 5")
    watchlist: bool = Field(default=False, description="Série dans la watchlist")
    watching: bool = Field(default=False, description="Série en cours de visionnage")
    watched: bool = Field(default=False, description="Série terminée")
    last_episode_watched: Optional[Dict[str, int]] = Field(
        None,
        description="Dernier épisode vu (format: {'season': 1, 'episode': 5})"
    )


class TVRatingCreate(TVRatingBase):
    """Schema pour créer une note de série TV"""
    tv_show_id: int = Field(..., description="ID de la série à noter")


class TVRatingUpdate(TVRatingBase):
    """Schema pour mettre à jour une note de série TV"""
    pass


class TVRatingResponse(TVRatingBase):
    """Schema de réponse pour une note de série TV"""
    id: int
    user_id: int
    tv_show_id: int
    tv_show: TVShowResponse
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TMDBTVSearchResponse(BaseModel):
    """Schema de réponse pour une recherche TMDB TV"""
    items: List[TVShowResponse]
    total_results: int
    total_pages: int
    page: int

    model_config = ConfigDict(from_attributes=True)