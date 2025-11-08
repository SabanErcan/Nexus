"""
Schemas Pydantic pour les préférences utilisateur
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class MediaPreference(BaseModel):
    """Schema pour les préférences d'un type de média spécifique"""
    enabled: bool = Field(default=False, description="Si ce type de média est activé")
    genres: List[str] = Field(default_factory=list, description="Liste des genres préférés")


class UserPreferenceBase(BaseModel):
    """Schema de base pour les préférences utilisateur"""
    movies: MediaPreference = Field(default_factory=MediaPreference, description="Préférences films")
    music: MediaPreference = Field(default_factory=MediaPreference, description="Préférences musique")
    books: MediaPreference = Field(default_factory=MediaPreference, description="Préférences livres")
    tv_shows: MediaPreference = Field(default_factory=MediaPreference, description="Préférences séries TV")
    games: MediaPreference = Field(default_factory=MediaPreference, description="Préférences jeux vidéo")


class UserPreferenceCreate(UserPreferenceBase):
    """Schema pour créer des préférences utilisateur"""
    pass


class UserPreferenceUpdate(UserPreferenceBase):
    """Schema pour mettre à jour des préférences utilisateur"""
    onboarding_completed: Optional[bool] = Field(None, description="Statut de l'onboarding")


class UserPreferenceResponse(UserPreferenceBase):
    """Schema de réponse pour les préférences utilisateur"""
    id: int
    user_id: int
    onboarding_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OnboardingStatus(BaseModel):
    """Schema pour le statut d'onboarding"""
    completed: bool
    current_step: Optional[str] = Field(None, description="Étape actuelle de l'onboarding")
    steps_completed: List[str] = Field(default_factory=list, description="Liste des étapes complétées")