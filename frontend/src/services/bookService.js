import api from './api';

/**
 * Service pour les livres (Google Books API)
 */
const bookService = {
  /**
   * Rechercher des livres
   */
  searchBooks: async (query, limit = 20, offset = 0) => {
    const response = await api.get('/books/search', {
      params: { query, limit, offset }
    });
    return response.data;
  },

  /**
   * Obtenir les détails d'un livre
   */
  getBook: async (bookId) => {
    const response = await api.get(`/books/book/${bookId}`);
    return response.data;
  },

  /**
   * Obtenir des recommandations de livres
   */
  getRecommendations: async (limit = 20) => {
    const response = await api.get('/books/recommendations', {
      params: { limit }
    });
    return response.data;
  },

  /**
   * Noter un livre
   */
  rateBook: async (bookId, rating, review = null) => {
    const response = await api.post('/books/ratings', {
      book_id: bookId,
      rating,
      review
    });
    return response.data;
  },

  /**
   * Mettre à jour une note de livre
   */
  updateRating: async (ratingId, rating, review = null) => {
    const response = await api.put(`/books/ratings/${ratingId}`, {
      rating,
      review
    });
    return response.data;
  },

  /**
   * Supprimer une note de livre
   */
  deleteRating: async (ratingId) => {
    await api.delete(`/books/ratings/${ratingId}`);
  },

  /**
   * Obtenir mes notes de livres
   */
  getMyRatings: async () => {
    const response = await api.get('/books/ratings/me');
    return response.data;
  }
};

export default bookService;
