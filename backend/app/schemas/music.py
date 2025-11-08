"""
Schemas Pydantic pour la musique (Spotify)
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class TrackBase(BaseModel):
    """Schema de base pour une piste musicale"""
    spotify_id: str = Field(..., description="ID Spotify de la piste")
    title: str = Field(..., description="Titre de la piste")
    artist: str = Field(..., description="Artiste principal")
    album: Optional[str] = Field(None, description="Album")
    release_year: Optional[int] = Field(None, description="Année de sortie")
    preview_url: Optional[str] = Field(None, description="URL du preview 30s")
    image_url: Optional[str] = Field(None, description="URL de la pochette")
    duration_ms: Optional[int] = Field(None, description="Durée en millisecondes")
    popularity: Optional[int] = Field(None, ge=0, le=100, description="Score de popularité Spotify")
    genres: List[str] = Field(default_factory=list, description="Genres musicaux")


class TrackCreate(TrackBase):
    """Schema pour créer une piste"""
    pass


class TrackResponse(TrackBase):
    """Schema de réponse pour une piste"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MusicRatingBase(BaseModel):
    """Schema de base pour une note musicale"""
    rating: int = Field(..., ge=1, le=5, description="Note de 1 à 5")


class MusicRatingCreate(MusicRatingBase):
    """Schema pour créer une note musicale"""
    track_id: int = Field(..., description="ID de la piste à noter")


class MusicRatingUpdate(MusicRatingBase):
    """Schema pour mettre à jour une note musicale"""
    pass


class MusicRatingResponse(MusicRatingBase):
    """Schema de réponse pour une note musicale"""
    id: int
    user_id: int
    track_id: int
    track: TrackResponse
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SpotifySearchResponse(BaseModel):
    """Schema de réponse pour une recherche Spotify"""
    items: List[TrackResponse]
    total: int
    limit: int
    offset: int

    model_config = ConfigDict(from_attributes=True)