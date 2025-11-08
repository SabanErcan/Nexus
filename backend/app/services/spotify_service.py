"""
Service Spotify - Interaction avec l'API Spotify
"""

import base64
import httpx
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models.music import Track


class SpotifyService:
    """
    Service pour interagir avec l'API Spotify
    Documentation: https://developer.spotify.com/documentation/web-api
    """
    
    def __init__(self):
        self.base_url = "https://api.spotify.com/v1"
        self.auth_url = "https://accounts.spotify.com/api/token"
        self.client_id = settings.spotify_client_id
        self.client_secret = settings.spotify_client_secret
        self._access_token = None
    
    async def _get_access_token(self) -> str:
        """
        Obtient un access token via Client Credentials Flow
        
        Returns:
            Access token Spotify
        """
        if not self.client_id or not self.client_secret:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Spotify credentials are not configured. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in backend/.env"
            )
        
        # Encode client_id:client_secret en Base64
        auth_bytes = f"{self.client_id}:{self.client_secret}".encode("ascii")
        auth_b64 = base64.b64encode(auth_bytes).decode("ascii")
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {"grant_type": "client_credentials"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.auth_url,
                    headers=headers,
                    data=data,
                    timeout=10.0
                )
                response.raise_for_status()
                self._access_token = response.json()["access_token"]
                return self._access_token
            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Spotify authentication failed: {str(e)}"
                )
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Fait une requête à l'API Spotify
        
        Args:
            endpoint: Endpoint de l'API (ex: "/search")
            params: Paramètres de la requête
        
        Returns:
            Réponse JSON de l'API
        """
        if not self._access_token:
            await self._get_access_token()
        
        if params is None:
            params = {}
        
        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self._access_token}"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=10.0
                )
                
                # Si token expiré, en obtenir un nouveau
                if response.status_code == 401:
                    self._access_token = await self._get_access_token()
                    headers["Authorization"] = f"Bearer {self._access_token}"
                    response = await client.get(url, params=params, headers=headers)
                
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Spotify API error: {str(e)}"
                )
    
    async def search_tracks(self, query: str, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Recherche de pistes musicales
        
        Args:
            query: Terme de recherche
            limit: Nombre de résultats
            offset: Index de départ
        
        Returns:
            Résultats de recherche Spotify
        """
        params = {
            "q": query,
            "type": "track",
            "limit": limit,
            "offset": offset,
            "market": "FR"  # Filtrer pour la France
        }
        return await self._make_request("/search", params)
    
    async def get_track(self, track_id: str) -> Dict[str, Any]:
        """
        Récupère les détails d'une piste
        
        Args:
            track_id: ID Spotify de la piste
        
        Returns:
            Détails de la piste
        """
        return await self._make_request(f"/tracks/{track_id}")
    
    async def get_recommendations(
        self,
        seed_tracks: Optional[List[str]] = None,
        seed_artists: Optional[List[str]] = None,
        seed_genres: Optional[List[str]] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Obtient des recommandations basées sur des seeds
        
        Args:
            seed_tracks: IDs de pistes (max 5)
            seed_artists: IDs d'artistes (max 5)
            seed_genres: Genres (max 5)
            limit: Nombre de recommandations
        
        Returns:
            Pistes recommandées
        """
        params = {"limit": limit}
        
        if seed_tracks:
            params["seed_tracks"] = ",".join(seed_tracks[:5])
        if seed_artists:
            params["seed_artists"] = ",".join(seed_artists[:5])
        if seed_genres:
            params["seed_genres"] = ",".join(seed_genres[:5])
        
        return await self._make_request("/recommendations", params)
    
    async def get_new_releases(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Récupère les nouvelles sorties
        
        Args:
            limit: Nombre de résultats
            offset: Index de départ
        
        Returns:
            Nouvelles sorties
        """
        params = {
            "limit": limit,
            "offset": offset,
            "country": "FR"
        }
        return await self._make_request("/browse/new-releases", params)
    
    def save_track_to_db(self, db: Session, track_data: Dict[str, Any]) -> Track:
        """
        Sauvegarde une piste Spotify dans la base de données
        
        Args:
            db: Session de base de données
            track_data: Données de la piste depuis Spotify
        
        Returns:
            Track créé ou existant
        """
        spotify_id = track_data["id"]
        
        # Vérifier si la piste existe déjà
        existing_track = db.query(Track).filter(Track.spotify_id == spotify_id).first()
        
        if existing_track:
            return existing_track
        
        # Extraire les données de la piste
        album = track_data.get("album", {})
        artists = track_data.get("artists", [])
        
        track = Track(
            spotify_id=spotify_id,
            title=track_data["name"],
            artist=artists[0]["name"] if artists else "Unknown Artist",
            album=album.get("name"),
            release_year=int(album.get("release_date", "0")[:4]) if album.get("release_date") else None,
            preview_url=track_data.get("preview_url"),
            image_url=album.get("images", [{}])[0].get("url") if album.get("images") else None,
            duration_ms=track_data.get("duration_ms"),
            popularity=track_data.get("popularity"),
            genres=[]  # Les genres nécessitent un appel API supplémentaire à /artists/{id}
        )
        
        db.add(track)
        db.commit()
        db.refresh(track)
        
        return track