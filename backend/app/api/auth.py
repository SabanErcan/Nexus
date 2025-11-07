"""
Routes d'authentification
Register, Login, Get Current User
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, UserWithStats
from app.services.auth_service import AuthService
from app.dependencies import get_current_user
from app.models.user import User
from app.models.user_preference import UserMoviePreference
from app.config import settings


router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Inscription d'un nouvel utilisateur
    
    - **username**: Nom d'utilisateur unique (3-50 caractères)
    - **email**: Email unique
    - **password**: Mot de passe (minimum 6 caractères)
    """
    user = AuthService.create_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )
    
    return user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Connexion d'un utilisateur
    
    - **email**: Email de l'utilisateur
    - **password**: Mot de passe
    
    Retourne un token JWT Bearer à utiliser dans le header Authorization
    """
    # Authentifier l'utilisateur
    user = AuthService.authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Créer le token JWT
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = AuthService.create_access_token(
        data={"user_id": user.id, "email": user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserWithStats)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les informations de l'utilisateur connecté avec statistiques
    
    Requiert un token JWT valide dans le header Authorization
    """
    # Récupérer les préférences/stats
    preferences = db.query(UserMoviePreference).filter(
        UserMoviePreference.user_id == current_user.id
    ).first()
    
    user_data = UserResponse.model_validate(current_user)
    
    # Ajouter les stats si elles existent
    if preferences:
        return UserWithStats(
            **user_data.model_dump(),
            total_ratings=preferences.total_ratings,
            average_rating=float(preferences.average_rating) if preferences.average_rating else None,
            highly_rated_count=preferences.highly_rated_count,
            favorite_genres=preferences.favorite_genres
        )
    
    return UserWithStats(**user_data.model_dump())


@router.get("/test", status_code=status.HTTP_200_OK)
async def test_auth():
    """
    Endpoint de test pour vérifier que l'API d'authentification fonctionne
    """
    return {"message": "Auth API is working!"}