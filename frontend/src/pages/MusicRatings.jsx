import React from 'react';
import MusicGrid from '../components/Music/MusicGrid';
import { musicService } from '../services/musicService';

/**
 * Page des notes musicales de l'utilisateur
 */
const MusicRatings = () => {
    const [ratings, setRatings] = React.useState([]);
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
        const loadRatings = async () => {
            try {
                const userRatings = await musicService.getUserRatings();
                setRatings(userRatings);
            } catch (error) {
                console.error('Error loading ratings:', error);
            } finally {
                setLoading(false);
            }
        };

        loadRatings();
    }, []);

    const handleRatingChange = async (trackId, rating) => {
        try {
            const existingRating = ratings.find((r) => r.track_id === trackId);
            
            if (existingRating) {
                if (rating === 0) {
                    // Supprimer la note
                    await musicService.deleteRating(existingRating.id);
                    setRatings(ratings.filter((r) => r.id !== existingRating.id));
                } else {
                    // Mettre à jour la note
                    const updatedRating = await musicService.updateRating(existingRating.id, rating);
                    setRatings(ratings.map((r) => 
                        r.id === updatedRating.id ? updatedRating : r
                    ));
                }
            }
        } catch (error) {
            console.error('Error updating rating:', error);
        }
    };

    const tracks = ratings.map((rating) => rating.track);

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold text-gray-800 dark:text-white mb-8">
                Mes notes musicales
            </h1>

            <MusicGrid
                tracks={tracks}
                loading={loading}
                onRatingChange={handleRatingChange}
                userRatings={ratings}
            />

            {!loading && tracks.length === 0 && (
                <div className="text-center text-gray-600 dark:text-gray-300 mt-8">
                    Vous n'avez pas encore noté de musique
                </div>
            )}
        </div>
    );
};

export default MusicRatings;