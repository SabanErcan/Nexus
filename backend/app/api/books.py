"""
Routes API pour les livres (Google Books)
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.book import Book, BookRating
from app.schemas.book import (
    BookResponse,
    GoogleBooksSearchResponse,
    BookRatingCreate,
    BookRatingUpdate,
    BookRatingResponse
)
from app.services.google_books_service import GoogleBooksService

router = APIRouter(prefix="/books", tags=["Books"])
books_service = GoogleBooksService()


@router.get("/search", response_model=GoogleBooksSearchResponse)
async def search_books(
    query: str,
    limit: int = Query(20, ge=1, le=40),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Recherche de livres via Google Books
    
    Args:
        query: Terme de recherche
        limit: Nombre de résultats (1-40)
        offset: Index de départ
        db: Session de base de données
    """
    try:
        search_results = await books_service.search_books(query, limit, offset)
        
        # Convertir les résultats en modèles de base de données
        books = []
        for book_data in search_results.get("items", []):
            try:
                # Rollback en cas d'erreur précédente pour éviter "transaction is aborted"
                if db.is_active and db.get_transaction() and db.get_transaction().is_active:
                    db.rollback()
                
                book = books_service.save_book_to_db(db, book_data)
                books.append(book)
            except Exception as e:
                db.rollback()  # Rollback en cas d'erreur
                continue
        
        return {
            "items": books,
            "total_items": search_results.get("totalItems", 0)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erreur lors de la recherche Google Books: {str(e)}"
        )


@router.get("/book/{book_id}", response_model=BookResponse)
async def get_book_details(
    book_id: str,
    db: Session = Depends(get_db)
):
    """
    Récupère les détails d'un livre
    
    Args:
        book_id: ID Google Books du livre
        db: Session de base de données
    """
    try:
        book_data = await books_service.get_book(book_id)
        book = books_service.save_book_to_db(db, book_data)
        return book
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erreur lors de la récupération du livre: {str(e)}"
        )


@router.get("/recommendations", response_model=List[BookResponse])
async def get_recommendations(
    limit: int = Query(20, ge=1, le=40),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtient des recommandations de livres basées sur les notes de l'utilisateur
    
    Args:
        limit: Nombre de recommandations
        current_user: Utilisateur actuel
        db: Session de base de données
    """
    try:
        # Récupérer les livres les mieux notés (≥4 étoiles)
        top_ratings = db.query(BookRating).options(
            joinedload(BookRating.book)
        ).filter(
            BookRating.user_id == current_user.id,
            BookRating.rating >= 4
        ).order_by(BookRating.rating.desc()).limit(5).all()
        
        books = []
        
        if top_ratings:
            # Extraire les auteurs des livres les mieux notés
            authors = []
            categories = []
            
            for rating in top_ratings:
                if rating.book.authors:
                    authors.extend(rating.book.authors)
                if rating.book.categories:
                    categories.extend(rating.book.categories)
            
            # Dédupliquer
            authors = list(set(authors))[:3]
            categories = list(set(categories))[:3]
            
            # Rechercher des livres similaires par auteur
            for author in authors:
                if len(books) >= limit:
                    break
                    
                try:
                    search_results = await books_service.search_by_author(author, limit=5)
                    
                    for book_data in search_results.get("items", []):
                        if len(books) >= limit:
                            break
                        
                        google_id = book_data["id"]
                        
                        # Éviter les doublons et les livres déjà notés
                        already_rated = any(r.book.google_books_id == google_id for r in top_ratings)
                        already_in_list = any(b.google_books_id == google_id for b in books)
                        
                        if not already_rated and not already_in_list:
                            book = books_service.save_book_to_db(db, book_data)
                            books.append(book)
                
                except Exception as e:
                    print(f"[BOOKS] Erreur recherche auteur {author}: {str(e)}")
                    continue
            
            # Compléter avec des livres par catégorie
            for category in categories:
                if len(books) >= limit:
                    break
                    
                try:
                    search_results = await books_service.search_by_category(category, limit=5)
                    
                    for book_data in search_results.get("items", []):
                        if len(books) >= limit:
                            break
                        
                        google_id = book_data["id"]
                        
                        already_rated = any(r.book.google_books_id == google_id for r in top_ratings)
                        already_in_list = any(b.google_books_id == google_id for b in books)
                        
                        if not already_rated and not already_in_list:
                            book = books_service.save_book_to_db(db, book_data)
                            books.append(book)
                
                except Exception as e:
                    print(f"[BOOKS] Erreur recherche catégorie {category}: {str(e)}")
                    continue
        
        # Si pas assez de recommandations, rechercher des livres populaires
        if len(books) < limit:
            try:
                popular_query = "bestseller fiction"  # Livres populaires
                search_results = await books_service.search_books(popular_query, limit=limit - len(books))
                
                for book_data in search_results.get("items", []):
                    if len(books) >= limit:
                        break
                    
                    google_id = book_data["id"]
                    already_in_list = any(b.google_books_id == google_id for b in books)
                    
                    if not already_in_list:
                        book = books_service.save_book_to_db(db, book_data)
                        books.append(book)
            
            except Exception as e:
                print(f"[BOOKS] Erreur recherche populaires: {str(e)}")
        
        return books[:limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erreur lors de la récupération des recommandations: {str(e)}"
        )


@router.post("/ratings", response_model=BookRatingResponse)
async def rate_book(
    rating: BookRatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Note un livre
    
    Args:
        rating: Données de la note
        current_user: Utilisateur actuel
        db: Session de base de données
    """
    # Vérifier si le livre existe
    book = db.query(Book).filter(Book.id == rating.book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livre non trouvé"
        )
    
    # Vérifier si une note existe déjà
    existing_rating = db.query(BookRating).filter(
        BookRating.user_id == current_user.id,
        BookRating.book_id == rating.book_id
    ).first()
    
    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous avez déjà noté ce livre"
        )
    
    # Créer la note
    db_rating = BookRating(
        user_id=current_user.id,
        book_id=rating.book_id,
        rating=rating.rating,
        review=rating.review
    )
    
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    
    # Charger explicitement la relation book
    db.refresh(db_rating, ['book'])
    
    return db_rating


@router.put("/ratings/{rating_id}", response_model=BookRatingResponse)
async def update_rating(
    rating_id: int,
    rating_update: BookRatingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Met à jour une note de livre
    
    Args:
        rating_id: ID de la note
        rating_update: Nouvelle note
        current_user: Utilisateur actuel
        db: Session de base de données
    """
    # Récupérer la note existante
    db_rating = db.query(BookRating).filter(
        BookRating.id == rating_id,
        BookRating.user_id == current_user.id
    ).first()
    
    if not db_rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note non trouvée ou non autorisée"
        )
    
    # Mettre à jour la note
    db_rating.rating = rating_update.rating
    if rating_update.review is not None:
        db_rating.review = rating_update.review
    
    db.commit()
    db.refresh(db_rating)
    
    # Charger explicitement la relation book
    db.refresh(db_rating, ['book'])
    
    return db_rating


@router.delete("/ratings/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rating(
    rating_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Supprime une note de livre
    
    Args:
        rating_id: ID de la note
        current_user: Utilisateur actuel
        db: Session de base de données
    """
    # Récupérer la note existante
    db_rating = db.query(BookRating).filter(
        BookRating.id == rating_id,
        BookRating.user_id == current_user.id
    ).first()
    
    if not db_rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note non trouvée ou non autorisée"
        )
    
    # Supprimer la note
    db.delete(db_rating)
    db.commit()


@router.get("/ratings/me", response_model=List[BookRatingResponse])
async def get_my_ratings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les notes de livres de l'utilisateur actuel
    
    Args:
        current_user: Utilisateur actuel
        db: Session de base de données
    """
    ratings = db.query(BookRating).options(
        joinedload(BookRating.book)
    ).filter(
        BookRating.user_id == current_user.id
    ).all()
    
    return ratings
