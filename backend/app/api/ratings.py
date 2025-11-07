"""
Routes pour les notations
Créer, modifier, supprimer, consulter les notes
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.schemas.rating import RatingCreate, RatingUpdate, RatingResponse, RatingWithMovie, UserRatingStats
from app.schemas.movie import MovieResponse
from app.dependencies import get_current_user
from app.models.user import User
from app.models.rating import Rating
from app.models.movie import Movie, MovieGenre, Genre


router = APIRouter()


@router.post("/", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_rating(
    rating_data: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crée ou met à jour une note pour un film
    
    - **movie_id**: ID TMDB du film
    - **rating**: Note de 1 à 5
    
    Si l'utilisateur a déjà noté ce film, la note est mise à jour
    """
    # Vérifier si le film existe en BDD
    movie = db.query(Movie).filter(Movie.id == rating_data.movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found. Please view the movie details first."
        )
    
    # Vérifier si une note existe déjà
    existing_rating = db.query(Rating).filter(
        Rating.user_id == current_user.id,
        Rating.movie_id == rating_data.movie_id
    ).first()
    
    if existing_rating:
        # Mettre à jour
        existing_rating.rating = rating_data.rating
        db.commit()
        db.refresh(existing_rating)
        return existing_rating
    else:
        # Créer
        new_rating = Rating(
            user_id=current_user.id,
            movie_id=rating_data.movie_id,
            rating=rating_data.rating
        )
        db.add(new_rating)
        db.commit()
        db.refresh(new_rating)
        return new_rating


@router.get("/", response_model=List[RatingWithMovie])
async def get_user_ratings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    Récupère toutes les notes de l'utilisateur connecté avec les détails des films
    
    - **skip**: Nombre d'éléments à sauter (pagination)
    - **limit**: Nombre maximum d'éléments à retourner (max 100)
    """
    ratings = db.query(Rating).filter(
        Rating.user_id == current_user.id
    ).order_by(Rating.updated_at.desc()).offset(skip).limit(limit).all()
    
    # Construire la réponse avec les films
    result = []
    for rating in ratings:
        movie = db.query(Movie).filter(Movie.id == rating.movie_id).first()
        
        if movie:
            movie_response = MovieResponse.model_validate(movie)
            rating_response = RatingResponse.model_validate(rating)
            
            result.append(RatingWithMovie(
                **rating_response.model_dump(),
                movie=movie_response
            ))
    
    return result


@router.get("/stats", response_model=UserRatingStats)
async def get_user_rating_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les statistiques de notation de l'utilisateur
    
    - Nombre total de notes
    - Note moyenne
    - Nombre de films bien notés (4-5)
    - Distribution des notes
    - Genres préférés
    """
    # Statistiques de base
    ratings = db.query(Rating).filter(Rating.user_id == current_user.id).all()
    
    if not ratings:
        return UserRatingStats(
            total_ratings=0,
            average_rating=0.0,
            highly_rated_count=0,
            rating_distribution={},
            favorite_genres=None,
            last_rating_date=None
        )
    
    total_ratings = len(ratings)
    average_rating = sum(r.rating for r in ratings) / total_ratings
    highly_rated_count = sum(1 for r in ratings if r.rating >= 4)
    
    # Distribution des notes
    rating_distribution = {i: 0 for i in range(1, 6)}
    for rating in ratings:
        rating_distribution[rating.rating] += 1
    
    # Genres préférés (calcul)
    genre_scores = {}
    for rating in ratings:
        if rating.rating >= 4:  # Seulement les films bien notés
            movie_genres = db.query(Genre).join(
                MovieGenre, MovieGenre.genre_id == Genre.id
            ).filter(MovieGenre.movie_id == rating.movie_id).all()
            
            for genre in movie_genres:
                genre_scores[genre.name] = genre_scores.get(genre.name, 0) + 1
    
    # Trier les genres par score décroissant
    favorite_genres = dict(sorted(genre_scores.items(), key=lambda x: x[1], reverse=True))
    
    # Date de la dernière note
    last_rating = max(ratings, key=lambda r: r.updated_at)
    
    return UserRatingStats(
        total_ratings=total_ratings,
        average_rating=round(average_rating, 2),
        highly_rated_count=highly_rated_count,
        rating_distribution=rating_distribution,
        favorite_genres=favorite_genres if favorite_genres else None,
        last_rating_date=last_rating.updated_at
    )


@router.put("/{rating_id}", response_model=RatingResponse)
async def update_rating(
    rating_id: int,
    rating_data: RatingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Met à jour une note existante
    
    - **rating_id**: ID de la note à mettre à jour
    - **rating**: Nouvelle note (1-5)
    """
    rating = db.query(Rating).filter(
        Rating.id == rating_id,
        Rating.user_id == current_user.id
    ).first()
    
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )
    
    rating.rating = rating_data.rating
    db.commit()
    db.refresh(rating)
    
    return rating


@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rating(
    rating_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Supprime une note
    
    - **rating_id**: ID de la note à supprimer
    """
    rating = db.query(Rating).filter(
        Rating.id == rating_id,
        Rating.user_id == current_user.id
    ).first()
    
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )
    
    db.delete(rating)
    db.commit()
    
    return None


@router.get("/movie/{movie_id}", response_model=RatingResponse)
async def get_rating_for_movie(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère la note de l'utilisateur pour un film spécifique
    
    - **movie_id**: ID TMDB du film
    """
    rating = db.query(Rating).filter(
        Rating.user_id == current_user.id,
        Rating.movie_id == movie_id
    ).first()
    
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No rating found for this movie"
        )
    
    return rating