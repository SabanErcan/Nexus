"""
Configuration de la base de données PostgreSQL
Gestion des sessions SQLAlchemy
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Créer le moteur SQLAlchemy
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Vérifie la connexion avant de l'utiliser
    pool_size=10,  # Nombre de connexions dans le pool
    max_overflow=20,  # Connexions supplémentaires autorisées
    echo=settings.debug  # Log les requêtes SQL en mode debug
)

# Créer une factory de sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base pour les modèles SQLAlchemy
Base = declarative_base()


def get_db():
    """
    Dependency injection pour FastAPI
    Crée une session de BDD pour chaque requête et la ferme après
    
    Usage dans les routes:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialise la base de données
    Crée toutes les tables si elles n'existent pas
    (Utilisé uniquement si on n'utilise pas Alembic)
    """
    Base.metadata.create_all(bind=engine)