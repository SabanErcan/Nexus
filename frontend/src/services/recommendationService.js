import api from './api'

const recommendationService = {
  // Générer de nouvelles recommandations
  generateRecommendations: async () => {
    const response = await api.post('/recommendations/generate')
    return response.data
  },

  // Récupérer les recommandations
  getRecommendations: async (limit = 20) => {
    const response = await api.get('/recommendations/', {
      params: { limit },
    })
    return response.data
  },

  // Expliquer une recommandation
  explainRecommendation: async (movieId) => {
    const response = await api.get(`/recommendations/explain/${movieId}`)
    return response.data
  },

  // Marquer une recommandation comme vue
  markAsViewed: async (recommendationId) => {
    const response = await api.patch(`/recommendations/${recommendationId}/view`)
    return response.data
  },

  // Rejeter une recommandation
  dismissRecommendation: async (recommendationId) => {
    const response = await api.patch(`/recommendations/${recommendationId}/dismiss`)
    return response.data
  },

  // Supprimer toutes les recommandations
  clearRecommendations: async () => {
    await api.delete('/recommendations/')
  },
}

export default recommendationService