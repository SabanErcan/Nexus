"""
Service d'authentification - JWT et hashing de mots de passe
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User
from app.schemas.user import TokenData


# Configuration du hashing - utiliser Argon2 (supporte les mots de passe longs)
# Argon2 est moderne et ne souffre pas de la limite de 72 octets de bcrypt.
# On garde bcrypt_sha256 et bcrypt en fallback pour compatibilité.
pwd_context = CryptContext(schemes=["argon2", "bcrypt_sha256", "bcrypt"], deprecated="auto")


class AuthService:
    """
    Service pour gérer l'authentification et les tokens JWT
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash un mot de passe avec bcrypt"""
        # Use the configured pwd_context (argon2 primary). Don't truncate here
        # because Argon2 supports arbitrary-length passwords. Keep try/except
        # to surface friendly errors.
        try:
            return pwd_context.hash(password)
        except ValueError as e:
            # Surface a clearer HTTPException so the API client gets a readable error.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=("Password is too long for bcrypt (max 72 bytes). "
                        "Use a shorter password or contact the administrator."),
            ) from e
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Vérifie un mot de passe contre son hash"""
        # Verify using the same context. Argon2 doesn't require truncation.
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Crée un token JWT
        
        Args:
            data: Données à encoder dans le token (user_id, email, etc.)
            expires_delta: Durée de validité du token
        
        Returns:
            Token JWT encodé
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        
        return encoded_jwt
    
    @staticmethod
    def decode_access_token(token: str) -> TokenData:
        """
        Décode un token JWT et extrait les données
        
        Args:
            token: Token JWT à décoder
        
        Returns:
            TokenData avec user_id et email
        
        Raises:
            HTTPException: Si le token est invalide ou expiré
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id: int = payload.get("user_id")
            email: str = payload.get("email")
            
            if user_id is None or email is None:
                raise credentials_exception
            
            return TokenData(user_id=user_id, email=email)
        
        except JWTError:
            raise credentials_exception
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authentifie un utilisateur
        
        Args:
            db: Session de base de données
            email: Email de l'utilisateur
            password: Mot de passe en clair
        
        Returns:
            User si authentification réussie, None sinon
        """
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        if not AuthService.verify_password(password, user.password_hash):
            return None
        
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Récupère un utilisateur par email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Récupère un utilisateur par username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Récupère un utilisateur par ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str) -> User:
        """
        Crée un nouvel utilisateur
        
        Args:
            db: Session de base de données
            username: Nom d'utilisateur
            email: Email
            password: Mot de passe en clair (sera hashé)
        
        Returns:
            User créé
        
        Raises:
            HTTPException: Si l'email ou le username existe déjà
        """
        # Vérifier si l'email existe déjà
        if AuthService.get_user_by_email(db, email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Vérifier si le username existe déjà
        if AuthService.get_user_by_username(db, username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Créer l'utilisateur
        hashed_password = AuthService.hash_password(password)
        user = User(
            username=username,
            email=email,
            password_hash=hashed_password
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user