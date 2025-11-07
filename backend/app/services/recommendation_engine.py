"""
Moteur de Recommandation Hybride
Combine filtrage collaboratif et filtrage basé sur le contenu
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

from app.config import settings
from app.models.user import User
from app.models.movie import Movie, MovieGenre
from app.models.rating import Rating
from app.models.recommendation import Recommendation
from app.models.similarity import UserSimilarity, MovieSimilarity


class RecommendationEngine:
    """
    Moteur de recommandation hybride
    
    Algorithmes:
    1. Filtrage collaboratif (User-Based): Trouve des utilisateurs similaires
    2. Filtrage basé contenu (Content-Based): Trouve des films similaires
    3. Hybride: Combine les deux avec pondération
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.collaborative_weight = settings.collaborative_weight
        self.content_weight = settings.content_weight
        self.min_ratings = settings.min_ratings_for_recommendations
        self.recommendations_count = settings.recommendations_count
        self.min_similarity = settings.min_similarity_score
    
    def generate_recommendations(self, user_id: int) -> List[Recommendation]:
        """
        Génère des recommandations hybrides pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Liste de recommandations triées par score décroissant
        """
        # Vérifier que l'utilisateur a assez de notes
        user_ratings_count = self.db.query(Rating).filter(Rating.user_id == user_id).count()
        
        if user_ratings_count < self.min_ratings:
            # Pas assez de données, recommander les films populaires
            return self._recommend_popular_movies(user_id)
        
        # 1. Calculer les scores collaboratifs
        collaborative_scores = self._collaborative_filtering(user_id)
        
        # 2. Calculer les scores basés contenu
        content_scores = self._content_based_filtering(user_id)
        
        # 3. Combiner les scores (hybride)
        hybrid_scores = self._combine_scores(collaborative_scores, content_scores)
        
        # 4. Filtrer les films déjà notés
        rated_movie_ids = {r.movie_id for r in self.db.query(Rating.movie_id).filter(Rating.user_id == user_id).all()}
        
        # 5. Trier et limiter
        recommendations = []
        for movie_id, score in sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True):
            if movie_id not in rated_movie_ids:
                explanation = self._generate_explanation(user_id, movie_id, collaborative_scores, content_scores)
                
                recommendation = Recommendation(
                    user_id=user_id,
                    movie_id=movie_id,
                    score=round(score, 3),
                    algorithm_type="hybrid",
                    explanation=explanation
                )
                
                recommendations.append(recommendation)
                
                if len(recommendations) >= self.recommendations_count:
                    break
        
        # Sauvegarder en BDD
        self._save_recommendations(recommendations)
        
        return recommendations
    
    def _collaborative_filtering(self, user_id: int) -> Dict[int, float]:
        """
        Filtrage collaboratif (User-Based)
        Trouve des utilisateurs similaires et recommande ce qu'ils ont aimé
        
        Returns:
            Dict {movie_id: score}
        """
        # 1. Calculer la similarité avec les autres utilisateurs
        similar_users = self._calculate_user_similarity(user_id)
        
        if not similar_users:
            return {}
        
        # 2. Récupérer les films aimés par les utilisateurs similaires
        scores = defaultdict(float)
        
        for similar_user_id, similarity_score in similar_users:
            # Récupérer les films bien notés (4-5) par cet utilisateur
            highly_rated = self.db.query(Rating).filter(
                and_(
                    Rating.user_id == similar_user_id,
                    Rating.rating >= 4
                )
            ).all()
            
            for rating in highly_rated:
                # Score = similarité × note normalisée
                normalized_rating = rating.rating / 5.0
                scores[rating.movie_id] += similarity_score * normalized_rating
        
        # Normaliser les scores
        if scores:
            max_score = max(scores.values())
            scores = {k: v / max_score for k, v in scores.items()}
        
        return scores
    
    def _content_based_filtering(self, user_id: int) -> Dict[int, float]:
        """
        Filtrage basé sur le contenu
        Recommande des films similaires à ceux que l'utilisateur a aimés
        
        Returns:
            Dict {movie_id: score}
        """
        # 1. Récupérer les films aimés par l'utilisateur (4-5 étoiles)
        liked_movies = self.db.query(Rating).filter(
            and_(
                Rating.user_id == user_id,
                Rating.rating >= 4
            )
        ).all()
        
        if not liked_movies:
            return {}
        
        # 2. Calculer la similarité basée sur les genres
        scores = defaultdict(float)
        
        for rating in liked_movies:
            similar_movies = self._find_similar_movies(rating.movie_id)
            
            for similar_movie_id, similarity_score in similar_movies:
                # Pondérer par la note donnée
                normalized_rating = rating.rating / 5.0
                scores[similar_movie_id] += similarity_score * normalized_rating
        
        # Normaliser
        if scores:
            max_score = max(scores.values())
            scores = {k: v / max_score for k, v in scores.items()}
        
        return scores
    
    def _calculate_user_similarity(self, user_id: int) -> List[Tuple[int, float]]:
        """
        Calcule la similarité entre l'utilisateur et les autres
        Utilise la similarité cosinus sur les notes communes
        
        Returns:
            Liste de (user_id, similarity_score) triée par similarité décroissante
        """
        # Récupérer les notes de l'utilisateur
        user_ratings = self.db.query(Rating).filter(Rating.user_id == user_id).all()
        user_ratings_dict = {r.movie_id: r.rating for r in user_ratings}
        
        if not user_ratings_dict:
            return []
        
        # Récupérer tous les autres utilisateurs ayant noté au moins un film en commun
        other_users = self.db.query(Rating.user_id).filter(
            and_(
                Rating.user_id != user_id,
                Rating.movie_id.in_(user_ratings_dict.keys())
            )
        ).distinct().all()
        
        similarities = []
        
        for (other_user_id,) in other_users:
            # Récupérer les notes de l'autre utilisateur
            other_ratings = self.db.query(Rating).filter(Rating.user_id == other_user_id).all()
            other_ratings_dict = {r.movie_id: r.rating for r in other_ratings}
            
            # Trouver les films en commun
            common_movies = set(user_ratings_dict.keys()) & set(other_ratings_dict.keys())
            
            if len(common_movies) < 2:  # Au moins 2 films en commun
                continue
            
            # Calculer la similarité cosinus
            user_vector = [user_ratings_dict[m] for m in common_movies]
            other_vector = [other_ratings_dict[m] for m in common_movies]
            
            similarity = cosine_similarity([user_vector], [other_vector])[0][0]
            
            if similarity >= self.min_similarity:
                similarities.append((other_user_id, similarity))
        
        # Trier par similarité décroissante et limiter
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:10]  # Top 10 utilisateurs similaires
    
    def _find_similar_movies(self, movie_id: int) -> List[Tuple[int, float]]:
        """
        Trouve des films similaires basés sur les genres
        
        Returns:
            Liste de (movie_id, similarity_score)
        """
        # Récupérer les genres du film
        movie_genres = self.db.query(MovieGenre.genre_id).filter(
            MovieGenre.movie_id == movie_id
        ).all()
        
        genre_ids = [g[0] for g in movie_genres]
        
        if not genre_ids:
            return []
        
        # Trouver des films avec des genres similaires
        similar_movies_query = self.db.query(
            MovieGenre.movie_id,
            func.count(MovieGenre.genre_id).label('common_genres')
        ).filter(
            and_(
                MovieGenre.genre_id.in_(genre_ids),
                MovieGenre.movie_id != movie_id
            )
        ).group_by(MovieGenre.movie_id).all()
        
        # Calculer le score de similarité (Jaccard)
        similarities = []
        total_genres = len(genre_ids)
        
        for similar_movie_id, common_genres_count in similar_movies_query:
            # Récupérer le nombre total de genres du film similaire
            similar_movie_genres_count = self.db.query(MovieGenre).filter(
                MovieGenre.movie_id == similar_movie_id
            ).count()
            
            # Similarité de Jaccard
            union = total_genres + similar_movie_genres_count - common_genres_count
            similarity = common_genres_count / union if union > 0 else 0
            
            if similarity >= self.min_similarity:
                similarities.append((similar_movie_id, similarity))
        
        # Trier par similarité décroissante
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:20]  # Top 20 films similaires
    
    def _combine_scores(
        self,
        collaborative_scores: Dict[int, float],
        content_scores: Dict[int, float]
    ) -> Dict[int, float]:
        """
        Combine les scores collaboratifs et basés contenu
        Score final = (weight_collab × score_collab) + (weight_content × score_content)
        
        Returns:
            Dict {movie_id: combined_score}
        """
        combined = {}
        all_movie_ids = set(collaborative_scores.keys()) | set(content_scores.keys())
        
        for movie_id in all_movie_ids:
            collab_score = collaborative_scores.get(movie_id, 0)
            content_score = content_scores.get(movie_id, 0)
            
            combined[movie_id] = (
                self.collaborative_weight * collab_score +
                self.content_weight * content_score
            )
        
        return combined
    
    def _generate_explanation(
        self,
        user_id: int,
        movie_id: int,
        collaborative_scores: Dict[int, float],
        content_scores: Dict[int, float]
    ) -> str:
        """
        Génère une explication pour la recommandation
        
        Returns:
            Texte d'explication
        """
        explanations = []
        
        # Explication basée sur le contenu
        if movie_id in content_scores and content_scores[movie_id] > 0.3:
            # Trouver un film similaire bien noté
            liked_movies = self.db.query(Movie.title, Rating.rating).join(
                Rating, Rating.movie_id == Movie.id
            ).filter(
                and_(
                    Rating.user_id == user_id,
                    Rating.rating >= 4
                )
            ).limit(3).all()
            
            if liked_movies:
                titles = ", ".join([m[0] for m in liked_movies[:2]])
                explanations.append(f"Parce que vous avez aimé {titles}")
        
        # Explication collaborative
        if movie_id in collaborative_scores and collaborative_scores[movie_id] > 0.3:
            explanations.append("Recommandé par des utilisateurs ayant des goûts similaires")
        
        return " et ".join(explanations) if explanations else "Recommandation basée sur vos préférences"
    
    def _recommend_popular_movies(self, user_id: int) -> List[Recommendation]:
        """
        Recommande les films populaires (cold start)
        Utilisé quand l'utilisateur n'a pas assez de notes
        
        Returns:
            Liste de recommandations basées sur la popularité
        """
        # Récupérer les films populaires non notés
        rated_movie_ids = {r.movie_id for r in self.db.query(Rating.movie_id).filter(Rating.user_id == user_id).all()}
        
        popular_movies = self.db.query(Movie).filter(
            ~Movie.id.in_(rated_movie_ids)
        ).order_by(Movie.popularity.desc()).limit(self.recommendations_count).all()
        
        recommendations = []
        for movie in popular_movies:
            recommendation = Recommendation(
                user_id=user_id,
                movie_id=movie.id,
                score=0.5,  # Score neutre
                algorithm_type="popular",
                explanation="Film populaire - Notez plus de films pour des recommandations personnalisées"
            )
            recommendations.append(recommendation)
        
        self._save_recommendations(recommendations)
        return recommendations
    
    def _save_recommendations(self, recommendations: List[Recommendation]):
        """Sauvegarde les recommandations en base de données"""
        if not recommendations:
            return
        
        user_id = recommendations[0].user_id
        
        # Supprimer les anciennes recommandations
        self.db.query(Recommendation).filter(Recommendation.user_id == user_id).delete()
        
        # Ajouter les nouvelles
        self.db.add_all(recommendations)
        self.db.commit()