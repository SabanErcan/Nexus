"""
Moteur de Recommandation Musicale
Combine filtrage collaboratif et basé sur le contenu pour la musique
"""

import numpy as np
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

from app.config import settings
from app.models.user import User
from app.models.music import Track, MusicRating
from app.models.recommendation import MusicRecommendation


class MusicRecommendationEngine:
    """
    Moteur de recommandation musicale hybride
    
    Algorithmes:
    1. Filtrage collaboratif (User-Based): Trouve des utilisateurs aux goûts similaires
    2. Filtrage basé contenu (Content-Based): Trouve des pistes similaires
    3. Hybride: Combine les deux approches avec pondération
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.collaborative_weight = settings.collaborative_weight
        self.content_weight = settings.content_weight
        self.min_ratings = settings.min_ratings_for_recommendations
        self.recommendations_count = settings.recommendations_count
        self.min_similarity = settings.min_similarity_score
    
    def generate_recommendations(self, user_id: int) -> List[MusicRecommendation]:
        """
        Génère des recommandations hybrides pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Liste de recommandations triées par score décroissant
        """
        # Vérifier que l'utilisateur a assez de notes
        user_ratings_count = self.db.query(MusicRating).filter(MusicRating.user_id == user_id).count()
        
        if user_ratings_count < self.min_ratings:
            # Pas assez de données, recommander les pistes populaires
            return self._recommend_popular_tracks(user_id)
        
        # 1. Calculer les scores collaboratifs
        collaborative_scores = self._collaborative_filtering(user_id)
        
        # 2. Calculer les scores basés contenu
        content_scores = self._content_based_filtering(user_id)
        
        # 3. Combiner les scores (hybride)
        hybrid_scores = self._combine_scores(collaborative_scores, content_scores)
        
        # 4. Filtrer les pistes déjà notées
        rated_track_ids = {r.track_id for r in self.db.query(MusicRating.track_id).filter(MusicRating.user_id == user_id).all()}
        
        # 5. Trier et limiter
        recommendations = []
        for track_id, score in sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True):
            if track_id not in rated_track_ids:
                explanation = self._generate_explanation(user_id, track_id, collaborative_scores, content_scores)
                
                recommendation = MusicRecommendation(
                    user_id=user_id,
                    track_id=track_id,
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
            Dict {track_id: score}
        """
        # 1. Calculer la similarité avec les autres utilisateurs
        similar_users = self._calculate_user_similarity(user_id)
        
        if not similar_users:
            return {}
        
        # 2. Récupérer les pistes aimées par les utilisateurs similaires
        scores = defaultdict(float)
        
        for similar_user_id, similarity_score in similar_users:
            # Récupérer les pistes bien notées (4-5) par cet utilisateur
            highly_rated = self.db.query(MusicRating).filter(
                and_(
                    MusicRating.user_id == similar_user_id,
                    MusicRating.rating >= 4
                )
            ).all()
            
            for rating in highly_rated:
                # Score = similarité × note normalisée
                normalized_rating = rating.rating / 5.0
                scores[rating.track_id] += similarity_score * normalized_rating
        
        # Normaliser les scores
        if scores:
            max_score = max(scores.values())
            scores = {k: v / max_score for k, v in scores.items()}
        
        return scores
    
    def _content_based_filtering(self, user_id: int) -> Dict[int, float]:
        """
        Filtrage basé sur le contenu
        Recommande des pistes similaires à celles que l'utilisateur a aimées
        
        Returns:
            Dict {track_id: score}
        """
        # 1. Récupérer les pistes aimées par l'utilisateur (4-5 étoiles)
        liked_tracks = self.db.query(MusicRating).filter(
            and_(
                MusicRating.user_id == user_id,
                MusicRating.rating >= 4
            )
        ).all()
        
        if not liked_tracks:
            return {}
        
        # 2. Calculer la similarité basée sur les genres et artistes
        scores = defaultdict(float)
        
        for rating in liked_tracks:
            similar_tracks = self._find_similar_tracks(rating.track_id)
            
            for similar_track_id, similarity_score in similar_tracks:
                # Pondérer par la note donnée
                normalized_rating = rating.rating / 5.0
                scores[similar_track_id] += similarity_score * normalized_rating
        
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
        user_ratings = self.db.query(MusicRating).filter(MusicRating.user_id == user_id).all()
        user_ratings_dict = {r.track_id: r.rating for r in user_ratings}
        
        if not user_ratings_dict:
            return []
        
        # Récupérer tous les autres utilisateurs ayant noté au moins une piste en commun
        other_users = self.db.query(MusicRating.user_id).filter(
            and_(
                MusicRating.user_id != user_id,
                MusicRating.track_id.in_(user_ratings_dict.keys())
            )
        ).distinct().all()
        
        similarities = []
        
        for (other_user_id,) in other_users:
            # Récupérer les notes de l'autre utilisateur
            other_ratings = self.db.query(MusicRating).filter(MusicRating.user_id == other_user_id).all()
            other_ratings_dict = {r.track_id: r.rating for r in other_ratings}
            
            # Trouver les pistes en commun
            common_tracks = set(user_ratings_dict.keys()) & set(other_ratings_dict.keys())
            
            if len(common_tracks) < 2:  # Au moins 2 pistes en commun
                continue
            
            # Calculer la similarité cosinus
            user_vector = [user_ratings_dict[t] for t in common_tracks]
            other_vector = [other_ratings_dict[t] for t in common_tracks]
            
            similarity = cosine_similarity([user_vector], [other_vector])[0][0]
            
            if similarity >= self.min_similarity:
                similarities.append((other_user_id, similarity))
        
        # Trier par similarité décroissante et limiter
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:10]  # Top 10 utilisateurs similaires
    
    def _find_similar_tracks(self, track_id: int) -> List[Tuple[int, float]]:
        """
        Trouve des pistes similaires basées sur les genres et l'artiste
        
        Returns:
            Liste de (track_id, similarity_score)
        """
        # Récupérer les informations de la piste
        track = self.db.query(Track).filter(Track.id == track_id).first()
        
        if not track or not track.genres:
            return []
        
        # Trouver des pistes avec des genres similaires et/ou même artiste
        similar_tracks_query = self.db.query(
            Track.id,
            func.count(func.unnest(Track.genres)).label('common_genres')
        ).filter(
            and_(
                Track.id != track_id,
                Track.genres.overlap(track.genres)  # Postgres specific
            )
        ).group_by(Track.id).all()
        
        # Calculer le score de similarité (Jaccard pour genres + bonus artiste)
        similarities = []
        total_genres = len(track.genres)
        
        for similar_track_id, common_genres_count in similar_tracks_query:
            similar_track = self.db.query(Track).filter(Track.id == similar_track_id).first()
            
            # Similarité de Jaccard pour les genres
            union = total_genres + len(similar_track.genres) - common_genres_count
            genre_similarity = common_genres_count / union if union > 0 else 0
            
            # Bonus si même artiste
            artist_bonus = 0.3 if similar_track.artist == track.artist else 0
            
            # Score final
            similarity = min(1.0, genre_similarity + artist_bonus)
            
            if similarity >= self.min_similarity:
                similarities.append((similar_track_id, similarity))
        
        # Trier par similarité décroissante
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:20]  # Top 20 pistes similaires
    
    def _combine_scores(
        self,
        collaborative_scores: Dict[int, float],
        content_scores: Dict[int, float]
    ) -> Dict[int, float]:
        """
        Combine les scores collaboratifs et basés contenu
        Score final = (weight_collab × score_collab) + (weight_content × score_content)
        
        Returns:
            Dict {track_id: combined_score}
        """
        combined = {}
        all_track_ids = set(collaborative_scores.keys()) | set(content_scores.keys())
        
        for track_id in all_track_ids:
            collab_score = collaborative_scores.get(track_id, 0)
            content_score = content_scores.get(track_id, 0)
            
            combined[track_id] = (
                self.collaborative_weight * collab_score +
                self.content_weight * content_score
            )
        
        return combined
    
    def _generate_explanation(
        self,
        user_id: int,
        track_id: int,
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
        if track_id in content_scores and content_scores[track_id] > 0.3:
            # Trouver une piste similaire bien notée
            liked_tracks = self.db.query(Track.title, Track.artist, MusicRating.rating).join(
                MusicRating, MusicRating.track_id == Track.id
            ).filter(
                and_(
                    MusicRating.user_id == user_id,
                    MusicRating.rating >= 4
                )
            ).limit(3).all()
            
            if liked_tracks:
                tracks_info = [f"{t[0]} par {t[1]}" for t in liked_tracks[:2]]
                explanations.append(f"Parce que vous avez aimé {', '.join(tracks_info)}")
        
        # Explication collaborative
        if track_id in collaborative_scores and collaborative_scores[track_id] > 0.3:
            explanations.append("Recommandé par des utilisateurs ayant des goûts similaires")
        
        return " et ".join(explanations) if explanations else "Recommandation basée sur vos préférences"
    
    def _recommend_popular_tracks(self, user_id: int) -> List[MusicRecommendation]:
        """
        Recommande les pistes populaires (cold start)
        Utilisé quand l'utilisateur n'a pas assez de notes
        
        Returns:
            Liste de recommandations basées sur la popularité
        """
        # Récupérer les pistes populaires non notées
        rated_track_ids = {r.track_id for r in self.db.query(MusicRating.track_id).filter(MusicRating.user_id == user_id).all()}
        
        popular_tracks = self.db.query(Track).filter(
            ~Track.id.in_(rated_track_ids)
        ).order_by(Track.popularity.desc()).limit(self.recommendations_count).all()
        
        recommendations = []
        for track in popular_tracks:
            recommendation = MusicRecommendation(
                user_id=user_id,
                track_id=track.id,
                score=0.5,  # Score neutre
                algorithm_type="popular",
                explanation="Piste populaire - Notez plus de pistes pour des recommandations personnalisées"
            )
            recommendations.append(recommendation)
        
        self._save_recommendations(recommendations)
        return recommendations
    
    def _save_recommendations(self, recommendations: List[MusicRecommendation]):
        """Sauvegarde les recommandations en base de données"""
        if not recommendations:
            return
        
        user_id = recommendations[0].user_id
        
        # Supprimer les anciennes recommandations
        self.db.query(MusicRecommendation).filter(MusicRecommendation.user_id == user_id).delete()
        
        # Ajouter les nouvelles
        self.db.add_all(recommendations)
        self.db.commit()