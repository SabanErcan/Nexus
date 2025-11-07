"""
Modèles SQLAlchemy (ORM)
Représentation Python des tables PostgreSQL
"""

from app.models.user import User
from app.models.movie import Movie, Genre, MovieGenre
from app.models.rating import Rating
from app.models.recommendation import Recommendation
from app.models.user_preference import UserMoviePreference
from app.models.similarity import UserSimilarity, MovieSimilarity

__all__ = [
    "User",
    "Movie",
    "Genre",
    "MovieGenre",
    "Rating",
    "Recommendation",
    "UserMoviePreference",
    "UserSimilarity",
    "MovieSimilarity",
]