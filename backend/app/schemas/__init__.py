"""
Schemas Pydantic pour validation des données API
Définissent la structure des requêtes/réponses
"""

# Utilisateurs et authentification
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserWithStats,
    Token,
    TokenData
)

# Préférences utilisateur et onboarding
from app.schemas.preference import (
    MediaPreference,
    UserPreferenceBase,
    UserPreferenceCreate,
    UserPreferenceUpdate,
    UserPreferenceResponse,
    OnboardingStatus
)

# Films
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

# Musique (Spotify)
from app.schemas.music import (
    TrackBase,
    TrackCreate,
    TrackResponse,
    MusicRatingBase,
    MusicRatingCreate,
    MusicRatingUpdate,
    MusicRatingResponse,
    SpotifySearchResponse
)

# Livres (Google Books)
from app.schemas.book import (
    BookBase,
    BookCreate,
    BookResponse,
    BookRatingBase,
    BookRatingCreate,
    BookRatingUpdate,
    BookRatingResponse,
    GoogleBooksSearchResponse
)

# Séries TV (TMDB)
from app.schemas.tv_show import (
    TVShowBase,
    TVShowCreate,
    TVShowResponse,
    TVRatingBase,
    TVRatingCreate,
    TVRatingUpdate,
    TVRatingResponse,
    TMDBTVSearchResponse
)

# Jeux vidéo (RAWG)
from app.schemas.game import (
    GameBase,
    GameCreate,
    GameResponse,
    GameRatingBase,
    GameRatingCreate,
    GameRatingUpdate,
    GameRatingResponse,
    RAWGSearchResponse
)

__all__ = [
    # User schemas
    "UserCreate", "UserLogin", "UserResponse", "UserWithStats",
    "Token", "TokenData",
    
    # Preference schemas
    "MediaPreference", "UserPreferenceBase", "UserPreferenceCreate",
    "UserPreferenceUpdate", "UserPreferenceResponse", "OnboardingStatus",
    
    # Movie schemas
    "MovieBase", "MovieCreate", "MovieResponse", "MovieDetail",
    "GenreResponse", "MovieSearchResponse",
    
    # Rating schemas
    "RatingCreate", "RatingUpdate", "RatingResponse", "UserRatingStats",
    
    # Recommendation schemas
    "RecommendationResponse", "RecommendationExplanation",
    
    # Music schemas
    "TrackBase", "TrackCreate", "TrackResponse",
    "MusicRatingBase", "MusicRatingCreate", "MusicRatingUpdate",
    "MusicRatingResponse", "SpotifySearchResponse",
    
    # Book schemas
    "BookBase", "BookCreate", "BookResponse",
    "BookRatingBase", "BookRatingCreate", "BookRatingUpdate",
    "BookRatingResponse", "GoogleBooksSearchResponse",
    
    # TV Show schemas
    "TVShowBase", "TVShowCreate", "TVShowResponse",
    "TVRatingBase", "TVRatingCreate", "TVRatingUpdate",
    "TVRatingResponse", "TMDBTVSearchResponse",
    
    # Game schemas
    "GameBase", "GameCreate", "GameResponse",
    "GameRatingBase", "GameRatingCreate", "GameRatingUpdate",
    "GameRatingResponse", "RAWGSearchResponse"
]