"""
Schemas Pydantic pour User et Authentication
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """Schema pour l'inscription d'un nouvel utilisateur"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    """Schema pour la connexion"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema de réponse pour un utilisateur (sans password)"""
    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserWithStats(UserResponse):
    """Schema utilisateur avec statistiques"""
    total_ratings: Optional[int] = 0
    average_rating: Optional[float] = None
    highly_rated_count: Optional[int] = 0
    favorite_genres: Optional[dict] = None


class Token(BaseModel):
    """Schema pour le token JWT"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema pour les données extraites du token"""
    user_id: Optional[int] = None
    email: Optional[str] = None