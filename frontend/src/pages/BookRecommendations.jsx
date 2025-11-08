import { useState, useEffect } from 'react';
import { Sparkles, Book } from 'lucide-react';
import bookService from '../services/bookService';
import BookGrid from '../components/Books/BookGrid';
import Loading from '../components/Common/Loading';

/**
 * Page de recommandations de livres personnalisées
 */
const BookRecommendations = () => {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await bookService.getRecommendations(20);
      console.log('📚 Recommandations chargées:', data.length, 'livres');
      setBooks(data);
    } catch (err) {
      console.error('Erreur chargement recommandations:', err);
      setError('Impossible de charger les recommandations');
    } finally {
      setLoading(false);
    }
  };

  const handleRate = async (bookId, rating) => {
    try {
      await bookService.rateBook(bookId, rating);
      // Recharger les recommandations après notation
      loadRecommendations();
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
      <div className="max-w-7xl mx-auto">
        {/* En-tête */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <Sparkles className="w-8 h-8 text-amber-500" />
            <h1 className="text-3xl font-bold text-white">Recommandations pour vous</h1>
          </div>
          <p className="text-gray-400">
            Découvrez des livres sélectionnés selon vos goûts littéraires
          </p>
        </div>

        {/* Message d'erreur */}
        {error && (
          <div className="bg-red-900 bg-opacity-50 border border-red-700 text-red-200 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* Recommandations */}
        {books.length === 0 ? (
          <div className="text-center py-12">
            <Book className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 text-lg mb-2">Aucune recommandation disponible</p>
            <p className="text-gray-500 text-sm">
              Notez quelques livres pour recevoir des recommandations personnalisées !
            </p>
          </div>
        ) : (
          <>
            <div className="mb-6">
              <p className="text-gray-300">
                {books.length} livre{books.length > 1 ? 's' : ''} recommandé{books.length > 1 ? 's' : ''} 
                {' '}basé sur vos lectures
              </p>
            </div>
            <BookGrid books={books} onRate={handleRate} />
          </>
        )}
      </div>
    </div>
  );
};

export default BookRecommendations;
