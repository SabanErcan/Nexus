"""
Service Google Books - Interaction avec l'API Google Books
"""

import httpx
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models.book import Book


class GoogleBooksService:
    """
    Service pour interagir avec l'API Google Books
    Documentation: https://developers.google.com/books/docs/v1/using
    """
    
    def __init__(self):
        self.base_url = "https://www.googleapis.com/books/v1"
        self.api_key = settings.google_books_api_key if hasattr(settings, 'google_books_api_key') else None
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Fait une requête à l'API Google Books
        
        Args:
            endpoint: Endpoint de l'API (ex: "/volumes")
            params: Paramètres de la requête
        
        Returns:
            Réponse JSON de l'API
        """
        if params is None:
            params = {}
        
        # Ajouter la clé API si disponible (optionnel pour Google Books)
        if self.api_key:
            params["key"] = self.api_key
        
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Google Books API error: {str(e)}"
                )
    
    async def search_books(self, query: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Recherche de livres
        
        Args:
            query: Terme de recherche
            limit: Nombre de résultats (max 40)
            offset: Index de départ
        
        Returns:
            Résultats de recherche Google Books
        """
        params = {
            "q": query,
            "maxResults": min(limit, 40),
            "startIndex": offset,
            "langRestrict": "fr",  # Filtrer pour le français
            "printType": "books"
        }
        return await self._make_request("/volumes", params)
    
    async def get_book(self, book_id: str) -> Dict[str, Any]:
        """
        Récupère les détails d'un livre
        
        Args:
            book_id: ID Google Books du livre
        
        Returns:
            Détails du livre
        """
        return await self._make_request(f"/volumes/{book_id}")
    
    async def search_by_author(self, author: str, limit: int = 10) -> Dict[str, Any]:
        """
        Recherche de livres par auteur
        
        Args:
            author: Nom de l'auteur
            limit: Nombre de résultats
        
        Returns:
            Livres de cet auteur
        """
        params = {
            "q": f"inauthor:{author}",
            "maxResults": min(limit, 40),
            "langRestrict": "fr",
            "printType": "books",
            "orderBy": "relevance"
        }
        return await self._make_request("/volumes", params)
    
    async def search_by_category(self, category: str, limit: int = 10) -> Dict[str, Any]:
        """
        Recherche de livres par catégorie
        
        Args:
            category: Catégorie/genre
            limit: Nombre de résultats
        
        Returns:
            Livres de cette catégorie
        """
        params = {
            "q": f"subject:{category}",
            "maxResults": min(limit, 40),
            "langRestrict": "fr",
            "printType": "books",
            "orderBy": "relevance"
        }
        return await self._make_request("/volumes", params)
    
    def save_book_to_db(self, db: Session, book_data: Dict[str, Any]) -> Book:
        """
        Sauvegarde un livre depuis Google Books dans la base de données
        
        Args:
            db: Session de base de données
            book_data: Données du livre depuis Google Books
        
        Returns:
            Book créé ou existant
        """
        google_books_id = book_data["id"]
        volume_info = book_data.get("volumeInfo", {})
        
        # Vérifier si le livre existe déjà
        existing_book = db.query(Book).filter(Book.google_books_id == google_books_id).first()
        
        if existing_book:
            return existing_book
        
        # Extraire les ISBNs
        isbn_13 = None
        for identifier in volume_info.get("industryIdentifiers", []):
            if identifier.get("type") == "ISBN_13":
                isbn_13 = identifier.get("identifier")
                break
        
        # Extraire l'image
        image_links = volume_info.get("imageLinks", {})
        image_url = image_links.get("thumbnail") or image_links.get("smallThumbnail")
        
        # Créer le livre
        book = Book(
            google_books_id=google_books_id,
            title=volume_info.get("title", "Titre inconnu"),
            authors=volume_info.get("authors", []),
            description=volume_info.get("description"),
            publisher=volume_info.get("publisher"),
            published_date=volume_info.get("publishedDate"),
            page_count=volume_info.get("pageCount"),
            categories=volume_info.get("categories", []),
            image_url=image_url,
            language=volume_info.get("language"),
            isbn_13=isbn_13,
            average_rating=volume_info.get("averageRating"),
            ratings_count=volume_info.get("ratingsCount")
        )
        
        db.add(book)
        db.commit()
        db.refresh(book)
        
        return book
