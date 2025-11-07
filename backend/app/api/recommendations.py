"""
Routes pour les recommandations
Générer, consulter, expliquer les recommandations
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.recommendation import RecommendationResponse, RecommendationExplanation
from app.schemas.movie import MovieResponse
from app.dependencies import get_current_user
from app.models.user import User
from app.models.recommendation import Recommendation
from app.models.movie import Movie
from app.services.recommendation_engine import RecommendationEngine


router = APIRouter()


@router.post("/generate", response_model=dict, status_code=status.HTTP_201_CREATED)
async def generate_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Génère de nouvelles recommandations pour l'utilisateur connecté
    
    Utilise l'algorithme hybride (filtrage collaboratif + basé contenu)
    
    Nécessite au moins 3 films notés pour des recommandations personnalisées.
    Sinon, retourne des films populaires.
    """
    engine = RecommendationEngine(db)
    recommendations = engine.generate_recommendations(current_user.id)
    
    return {
        "message": f"Generated {len(recommendations)} recommendations",
        "count": len(recommendations),
        "recommendations_ids": [r.movie_id for r in recommendations]
    }


@router.get("/", response_model=List[RecommendationResponse])
async def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=50, description="Nombre de recommandations à retourner")
):
    """
    Récupère les recommandations de l'utilisateur connecté
    
    - **limit**: Nombre maximum de recommandations (défaut: 20, max: 50)
    
    Retourne les recommandations triées par score décroissant avec les détails des films
    """
    recommendations = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id
    ).order_by(Recommendation.score.desc()).limit(limit).all()
    
    if not recommendations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No recommendations found. Please generate recommendations first or rate more movies."
        )
    
    # Construire la réponse avec les films
    result = []
    for rec in recommendations:
        movie = db.query(Movie).filter(Movie.id == rec.movie_id).first()
        
        if movie:
            movie_response = MovieResponse.model_validate(movie)
            result.append(RecommendationResponse(
                id=rec.id,
                user_id=rec.user_id,
                movie_id=rec.movie_id,
                score=float(rec.score),
                algorithm_type=rec.algorithm_type,
                explanation=rec.explanation,
                created_at=rec.created_at,
                is_viewed=rec.is_viewed,
                is_dismissed=rec.is_dismissed,
                movie=movie_response
            ))
    
    return result


@router.get("/explain/{movie_id}", response_model=RecommendationExplanation)
async def explain_recommendation(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Explique pourquoi un film est recommandé
    
    - **movie_id**: ID TMDB du film
    
    Retourne l'explication détaillée avec les films/utilisateurs similaires
    """
    # Récupérer la recommandation
    recommendation = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id,
        Recommendation.movie_id == movie_id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No recommendation found for this movie"
        )
    
    # Récupérer le film
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    # Construire l'explication détaillée
    explanation = RecommendationExplanation(
        movie_id=movie_id,
        movie_title=movie.title,
        score=float(recommendation.score),
        algorithm_type=recommendation.algorithm_type,
        explanation=recommendation.explanation or "Recommandation basée sur vos préférences"
    )
    
    return explanation


@router.patch("/{recommendation_id}/view", response_model=RecommendationResponse)
async def mark_recommendation_as_viewed(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Marque une recommandation comme vue
    
    - **recommendation_id**: ID de la recommandation
    """
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == current_user.id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    recommendation.is_viewed = True
    db.commit()
    db.refresh(recommendation)
    
    # Récupérer le film pour la réponse
    movie = db.query(Movie).filter(Movie.id == recommendation.movie_id).first()
    movie_response = MovieResponse.model_validate(movie)
    
    return RecommendationResponse(
        id=recommendation.id,
        user_id=recommendation.user_id,
        movie_id=recommendation.movie_id,
        score=float(recommendation.score),
        algorithm_type=recommendation.algorithm_type,
        explanation=recommendation.explanation,
        created_at=recommendation.created_at,
        is_viewed=recommendation.is_viewed,
        is_dismissed=recommendation.is_dismissed,
        movie=movie_response
    )


@router.patch("/{recommendation_id}/dismiss", response_model=RecommendationResponse)
async def dismiss_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Rejette une recommandation (ne plus la montrer)
    
    - **recommendation_id**: ID de la recommandation
    """
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == current_user.id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    recommendation.is_dismissed = True
    db.commit()
    db.refresh(recommendation)
    
    movie = db.query(Movie).filter(Movie.id == recommendation.movie_id).first()
    movie_response = MovieResponse.model_validate(movie)
    
    return RecommendationResponse(
        id=recommendation.id,
        user_id=recommendation.user_id,
        movie_id=recommendation.movie_id,
        score=float(recommendation.score),
        algorithm_type=recommendation.algorithm_type,
        explanation=recommendation.explanation,
        created_at=recommendation.created_at,
        is_viewed=recommendation.is_viewed,
        is_dismissed=recommendation.is_dismissed,
        movie=movie_response
    )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_all_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Supprime toutes les recommandations de l'utilisateur
    
    Utile avant de regénérer de nouvelles recommandations
    """
    db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id
    ).delete()
    
    db.commit()
    
    return None