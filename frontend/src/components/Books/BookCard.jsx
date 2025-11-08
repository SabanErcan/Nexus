import { motion } from 'framer-motion';
import { Book, Calendar, User } from 'lucide-react';
import RatingStars from '../Movies/RatingStars';

/**
 * Carte d'affichage pour un livre
 */
const BookCard = ({ book, onRate, initialRating = 0, showRating = true }) => {
  // Extraire les auteurs
  const authors = Array.isArray(book.authors) ? book.authors.join(', ') : 'Auteur inconnu';
  
  // Formater la date de publication
  const publishedYear = book.published_date ? book.published_date.substring(0, 4) : 'N/A';
  
  return (
    <motion.div
      className="bg-gray-800 rounded-lg overflow-hidden shadow-lg hover:shadow-2xl transition-shadow duration-300"
      whileHover={{ y: -5 }}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {/* Image de couverture */}
      <div className="relative h-64 bg-gray-700">
        {book.image_url ? (
          <img
            src={book.image_url}
            alt={book.title}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = 'https://via.placeholder.com/300x450?text=No+Cover';
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Book className="w-16 h-16 text-gray-500" />
          </div>
        )}
        
        {/* Badge nombre de pages */}
        {book.page_count && (
          <div className="absolute top-2 right-2 bg-black bg-opacity-75 text-white px-2 py-1 rounded text-xs">
            {book.page_count} pages
          </div>
        )}
      </div>
      
      {/* Informations du livre */}
      <div className="p-4">
        {/* Titre */}
        <h3 className="text-lg font-semibold text-white mb-2 line-clamp-2">
          {book.title}
        </h3>
        
        {/* Auteurs */}
        <div className="flex items-center text-gray-400 text-sm mb-2">
          <User className="w-4 h-4 mr-1" />
          <span className="line-clamp-1">{authors}</span>
        </div>
        
        {/* Date et éditeur */}
        <div className="flex items-center justify-between text-gray-400 text-xs mb-3">
          {publishedYear !== 'N/A' && (
            <div className="flex items-center">
              <Calendar className="w-3 h-3 mr-1" />
              <span>{publishedYear}</span>
            </div>
          )}
          {book.publisher && (
            <span className="line-clamp-1">{book.publisher}</span>
          )}
        </div>
        
        {/* Description courte */}
        {book.description && (
          <p className="text-gray-400 text-sm mb-3 line-clamp-3">
            {book.description}
          </p>
        )}
        
        {/* Catégories */}
        {book.categories && book.categories.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {book.categories.slice(0, 2).map((category, index) => (
              <span
                key={index}
                className="bg-amber-900 bg-opacity-50 text-amber-300 px-2 py-1 rounded text-xs"
              >
                {category}
              </span>
            ))}
          </div>
        )}
        
        {/* Système de notation */}
        {showRating && onRate && (
          <div className="mt-4">
            <RatingStars
              initialRating={initialRating}
              onRate={(rating) => onRate(book.id, rating)}
            />
          </div>
        )}
        
        {/* Note Google Books */}
        {book.average_rating && (
          <div className="mt-2 text-xs text-gray-500">
            ⭐ {book.average_rating.toFixed(1)} Google Books
            {book.ratings_count && ` (${book.ratings_count} avis)`}
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default BookCard;
