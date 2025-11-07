import MovieCard from './MovieCard'

const MovieGrid = ({ movies, onRate, userRatings = {} }) => {
  if (!movies || movies.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">Aucun film trouvé</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 md:gap-6">
      {movies.map((movie) => (
        <MovieCard
          key={movie.id}
          movie={movie}
          onRate={onRate}
          userRating={userRatings[movie.id]}
        />
      ))}
    </div>
  )
}

export default MovieGrid