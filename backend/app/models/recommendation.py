"""
Modèle Recommendation - Recommandations générées pour les utilisateurs
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Numeric, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Recommendation(Base):
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
    
    def __repr__(self):
        return f"<Recommendation(user_id={self.user_id}, movie_id={self.movie_id}, score={self.score}, type='{self.algorithm_type}')>"