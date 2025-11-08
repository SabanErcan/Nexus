"""
Modèles SQLAlchemy (ORM)
Représentation Python des tables PostgreSQL
"""

# Utilisateurs et préférences
from app.models.user import User
from app.models.user_preference import UserMoviePreference, UserPreference

# Films
from app.models.movie import Movie, Genre, MovieGenre
from app.models.rating import Rating
from app.models.recommendation import Recommendation
from app.models.similarity import UserSimilarity, MovieSimilarity

# Musique (Spotify)
from app.models.music import Track, MusicRating

# Livres (Google Books)
from app.models.book import Book, BookRating

# Séries TV (TMDB)
from app.models.tv_show import TVShow, TVRating

# Jeux vidéo (RAWG)
from app.models.game import Game, GameRating

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