"""
Modèles SQLAlchemy (ORM)
Représentation Python des tables PostgreSQL
"""

"""
Charge les modules de modèles pour que les classes déclaratives
soient enregistrées auprès de SQLAlchemy sans forcer un ordre fragile
d'import qui cause des erreurs de mapping.
"""

# Importer les modules (en tant que modules) — ceci enregistre toutes
# les classes dérivées de Base dans la metadata sans déclencher
# immédiatement la configuration des mappers dans un ordre cassé.
import app.models.user_preference
import app.models.user
import app.models.movie
import app.models.rating
import app.models.recommendation
import app.models.similarity
import app.models.music
import app.models.book
import app.models.tv_show
import app.models.game

# Optionnel: exposer quelques noms courants pour compatibilité
from app.models.user import User
from app.models.movie import Movie, Genre, MovieGenre
from app.models.rating import Rating
from app.models.recommendation import Recommendation
from app.models.user_preference import UserMoviePreference, UserPreference

__all__ = [
    "User",
    "Movie",
    "Genre",
    "MovieGenre",
    "Rating",
    "Recommendation",
    "UserMoviePreference",
    "UserPreference",
]