"""
Modèle Recommendation - Recommandations générées pour les utilisateurs
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Numeric, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime


class RecommendationMixin:
    """Classe de base pour les recommandations"""
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Numeric(5, 3), nullable=False, index=True)
    algorithm_type = Column(String(50), nullable=False)
    explanation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_viewed = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('score >= 0 AND score <= 1', name='score_range_check'),
    )
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(user_id={self.user_id}, score={self.score}, type='{self.algorithm_type}')>"


class Recommendation(Base, RecommendationMixin):
    """Recommandations de films"""
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Numeric(5, 3), nullable=False, index=True)
    algorithm_type = Column(String(50), nullable=False)  # 'collaborative', 'content_based', 'hybrid'
    explanation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_viewed = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('score >= 0 AND score <= 1', name='score_range_check'),
    )
    
    # Relations
    user = relationship("User", back_populates="recommendations")
    movie = relationship("Movie", back_populates="recommendations")
    
class MusicRecommendation(Base, RecommendationMixin):
    """Recommandations musicales"""
    __tablename__ = "music_recommendations"
    
    track_id = Column(Integer, ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relations
    user = relationship("User", back_populates="music_recommendations")
    track = relationship("Track", back_populates="recommendations")