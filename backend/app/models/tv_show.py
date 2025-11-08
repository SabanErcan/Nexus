"""
Modèles TVShow et TVRating - Gestion des séries TV via TMDB
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Date, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class TVShow(Base):
    """
    Modèle représentant une série TV de TMDB
    """
    __tablename__ = "tv_shows"
    
    id = Column(Integer, primary_key=True)  # ID TMDB
    title = Column(String(500), nullable=False, index=True)
    original_title = Column(String(500))
    overview = Column(String(2000))
    first_air_date = Column(Date)
    last_air_date = Column(Date)
    poster_path = Column(String(500))
    backdrop_path = Column(String(500))
    popularity = Column(Integer)
    vote_average = Column(Integer)  # Note TMDB (0-10)
    vote_count = Column(Integer)
    number_of_seasons = Column(Integer)
    number_of_episodes = Column(Integer)
    status = Column(String(50))  # 'Ended', 'Returning Series', etc.
    genres = Column(JSON, default=list)  # [{"id": 18, "name": "Drama"}, ...]
    networks = Column(JSON, default=list)  # [{"id": 213, "name": "Netflix"}, ...]
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    ratings = relationship("TVRating", back_populates="tv_show", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TVShow(id={self.id}, title='{self.title}')>"


class TVRating(Base):
    """
    Note attribuée par un utilisateur à une série TV
    """
    __tablename__ = "tv_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tv_show_id = Column(Integer, ForeignKey("tv_shows.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    watchlist = Column(Boolean, default=False)  # Série dans la watchlist
    watching = Column(Boolean, default=False)  # Série en cours de visionnage
    watched = Column(Boolean, default=False)  # Série terminée
    last_episode_watched = Column(JSON)  # {"season": 1, "episode": 5}
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="tv_ratings")
    tv_show = relationship("TVShow", back_populates="ratings")
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='tv_rating_range'),
        UniqueConstraint('user_id', 'tv_show_id', name='unique_user_tvshow_rating'),
    )
    
    def __repr__(self):
        return f"<TVRating(user_id={self.user_id}, tv_show_id={self.tv_show_id}, rating={self.rating})>"