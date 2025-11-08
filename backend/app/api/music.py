"""
Routes API pour la musique (Spotify)
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.music import Track, MusicRating
from app.schemas.music import (
    TrackResponse,
    SpotifySearchResponse,
    MusicRatingCreate,
    MusicRatingUpdate,
    MusicRatingResponse
)
from app.services.spotify_service import SpotifyService

router = APIRouter(prefix="/music", tags=["Music"])
spotify_service = SpotifyService()


@router.get("/search", response_model=SpotifySearchResponse)
async def search_music(
    query: str,
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Recherche de musique via Spotify
    
    Args:
        query: Terme de recherche
        limit: Nombre de résultats (1-50)
        offset: Index de départ
        db: Session de base de données
    """
    try:
        search_results = await spotify_service.search_tracks(query, limit, offset)
        
        # Convertir les résultats en modèles de base de données
        tracks = []
        for track_data in search_results["tracks"]["items"]:
            track = spotify_service.save_track_to_db(db, track_data)
            tracks.append(track)
        
        return {
            "items": tracks,
            "total": search_results["tracks"]["total"],
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erreur lors de la recherche Spotify: {str(e)}"
        )


@router.get("/track/{track_id}", response_model=TrackResponse)
async def get_track_details(
    track_id: str,
    db: Session = Depends(get_db)
):
    """
    Récupère les détails d'une piste
    
    Args:
        track_id: ID Spotify de la piste
        db: Session de base de données
    """
    try:
        track_data = await spotify_service.get_track(track_id)
        track = spotify_service.save_track_to_db(db, track_data)
        return track
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erreur lors de la récupération de la piste: {str(e)}"
        )


@router.get("/recommendations", response_model=List[TrackResponse])
async def get_recommendations(
    seed_tracks: Optional[str] = Query(None, description="IDs de pistes (max 5, séparés par des virgules)"),
    seed_artists: Optional[str] = Query(None, description="IDs d'artistes (max 5, séparés par des virgules)"),
    seed_genres: Optional[str] = Query(None, description="Genres (max 5, séparés par des virgules)"),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtient des recommandations musicales basées sur les notes de l'utilisateur
    
    Note: L'API Spotify /recommendations nécessite OAuth utilisateur.
    On utilise donc une alternative: recherche basée sur les artistes notés.
    
    Args:
        seed_tracks: IDs de pistes comme seeds (non utilisé - fallback)
        seed_artists: IDs d'artistes comme seeds
        seed_genres: Genres comme seeds
        limit: Nombre de recommandations
        current_user: Utilisateur actuel
        db: Session de base de données
    """
    try:
        # Récupérer les pistes les mieux notées de l'utilisateur
        top_ratings = db.query(MusicRating).options(
            joinedload(MusicRating.track)
        ).filter(
            MusicRating.user_id == current_user.id,
            MusicRating.rating >= 4
        ).order_by(MusicRating.rating.desc()).limit(5).all()
        
        tracks = []
        
        if top_ratings:
            # Extraire les artistes des pistes les mieux notées
            artists = list(set([rating.track.artist for rating in top_ratings if rating.track]))
            
            # Rechercher des pistes similaires pour chaque artiste
            for artist in artists[:3]:  # Limiter à 3 artistes
                try:
                    search_results = await spotify_service.search_tracks(
                        query=f"artist:{artist}",
                        limit=7,
                        offset=0
                    )
                    
                    for track_data in search_results["tracks"]["items"]:
                        # Éviter les doublons et les pistes déjà notées
                        track_spotify_id = track_data["id"]
                        already_rated = any(r.track.spotify_id == track_spotify_id for r in top_ratings)
                        
                        if not already_rated and track_spotify_id not in [t.spotify_id for t in tracks]:
                            track = spotify_service.save_track_to_db(db, track_data)
                            tracks.append(track)
                            
                            if len(tracks) >= limit:
                                break
                except Exception as e:
                    print(f"[RECOMMENDATIONS] Error searching for artist {artist}: {str(e)}")
                    continue
                
                if len(tracks) >= limit:
                    break
        
        # Si pas assez de recommandations, compléter avec des nouveautés
        if len(tracks) < limit:
            try:
                releases = await spotify_service.get_new_releases(limit=limit - len(tracks), offset=0)
                for album in releases["albums"]["items"]:
                    if album["id"] and len(tracks) < limit:
                        track_data = {
                            "id": album["id"],
                            "name": album["name"],
                            "artists": album["artists"],
                            "album": album,
                            "preview_url": None,
                            "duration_ms": None,
                            "popularity": None
                        }
                        track = spotify_service.save_track_to_db(db, track_data)
                        tracks.append(track)
            except Exception as e:
                print(f"[RECOMMENDATIONS] Error getting new releases: {str(e)}")
        
        return tracks[:limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erreur lors de la récupération des recommandations: {str(e)}"
        )


@router.get("/new-releases", response_model=List[TrackResponse])
async def get_new_releases(
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Récupère les nouvelles sorties
    
    Args:
        limit: Nombre de résultats
        offset: Index de départ
        db: Session de base de données
    """
    try:
        releases = await spotify_service.get_new_releases(limit, offset)
        
        # Sauvegarder et convertir en modèles de base de données
        tracks = []
        for album in releases["albums"]["items"]:
            # Pour chaque album, on récupère la première piste
            if album["id"]:
                track_data = {
                    "id": album["id"],
                    "name": album["name"],
                    "artists": album["artists"],
                    "album": album,
                    "preview_url": None,  # Nécessiterait un appel API supplémentaire
                    "duration_ms": None,  # Nécessiterait un appel API supplémentaire
                    "popularity": None    # Nécessiterait un appel API supplémentaire
                }
                track = spotify_service.save_track_to_db(db, track_data)
                tracks.append(track)
        
        return tracks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erreur lors de la récupération des nouveautés: {str(e)}"
        )


@router.post("/ratings", response_model=MusicRatingResponse)
async def rate_track(
    rating: MusicRatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Note une piste musicale
    
    Args:
        rating: Données de la note
        current_user: Utilisateur actuel
        db: Session de base de données
    """
    # Vérifier si la piste existe
    track = db.query(Track).filter(Track.id == rating.track_id).first()
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Piste non trouvée"
        )
    
    # Vérifier si une note existe déjà
    existing_rating = db.query(MusicRating).filter(
        MusicRating.user_id == current_user.id,
        MusicRating.track_id == rating.track_id
    ).first()
    
    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous avez déjà noté cette piste"
        )
    
    # Créer la note
    db_rating = MusicRating(
        user_id=current_user.id,
        track_id=rating.track_id,
        rating=rating.rating
    )
    
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    
    # Charger explicitement la relation track
    db.refresh(db_rating, ['track'])
    
    return db_rating


@router.put("/ratings/{rating_id}", response_model=MusicRatingResponse)
async def update_rating(
    rating_id: int,
    rating_update: MusicRatingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Met à jour une note musicale
    
    Args:
        rating_id: ID de la note
        rating_update: Nouvelle note
        current_user: Utilisateur actuel
        db: Session de base de données
    """
    # Récupérer la note existante
    db_rating = db.query(MusicRating).filter(
        MusicRating.id == rating_id,
        MusicRating.user_id == current_user.id
    ).first()
    
    if not db_rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note non trouvée ou non autorisée"
        )
    
    # Mettre à jour la note
    db_rating.rating = rating_update.rating
    db.commit()
    db.refresh(db_rating)
    
    # Charger explicitement la relation track
    db.refresh(db_rating, ['track'])
    
    return db_rating


@router.delete("/ratings/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rating(
    rating_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Supprime une note musicale
    
    Args:
        rating_id: ID de la note
        current_user: Utilisateur actuel
        db: Session de base de données
    """
    # Récupérer la note existante
    db_rating = db.query(MusicRating).filter(
        MusicRating.id == rating_id,
        MusicRating.user_id == current_user.id
    ).first()
    
    if not db_rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note non trouvée ou non autorisée"
        )
    
    # Supprimer la note
    db.delete(db_rating)
    db.commit()


@router.get("/ratings/me", response_model=List[MusicRatingResponse])
async def get_my_ratings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les notes musicales de l'utilisateur actuel
    
    Args:
        current_user: Utilisateur actuel
        db: Session de base de données
    """
    ratings = db.query(MusicRating).options(
        joinedload(MusicRating.track)
    ).filter(
        MusicRating.user_id == current_user.id
    ).all()
    
    return ratings