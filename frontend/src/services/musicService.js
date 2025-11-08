import api from './api';

/**
 * Service pour interagir avec l'API musicale
 */
export const musicService = {
    /**
     * Recherche des pistes musicales
     * @param {string} query - Terme de recherche
     * @param {number} limit - Nombre de résultats
     * @param {number} offset - Index de départ
     * @returns {Promise} Résultats de recherche
     */
    searchTracks: async (query, limit = 20, offset = 0) => {
        const response = await api.get(`/music/search`, {
            params: { query, limit, offset }
        });
        return response.data;
    },

    /**
     * Récupère les détails d'une piste
     * @param {string} trackId - ID Spotify de la piste
     * @returns {Promise} Détails de la piste
     */
    getTrackDetails: async (trackId) => {
        const response = await api.get(`/music/track/${trackId}`);
        return response.data;
    },

    /**
     * Obtient des recommandations musicales
     * @param {Object} params - Paramètres de recommandation
     * @returns {Promise} Pistes recommandées
     */
    getRecommendations: async ({ seedTracks, seedArtists, seedGenres, limit = 20 }) => {
        const response = await api.get(`/music/recommendations`, {
            params: {
                seed_tracks: seedTracks?.join(','),
                seed_artists: seedArtists?.join(','),
                seed_genres: seedGenres?.join(','),
                limit
            }
        });
        return response.data;
    },

    /**
     * Récupère les nouvelles sorties
     * @param {number} limit - Nombre de résultats
     * @param {number} offset - Index de départ
     * @returns {Promise} Nouvelles sorties
     */
    getNewReleases: async (limit = 20, offset = 0) => {
        const response = await api.get(`/music/new-releases`, {
            params: { limit, offset }
        });
        return response.data;
    },

    /**
     * Note une piste musicale
     * @param {number} trackId - ID de la piste
     * @param {number} rating - Note (1-5)
     * @returns {Promise} Note créée
     */
    rateTrack: async (trackId, rating) => {
        const response = await api.post(`/music/ratings`, {
            track_id: trackId,
            rating
        });
        return response.data;
    },

    /**
     * Met à jour une note musicale
     * @param {number} ratingId - ID de la note
     * @param {number} rating - Nouvelle note (1-5)
     * @returns {Promise} Note mise à jour
     */
    updateRating: async (ratingId, rating) => {
        const response = await api.put(`/music/ratings/${ratingId}`, { rating });
        return response.data;
    },

    /**
     * Supprime une note musicale
     * @param {number} ratingId - ID de la note
     * @returns {Promise} void
     */
    deleteRating: async (ratingId) => {
        await api.delete(`/music/ratings/${ratingId}`);
    },

    /**
     * Récupère les notes de l'utilisateur
     * @returns {Promise} Liste des notes
     */
    getUserRatings: async () => {
        const response = await api.get(`/music/ratings/me`);
        return response.data;
    }
};