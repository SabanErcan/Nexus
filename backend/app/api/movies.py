"""
Routes pour les films
Recherche, découverte, détails via TMDB API
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.movie import MovieResponse, MovieDetail, GenreResponse, MovieSearchResponse
from app.services.tmdb_service import TMDBService
from app.dependencies import get_current_user
from app.models.user import User
from app.models.movie import Movie, Genre
from app.models.rating import Rating


router = APIRouter()
tmdb_service = TMDBService()


@router.get("/search", response_model=dict)
async def search_movies(
    query: str = Query(..., min_length=1, description="Terme de recherche"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recherche de films par titre via TMDB
    
    - **query**: Terme de recherche (minimum 1 caractère)
    - **page**: Numéro de page (défaut: 1)
    """
    results = await tmdb_service.search_movies(query, page)
    
    # Sauvegarder les films en BDD (optionnel, pour cache)
    for movie_data in results.get("results", []):
        tmdb_service.save_movie_to_db(db, movie_data)
    
    return results


@router.get("/popular", response_model=dict)
async def get_popular_movies(
    page: int = Query(1, ge=1, description="Numéro de page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les films populaires via TMDB
    
    - **page**: Numéro de page (défaut: 1)
    """
    results = await tmdb_service.get_popular_movies(page)
    
    # Sauvegarder en BDD
    for movie_data in results.get("results", []):
        tmdb_service.save_movie_to_db(db, movie_data)
    
    return results


@router.get("/top-rated", response_model=dict)
async def get_top_rated_movies(
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les films les mieux notés via TMDB
    """
    results = await tmdb_service.get_top_rated_movies(page)
    
    for movie_data in results.get("results", []):
        tmdb_service.save_movie_to_db(db, movie_data)
    
    return results


@router.get("/now-playing", response_model=dict)
async def get_now_playing_movies(
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les films actuellement au cinéma via TMDB
    """
    results = await tmdb_service.get_now_playing_movies(page)
    
    for movie_data in results.get("results", []):
        tmdb_service.save_movie_to_db(db, movie_data)
    
    return results


@router.get("/discover", response_model=dict)
async def discover_movies(
    page: int = Query(1, ge=1),
    genre_ids: Optional[str] = Query(None, description="IDs des genres séparés par virgule (ex: 28,12)"),
    sort_by: str = Query("popularity.desc", description="Tri: popularity.desc, vote_average.desc, etc."),
    year: Optional[int] = Query(None, description="Année de sortie"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Découvre des films avec filtres
    
    - **page**: Numéro de page
    - **genre_ids**: IDs des genres TMDB (ex: "28,12" pour Action,Adventure)
    - **sort_by**: Critère de tri (popularity.desc, vote_average.desc, release_date.desc)
    - **year**: Année de sortie
    """
    genre_ids_list = None
    if genre_ids:
        genre_ids_list = [int(gid.strip()) for gid in genre_ids.split(",")]
    
    results = await tmdb_service.discover_movies(
        page=page,
        genre_ids=genre_ids_list,
        sort_by=sort_by,
        year=year
    )
    
    for movie_data in results.get("results", []):
        tmdb_service.save_movie_to_db(db, movie_data)
    
    return results


@router.get("/genres", response_model=List[GenreResponse])
async def get_genres(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère la liste de tous les genres
    """
    genres = db.query(Genre).order_by(Genre.name).all()
    return genres


@router.get("/{movie_id}", response_model=dict)
async def get_movie_details(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les détails complets d'un film
    
    - **movie_id**: ID TMDB du film
    
    Retourne les infos du film + la note de l'utilisateur connecté si elle existe
    """
    # Récupérer depuis TMDB
    movie_data = await tmdb_service.get_movie_details(movie_id)
    
    # Sauvegarder en BDD
    movie = tmdb_service.save_movie_to_db(db, movie_data)
    
    # Récupérer la note de l'utilisateur connecté
    user_rating = db.query(Rating).filter(
        Rating.user_id == current_user.id,
        Rating.movie_id == movie_id
    ).first()
    
    # Ajouter la note utilisateur dans les données
    movie_data["user_rating"] = user_rating.rating if user_rating else None
    
    # Ajouter les URLs complètes des images
    if movie_data.get("poster_path"):
        movie_data["poster_url"] = tmdb_service.get_poster_url(movie_data["poster_path"])
    
    if movie_data.get("backdrop_path"):
        movie_data["backdrop_url"] = tmdb_service.get_backdrop_url(movie_data["backdrop_path"])
    
    return movie_data