"""
Modèles Similarity - Calculs de similarité pour les algorithmes de recommandation
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class UserSimilarity(Base):
    """
    Similarité entre utilisateurs (pour filtrage collaboratif)
    Score basé sur les films notés en commun
    """
    __tablename__ = "user_similarity"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id_1 = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id_2 = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    similarity_score = Column(Numeric(5, 3), nullable=False, index=True)
    common_ratings_count = Column(Integer, nullable=False)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('similarity_score >= 0 AND similarity_score <= 1', name='user_similarity_score_check'),
        CheckConstraint('user_id_1 < user_id_2', name='user_order_check'),  # Évite doublons
        UniqueConstraint('user_id_1', 'user_id_2', name='unique_user_pair'),
    )
    
    def __repr__(self):
        return f"<UserSimilarity(user1={self.user_id_1}, user2={self.user_id_2}, score={self.similarity_score})>"


class MovieSimilarity(Base):
    """
    Similarité entre films (pour filtrage basé sur le contenu)
    Score basé sur les genres, popularité, etc.
    """
    __tablename__ = "movie_similarity"
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id_1 = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    movie_id_2 = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    similarity_score = Column(Numeric(5, 3), nullable=False, index=True)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('similarity_score >= 0 AND similarity_score <= 1', name='movie_similarity_score_check'),
        CheckConstraint('movie_id_1 < movie_id_2', name='movie_order_check'),
        UniqueConstraint('movie_id_1', 'movie_id_2', name='unique_movie_pair'),
    )
    
    def __repr__(self):
        return f"<MovieSimilarity(movie1={self.movie_id_1}, movie2={self.movie_id_2}, score={self.similarity_score})>"