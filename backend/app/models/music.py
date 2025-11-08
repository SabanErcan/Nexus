"""
Modèles Track, Artist et MusicRating - Gestion de la musique via Spotify
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, BigInteger, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Track(Base):
    """
    Modèle représentant une piste musicale de Spotify
    """
    __tablename__ = "tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    spotify_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    artist = Column(String(500), nullable=False, index=True)
    album = Column(String(500))
    release_year = Column(Integer)
    preview_url = Column(String(500))  # URL du preview 30s MP3
    image_url = Column(String(500))  # URL de la pochette d'album
    duration_ms = Column(BigInteger)
    popularity = Column(Integer)  # Score de popularité Spotify (0-100)
    genres = Column(JSON, default=list)  # Liste des genres musicaux
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    ratings = relationship("MusicRating", back_populates="track", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Track(spotify_id='{self.spotify_id}', title='{self.title}', artist='{self.artist}')>"


class MusicRating(Base):
    """
    Note attribuée par un utilisateur à une piste musicale
    """
    __tablename__ = "music_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="music_ratings")
    track = relationship("Track", back_populates="ratings")
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='music_rating_range'),
        UniqueConstraint('user_id', 'track_id', name='unique_user_track_rating'),
    )
    
    def __repr__(self):
        return f"<MusicRating(user_id={self.user_id}, track_id={self.track_id}, rating={self.rating})>"