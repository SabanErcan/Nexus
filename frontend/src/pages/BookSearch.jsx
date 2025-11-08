import { useState, useEffect } from 'react';
import { Search } from 'lucide-react';
import bookService from '../services/bookService';
import BookGrid from '../components/Books/BookGrid';
import SearchBar from '../components/Common/SearchBar';
import Loading from '../components/Common/Loading';

/**
 * Page de recherche de livres
 */
const BookSearch = () => {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Charger des livres populaires au démarrage
  useEffect(() => {
    loadPopularBooks();
  }, []);

  const loadPopularBooks = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await bookService.searchBooks('bestseller', 20);
      setBooks(response.items);
    } catch (err) {
      console.error('Erreur chargement livres populaires:', err);
      setError('Impossible de charger les livres');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query) => {
    if (!query.trim()) {
      loadPopularBooks();
      return;
    }

    setLoading(true);
    setError(null);
    setSearchQuery(query);

    try {
      const response = await bookService.searchBooks(query, 20);
      setBooks(response.items);
    } catch (err) {
      console.error('Erreur recherche:', err);
      setError('Erreur lors de la recherche');
    } finally {
      setLoading(false);
    }
  };

  const handleRate = async (bookId, rating) => {
    try {
      await bookService.rateBook(bookId, rating);
      // Optionnel : afficher un message de succès
    } catch (err) {
      console.error('Erreur notation:', err);
      if (err.response?.status === 400) {
        alert('Vous avez déjà noté ce livre');
      }
    }
  };

  if (loading) return <Loading />;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      {/* En-tête */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center gap-3 mb-6">
          <Search className="w-8 h-8 text-amber-500" />
          <h1 className="text-3xl font-bold text-white">Rechercher des livres</h1>
        </div>

        {/* Barre de recherche */}
        <SearchBar
          placeholder="Rechercher un livre, un auteur, un ISBN..."
          onSearch={handleSearch}
        />
      </div>

      {/* Message d'erreur */}
      {error && (
        <div className="max-w-7xl mx-auto mb-6">
          <div className="bg-red-900 bg-opacity-50 border border-red-700 text-red-200 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      )}

      {/* Résultats */}
      <div className="max-w-7xl mx-auto">
        {!searchQuery && (
          <h2 className="text-xl font-semibold text-white mb-6">
            Livres populaires
          </h2>
        )}
        {searchQuery && (
          <h2 className="text-xl font-semibold text-white mb-6">
            Résultats pour "{searchQuery}"
          </h2>
        )}

        <BookGrid books={books} onRate={handleRate} />
      </div>
    </div>
  );
};

export default BookSearch;
