import React from 'react';
import MusicGrid from '../components/Music/MusicGrid';
import { musicService } from '../services/musicService';

/**
 * Page de découverte musicale
 */
const MusicDiscover = () => {
    const [newReleases, setNewReleases] = React.useState([]);
    const [recommendations, setRecommendations] = React.useState([]);
    const [userRatings, setUserRatings] = React.useState([]);
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
        const loadContent = async () => {
            try {
                // Charger les notes de l'utilisateur
                const ratings = await musicService.getUserRatings();
                setUserRatings(ratings);

                // Charger les nouvelles sorties
                const releases = await musicService.getNewReleases(10);
                setNewReleases(releases);

                // Si l'utilisateur a des notes, charger les recommandations
                if (ratings.length > 0) {
                    // Utiliser les 5 dernières notes comme seeds
                    const seedTracks = ratings
                        .sort((a, b) => b.rating - a.rating)
                        .slice(0, 5)
                        .map(rating => rating.track.spotify_id);

                    const recs = await musicService.getRecommendations({
                        seedTracks,
                        limit: 10
                    });
                    setRecommendations(recs);
                }
            } catch (error) {
                console.error('Error loading content:', error);
            } finally {
                setLoading(false);
            }
        };

        loadContent();
    }, []);

    const handleRatingChange = async (trackId, rating) => {
        try {
            const existingRating = userRatings.find((r) => r.track_id === trackId);
            
            if (existingRating) {
                const updatedRating = await musicService.updateRating(existingRating.id, rating);
                setUserRatings(userRatings.map((r) => 
                    r.id === updatedRating.id ? updatedRating : r
                ));
            } else {
                const newRating = await musicService.rateTrack(trackId, rating);
                setUserRatings([...userRatings, newRating]);
            }
        } catch (error) {
            console.error('Error updating rating:', error);
        }
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-8">
                Découvrir de la musique
            </h1>

            {recommendations.length > 0 && (
                <>
                    <h2 className="text-2xl font-semibold text-gray-700 dark:text-gray-200 mb-4">
                        Recommandé pour vous
                    </h2>
                    <MusicGrid
                        tracks={recommendations}
                        loading={loading}
                        onRatingChange={handleRatingChange}
                        userRatings={userRatings}
                    />
                </>
            )}

            <h2 className="text-2xl font-semibold text-gray-700 dark:text-gray-200 mb-4 mt-8">
                Nouveautés
            </h2>
            <MusicGrid
                tracks={newReleases}
                loading={loading}
                onRatingChange={handleRatingChange}
                userRatings={userRatings}
            />

            {!loading && newReleases.length === 0 && recommendations.length === 0 && (
                <div className="text-center text-gray-600 dark:text-gray-300 mt-8">
                    Aucune musique à découvrir pour le moment
                </div>
            )}
        </div>
    );
};

export default MusicDiscover;