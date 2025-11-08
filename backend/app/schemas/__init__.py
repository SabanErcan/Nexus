"""
Schemas Pydantic pour validation des données API
Définissent la structure des requêtes/réponses
"""

from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserWithStats,
    Token,
    TokenData
)
from app.schemas.movie import (
    MovieBase,
    MovieCreate,
    MovieResponse,
    MovieDetail,
    GenreResponse,
    MovieSearchResponse
)
from app.schemas.rating import (
    RatingCreate,
    RatingUpdate,
    RatingResponse,
    UserRatingStats
)
from app.schemas.recommendation import (
    RecommendationResponse,
    RecommendationExplanation
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserWithStats",
    "Token",
    "TokenData",
    
    # Movie schemas
    "MovieBase",
    "MovieCreate",
    "MovieResponse",
    "MovieDetail",
    "GenreResponse",
    "MovieSearchResponse",
    
    # Rating schemas
    "RatingCreate",
    "RatingUpdate",
    "RatingResponse",
    "UserRatingStats",
    
    # Recommendation schemas
    "RecommendationResponse",
    "RecommendationExplanation"
]