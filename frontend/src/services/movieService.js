import api from './api'

const movieService = {
  // Rechercher des films
  searchMovies: async (query, page = 1) => {
    const response = await api.get('/movies/search', {
      params: { query, page },
    })
    return response.data
  },

  // Films populaires
  getPopularMovies: async (page = 1) => {
    const response = await api.get('/movies/popular', {
      params: { page },
    })
    return response.data
  },

  // Films les mieux notés
  getTopRatedMovies: async (page = 1) => {
    const response = await api.get('/movies/top-rated', {
      params: { page },
    })
    return response.data
  },

  // Films au cinéma
  getNowPlayingMovies: async (page = 1) => {
    const response = await api.get('/movies/now-playing', {
      params: { page },
    })
    return response.data
  },

  // Découvrir des films avec filtres
  discoverMovies: async (filters = {}) => {
    const response = await api.get('/movies/discover', {
      params: filters,
    })
    return response.data
  },

  // Détails d'un film
  getMovieDetails: async (movieId) => {
    const response = await api.get(`/movies/${movieId}`)
    return response.data
  },

  // Liste des genres
  getGenres: async () => {
    const response = await api.get('/movies/genres')
    return response.data
  },

  // URL de l'image TMDB
  getImageUrl: (path, size = 'w500') => {
    if (!path) return '/placeholder-movie.png'
    return `https://image.tmdb.org/t/p/${size}${path}`
  },
}

export default movieService