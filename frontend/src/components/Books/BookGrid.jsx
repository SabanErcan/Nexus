import BookCard from './BookCard';

/**
 * Grille d'affichage pour plusieurs livres
 */
const BookGrid = ({ books, onRate, ratingsMap = {}, showRating = true }) => {
  if (!books || books.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        <p>Aucun livre à afficher</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {books.map((book) => (
        <BookCard
          key={book.id}
          book={book}
          onRate={onRate}
          initialRating={ratingsMap[book.id]?.rating || 0}
          showRating={showRating}
        />
      ))}
    </div>
  );
};

export default BookGrid;
