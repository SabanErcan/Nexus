import { useState, useEffect } from 'react';
import { Book, Star } from 'lucide-react';
import { motion } from 'framer-motion';
import bookService from '../services/bookService';
import BookGrid from '../components/Books/BookGrid';
import Loading from '../components/Common/Loading';

/**
 * Page affichant les livres notés par l'utilisateur
 */
const BookRatings = () => {
  const [ratings, setRatings] = useState([]);
  const [ratingsMap, setRatingsMap] = useState({});
  const [ratedBooks, setRatedBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, average: 0, topRated: 0 });

  useEffect(() => {
    loadRatings();
  }, []);

  const loadRatings = async () => {
    try {
      const data = await bookService.getMyRatings();
      setRatings(data);

      // Créer le map {bookId: {ratingId, rating}}
      const map = {};
      const books = [];

      data.forEach((rating) => {
        map[rating.book.id] = {
          ratingId: rating.id,
          rating: rating.rating,
          review: rating.review
        };
        books.push(rating.book);
      });

      setRatingsMap(map);
      setRatedBooks(books);

      // Calculer les statistiques
      const total = data.length;
      const average = total > 0 
        ? data.reduce((sum, r) => sum + r.rating, 0) / total 
        : 0;
      const topRated = data.filter(r => r.rating >= 4).length;

      setStats({ total, average, topRated });
    } catch (error) {
      console.error('Erreur chargement notes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRate = async (bookId, newRating) => {
    try {
      const ratingInfo = ratingsMap[bookId];
      
      if (ratingInfo) {
        // Mettre à jour la note existante
        await bookService.updateRating(ratingInfo.ratingId, newRating);
        
        // Mettre à jour l'état local
        setRatingsMap(prev => ({
          ...prev,
          [bookId]: { ...prev[bookId], rating: newRating }
        }));

        // Recalculer les stats
        const updatedRatings = ratings.map(r => 
          r.book.id === bookId ? { ...r, rating: newRating } : r
        );
        const total = updatedRatings.length;
        const average = total > 0 
          ? updatedRatings.reduce((sum, r) => sum + r.rating, 0) / total 
          : 0;
        const topRated = updatedRatings.filter(r => r.rating >= 4).length;
        setStats({ total, average, topRated });
      }
    } catch (error) {
      console.error('Erreur mise à jour note:', error);
    }
  };

  if (loading) return <Loading />;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* En-tête */}
        <div className="flex items-center gap-3 mb-8">
          <Book className="w-8 h-8 text-amber-500" />
          <h1 className="text-3xl font-bold text-white">Mes livres notés</h1>
        </div>

        {/* Statistiques */}
        {stats.total > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {/* Total */}
            <motion.div
              className="bg-gradient-to-br from-amber-900 to-amber-800 p-6 rounded-lg shadow-lg"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-amber-200 text-sm font-medium">Total</p>
                  <p className="text-4xl font-bold text-white mt-2">{stats.total}</p>
                </div>
                <Book className="w-12 h-12 text-amber-300 opacity-50" />
              </div>
            </motion.div>

            {/* Moyenne */}
            <motion.div
              className="bg-gradient-to-br from-yellow-900 to-yellow-800 p-6 rounded-lg shadow-lg"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-yellow-200 text-sm font-medium">Note moyenne</p>
                  <p className="text-4xl font-bold text-white mt-2">{stats.average.toFixed(1)}</p>
                  <p className="text-yellow-300 text-xs mt-1">sur 5 étoiles</p>
                </div>
                <Star className="w-12 h-12 text-yellow-300 opacity-50" />
              </div>
            </motion.div>

            {/* Favoris */}
            <motion.div
              className="bg-gradient-to-br from-orange-900 to-orange-800 p-6 rounded-lg shadow-lg"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-orange-200 text-sm font-medium">Coups de cœur</p>
                  <p className="text-4xl font-bold text-white mt-2">{stats.topRated}</p>
                  <p className="text-orange-300 text-xs mt-1">≥ 4 étoiles</p>
                </div>
                <div className="flex">
                  <Star className="w-12 h-12 text-orange-300 opacity-50" />
                  <Star className="w-12 h-12 text-orange-300 opacity-50 -ml-4" />
                </div>
              </div>
            </motion.div>
          </div>
        )}

        {/* Grille de livres */}
        {ratedBooks.length === 0 ? (
          <div className="text-center py-12">
            <Book className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 text-lg">Vous n'avez pas encore noté de livres</p>
            <p className="text-gray-500 text-sm mt-2">
              Recherchez des livres et commencez à les noter !
            </p>
          </div>
        ) : (
          <BookGrid books={ratedBooks} onRate={handleRate} ratingsMap={ratingsMap} />
        )}
      </div>
    </div>
  );
};

export default BookRatings;
