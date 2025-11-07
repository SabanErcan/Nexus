"""
Modèle UserMoviePreference - Préférences et statistiques utilisateur
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class UserMoviePreference(Base):
    __tablename__ = "user_movie_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    favorite_genres = Column(JSON)  # {"Action": 15, "Drama": 10, ...}
    average_rating = Column(Numeric(3, 2))
    total_ratings = Column(Integer, default=0)
    highly_rated_count = Column(Integer, default=0)  # Films notés 4-5
    last_rating_date = Column(DateTime(timezone=True))
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="preferences")
    
    def __repr__(self):
        return f"<UserMoviePreference(user_id={self.user_id}, total_ratings={self.total_ratings})>"