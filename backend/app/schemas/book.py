"""
Schemas Pydantic pour les livres (Google Books)
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class BookBase(BaseModel):
    """Schema de base pour un livre"""
    google_books_id: str = Field(..., description="ID Google Books")
    title: str = Field(..., description="Titre du livre")
    authors: List[str] = Field(default_factory=list, description="Liste des auteurs")
    description: Optional[str] = Field(None, description="Description/résumé")
    publisher: Optional[str] = Field(None, description="Éditeur")
    published_date: Optional[str] = Field(None, description="Date de publication")
    page_count: Optional[int] = Field(None, gt=0, description="Nombre de pages")
    categories: List[str] = Field(default_factory=list, description="Genres/catégories")
    image_url: Optional[str] = Field(None, description="URL de la couverture")
    language: Optional[str] = Field(None, description="Code langue (ex: 'fr')")
    isbn_13: Optional[str] = Field(None, description="ISBN-13")
    average_rating: Optional[float] = Field(None, ge=0, le=5, description="Note moyenne Google Books")
    ratings_count: Optional[int] = Field(None, ge=0, description="Nombre de notes Google Books")


class BookCreate(BookBase):
    """Schema pour créer un livre"""
    pass


class BookResponse(BookBase):
    """Schema de réponse pour un livre"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookRatingBase(BaseModel):
    """Schema de base pour une note de livre"""
    rating: int = Field(..., ge=1, le=5, description="Note de 1 à 5")
    review: Optional[str] = Field(None, max_length=1000, description="Commentaire optionnel")


class BookRatingCreate(BookRatingBase):
    """Schema pour créer une note de livre"""
    book_id: int = Field(..., description="ID du livre à noter")


class BookRatingUpdate(BookRatingBase):
    """Schema pour mettre à jour une note de livre"""
    pass


class BookRatingResponse(BookRatingBase):
    """Schema de réponse pour une note de livre"""
    id: int
    user_id: int
    book_id: int
    book: BookResponse
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GoogleBooksSearchResponse(BaseModel):
    """Schema de réponse pour une recherche Google Books"""
    items: List[BookResponse]
    total_items: int

    model_config = ConfigDict(from_attributes=True)