"""
Modèles Movie, Genre, MovieGenre - Films et leurs genres
"""

from sqlalchemy import Column, Integer, String, Text, Date, Numeric, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True)  # ID TMDB
    title = Column(String(500), nullable=False, index=True)
    original_title = Column(String(500))
    overview = Column(Text)
    release_date = Column(Date, index=True)
    poster_path = Column(String(255))
    backdrop_path = Column(String(255))
    vote_average = Column(Numeric(3, 1), index=True)
    vote_count = Column(Integer)
    popularity = Column(Numeric(10, 3), index=True)
    original_language = Column(String(10))
    runtime = Column(Integer)
    budget = Column(BigInteger)
    revenue = Column(BigInteger)
    status = Column(String(50))
    tagline = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relations
    genres = relationship("Genre", secondary="movie_genres", back_populates="movies")
    ratings = relationship("Rating", back_populates="movie", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="movie", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Movie(id={self.id}, title='{self.title}')>"


class Genre(Base):
    __tablename__ = "genres"
    
    id = Column(Integer, primary_key=True)  # ID TMDB
    name = Column(String(100), unique=True, nullable=False)
    
    # Relations
    movies = relationship("Movie", secondary="movie_genres", back_populates="genres")
    
    def __repr__(self):
        return f"<Genre(id={self.id}, name='{self.name}')>"


class MovieGenre(Base):
    """
    Table de liaison many-to-many entre Movies et Genres
    """
    __tablename__ = "movie_genres"
    
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True, index=True)
    genre_id = Column(Integer, ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True, index=True)
    
    def __repr__(self):
        return f"<MovieGenre(movie_id={self.movie_id}, genre_id={self.genre_id})>"