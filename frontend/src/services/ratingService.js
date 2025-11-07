import api from './api'

const ratingService = {
  // Créer ou mettre à jour une note
  rateMovie: async (movieId, rating) => {
    const response = await api.post('/ratings/', {
      movie_id: movieId,
      rating,
    })
    return response.data
  },

  // Récupérer toutes les notes de l'utilisateur
  getUserRatings: async (skip = 0, limit = 100) => {
    const response = await api.get('/ratings/', {
      params: { skip, limit },
    })
    return response.data
  },

  // Récupérer les statistiques de notation
  getUserRatingStats: async () => {
    const response = await api.get('/ratings/stats')
    return response.data
  },

  // Mettre à jour une note
  updateRating: async (ratingId, rating) => {
    const response = await api.put(`/ratings/${ratingId}`, { rating })
    return response.data
  },

  // Supprimer une note
  deleteRating: async (ratingId) => {
    await api.delete(`/ratings/${ratingId}`)
  },

  // Récupérer la note d'un film spécifique
  getRatingForMovie: async (movieId) => {
    try {
      const response = await api.get(`/ratings/movie/${movieId}`)
      return response.data
    } catch (error) {
      if (error.response?.status === 404) {
        return null
      }
      throw error
    }
  },
}

export default ratingService