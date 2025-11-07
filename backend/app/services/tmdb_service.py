"""
Service TMDB - Interaction avec l'API The Movie Database
"""

import httpx
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models.movie import Movie, Genre, MovieGenre


class TMDBService:
    """
    Service pour interagir avec l'API TMDB
    Documentation: https://developers.themoviedb.org/3
    """
    
    def __init__(self):
        self.base_url = settings.tmdb_base_url
        self.api_key = settings.tmdb_api_key
        self.image_base_url = settings.tmdb_image_base_url
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Fait une requête à l'API TMDB
        
        Args:
            endpoint: Endpoint de l'API (ex: "/movie/popular")
            params: Paramètres de la requête
        
        Returns:
            Réponse JSON de l'API
        """
        if params is None:
            params = {}
        
        params["api_key"] = self.api_key
        params["language"] = "fr-FR"  # Langue française
        
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"TMDB API error: {str(e)}"
                )
    
    async def search_movies(self, query: str, page: int = 1) -> Dict[str, Any]:
        """
        Recherche de films par titre
        
        Args:
            query: Terme de recherche
            page: Numéro de page
        
        Returns:
            Résultats de recherche TMDB
        """
        return await self._make_request("/search/movie", {"query": query, "page": page})
    
    async def get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """
        Récupère les détails d'un film
        
        Args:
            movie_id: ID TMDB du film
        
        Returns:
            Détails du film
        """
        return await self._make_request(f"/movie/{movie_id}")
    
    async def get_popular_movies(self, page: int = 1) -> Dict[str, Any]:
        """
        Récupère les films populaires
        
        Args:
            page: Numéro de page
        
        Returns:
            Films populaires
        """
        return await self._make_request("/movie/popular", {"page": page})
    
    async def get_top_rated_movies(self, page: int = 1) -> Dict[str, Any]:
        """
        Récupère les films les mieux notés
        
        Args:
            page: Numéro de page
        
        Returns:
            Films top rated
        """
        return await self._make_request("/movie/top_rated", {"page": page})
    
    async def get_now_playing_movies(self, page: int = 1) -> Dict[str, Any]:
        """
        Récupère les films actuellement au cinéma
        
        Args:
            page: Numéro de page
        
        Returns:
            Films now playing
        """
        return await self._make_request("/movie/now_playing", {"page": page})
    
    async def discover_movies(
        self,
        page: int = 1,
        genre_ids: Optional[List[int]] = None,
        sort_by: str = "popularity.desc",
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Découverte de films avec filtres
        
        Args:
            page: Numéro de page
            genre_ids: Liste d'IDs de genres
            sort_by: Tri (popularity.desc, vote_average.desc, etc.)
            year: Année de sortie
        
        Returns:
            Films découverts
        """
        params = {"page": page, "sort_by": sort_by}
        
        if genre_ids:
            params["with_genres"] = ",".join(map(str, genre_ids))
        
        if year:
            params["primary_release_year"] = year
        
        return await self._make_request("/discover/movie", params)
    
    def get_poster_url(self, poster_path: Optional[str], size: str = "w500") -> Optional[str]:
        """
        Génère l'URL complète d'un poster
        
        Args:
            poster_path: Chemin du poster (ex: "/abc123.jpg")
            size: Taille de l'image (w185, w342, w500, w780, original)
        
        Returns:
            URL complète ou None
        """
        if not poster_path:
            return None
        return f"{self.image_base_url}/{size}{poster_path}"
    
    def get_backdrop_url(self, backdrop_path: Optional[str], size: str = "w1280") -> Optional[str]:
        """
        Génère l'URL complète d'un backdrop
        
        Args:
            backdrop_path: Chemin du backdrop
            size: Taille de l'image (w300, w780, w1280, original)
        
        Returns:
            URL complète ou None
        """
        if not backdrop_path:
            return None
        return f"{self.image_base_url}/{size}{backdrop_path}"
    
    def save_movie_to_db(self, db: Session, movie_data: Dict[str, Any]) -> Movie:
        """
        Sauvegarde un film depuis TMDB dans la base de données
        
        Args:
            db: Session de base de données
            movie_data: Données du film depuis TMDB
        
        Returns:
            Movie créé ou existant
        """
        movie_id = movie_data["id"]
        
        # Vérifier si le film existe déjà
        existing_movie = db.query(Movie).filter(Movie.id == movie_id).first()
        
        if existing_movie:
            return existing_movie
        
        # Créer le film
        movie = Movie(
            id=movie_id,
            title=movie_data.get("title"),
            original_title=movie_data.get("original_title"),
            overview=movie_data.get("overview"),
            release_date=movie_data.get("release_date"),
            poster_path=movie_data.get("poster_path"),
            backdrop_path=movie_data.get("backdrop_path"),
            vote_average=movie_data.get("vote_average"),
            vote_count=movie_data.get("vote_count"),
            popularity=movie_data.get("popularity"),
            original_language=movie_data.get("original_language"),
            runtime=movie_data.get("runtime"),
            budget=movie_data.get("budget"),
            revenue=movie_data.get("revenue"),
            status=movie_data.get("status"),
            tagline=movie_data.get("tagline")
        )
        
        db.add(movie)
        
        # Ajouter les genres
        if "genres" in movie_data:
            for genre_data in movie_data["genres"]:
                genre_id = genre_data["id"]
                
                # Vérifier si le genre existe
                genre = db.query(Genre).filter(Genre.id == genre_id).first()
                
                if not genre:
                    genre = Genre(id=genre_id, name=genre_data["name"])
                    db.add(genre)
                
                # Créer la relation
                movie_genre = MovieGenre(movie_id=movie_id, genre_id=genre_id)
                db.add(movie_genre)
        
        # Gérer les genres depuis genre_ids (recherche/discover)
        elif "genre_ids" in movie_data:
            for genre_id in movie_data["genre_ids"]:
                # Le genre doit déjà exister (initialisé dans init.sql)
                genre = db.query(Genre).filter(Genre.id == genre_id).first()
                
                if genre:
                    movie_genre = MovieGenre(movie_id=movie_id, genre_id=genre_id)
                    db.add(movie_genre)
        
        db.commit()
        db.refresh(movie)
        
        return movie