"""
Modèle User - Utilisateurs de l'application
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relations - Films
    # Use canonical name 'ratings' to match back_populates on Rating
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    movie_preferences = relationship("UserMoviePreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    # Relations - Autres médias
    # UserPreference relationship (single row per user)
    # back_populates points to 'user_pref' on the UserPreference side
    preferences = relationship("UserPreference", back_populates="user_pref", uselist=False, cascade="all, delete-orphan")
    music_ratings = relationship("MusicRating", back_populates="user", cascade="all, delete-orphan")
    music_recommendations = relationship("MusicRecommendation", back_populates="user", cascade="all, delete-orphan")
    book_ratings = relationship("BookRating", back_populates="user", cascade="all, delete-orphan")
    tv_ratings = relationship("TVRating", back_populates="user", cascade="all, delete-orphan")
    game_ratings = relationship("GameRating", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"