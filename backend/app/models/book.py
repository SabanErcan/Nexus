"""
Modèles Book et BookRating - Gestion des livres via Google Books API
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Book(Base):
    """
    Modèle représentant un livre de Google Books
    """
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    google_books_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False, index=True)
    authors = Column(JSON, default=list)  # Liste des auteurs
    description = Column(String(5000))
    publisher = Column(String(200))
    published_date = Column(String(50))  # Format YYYY ou YYYY-MM-DD
    page_count = Column(Integer)
    categories = Column(JSON, default=list)  # Genres/catégories
    image_url = Column(String(500))  # URL de la couverture
    language = Column(String(10))  # Code langue (ex: 'fr', 'en')
    isbn_13 = Column(String(13))
    average_rating = Column(Integer)  # Note Google Books
    ratings_count = Column(Integer)  # Nombre de notes Google Books
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    ratings = relationship("BookRating", back_populates="book", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Book(google_books_id='{self.google_books_id}', title='{self.title}')>"


class BookRating(Base):
    """
    Note attribuée par un utilisateur à un livre
    """
    __tablename__ = "book_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    review = Column(String(1000))  # Commentaire optionnel
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="book_ratings")
    book = relationship("Book", back_populates="ratings")
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='book_rating_range'),
        UniqueConstraint('user_id', 'book_id', name='unique_user_book_rating'),
    )
    
    def __repr__(self):
        return f"<BookRating(user_id={self.user_id}, book_id={self.book_id}, rating={self.rating})>"