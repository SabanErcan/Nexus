"""
Modèles Game et GameRating - Gestion des jeux vidéo via RAWG
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Date, Boolean, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Game(Base):
    """
    Modèle représentant un jeu vidéo de RAWG
    """
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, index=True)
    rawg_id = Column(Integer, unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    description = Column(String(5000))
    released = Column(Date)
    background_image = Column(String(500))
    metacritic = Column(Integer)  # Score Metacritic (0-100)
    rating = Column(Integer)  # Note RAWG (0-5)
    ratings_count = Column(Integer)
    playtime = Column(Integer)  # Temps de jeu moyen en heures
    website = Column(String(500))
    
    # Relations et métadonnées
    genres = Column(JSON, default=list)  # [{"id": 4, "name": "Action"}, ...]
    platforms = Column(JSON, default=list)  # [{"platform": {"id": 4, "name": "PC"}}, ...]
    developers = Column(JSON, default=list)  # [{"id": 405, "name": "Ubisoft"}, ...]
    publishers = Column(JSON, default=list)
    esrb_rating = Column(JSON)  # {"id": 4, "name": "Mature"}
    tags = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    ratings = relationship("GameRating", back_populates="game", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Game(rawg_id={self.rawg_id}, title='{self.title}')>"


class GameRating(Base):
    """
    Note attribuée par un utilisateur à un jeu vidéo
    """
    __tablename__ = "game_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    playtime = Column(Integer)  # Temps de jeu personnel en heures
    status = Column(String(50))  # 'playing', 'completed', 'abandoned', 'wishlist'
    completion_rate = Column(Integer)  # Pourcentage de complétion (0-100)
    platform = Column(String(100))  # Plateforme sur laquelle le jeu est joué
    review = Column(String(1000))  # Avis personnel
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="game_ratings")
    game = relationship("Game", back_populates="ratings")
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='game_rating_range'),
        CheckConstraint('completion_rate >= 0 AND completion_rate <= 100', name='completion_rate_range'),
        UniqueConstraint('user_id', 'game_id', name='unique_user_game_rating'),
    )
    
    def __repr__(self):
        return f"<GameRating(user_id={self.user_id}, game_id={self.game_id}, rating={self.rating})>"