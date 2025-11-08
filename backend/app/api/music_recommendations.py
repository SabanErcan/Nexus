"""
Routes API pour les recommandations musicales
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.recommendation import MusicRecommendationResponse
from app.services.music_recommendation_engine import MusicRecommendationEngine
from app.models.recommendation import MusicRecommendation


router = APIRouter(prefix="/music-recommendations", tags=["Music Recommendations"])


@router.get("", response_model=List[MusicRecommendationResponse])
async def get_music_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les recommandations musicales pour l'utilisateur connecté
    
    Args:
        current_user: Utilisateur connecté
        db: Session de base de données
    """
    engine = MusicRecommendationEngine(db)
    recommendations = engine.generate_recommendations(current_user.id)
    return recommendations


@router.post("/{recommendation_id}/viewed")
async def mark_recommendation_viewed(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Marque une recommandation comme vue
    
    Args:
        recommendation_id: ID de la recommandation
        current_user: Utilisateur connecté
        db: Session de base de données
    """
    recommendation = db.query(MusicRecommendation).filter(
        MusicRecommendation.id == recommendation_id,
        MusicRecommendation.user_id == current_user.id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommandation non trouvée"
        )
    
    recommendation.is_viewed = True
    db.commit()
    return {"success": True}


@router.post("/{recommendation_id}/dismissed")
async def dismiss_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ignore une recommandation
    
    Args:
        recommendation_id: ID de la recommandation
        current_user: Utilisateur connecté
        db: Session de base de données
    """
    recommendation = db.query(MusicRecommendation).filter(
        MusicRecommendation.id == recommendation_id,
        MusicRecommendation.user_id == current_user.id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommandation non trouvée"
        )
    
    recommendation.is_dismissed = True
    db.commit()
    return {"success": True}