import { useState } from 'react'
import { motion } from 'framer-motion'
import { Star, Calendar, TrendingUp } from 'lucide-react'
import movieService from '../../services/movieService'
import RatingStars from './RatingStars'

const MovieCard = ({ movie, onRate, userRating }) => {
  const [showRating, setShowRating] = useState(false)
  const [isHovered, setIsHovered] = useState(false)

  const posterUrl = movieService.getImageUrl(movie.poster_path, 'w500')
  const releaseYear = movie.release_date ? new Date(movie.release_date).getFullYear() : 'N/A'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -8 }}
      transition={{ duration: 0.3 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      className="relative group"
    >
      <div className="card card-hover overflow-hidden">
        {/* Poster */}
        <div className="relative aspect-[2/3] overflow-hidden bg-dark-hover">
          <img
            src={posterUrl}
            alt={movie.title}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
            loading="lazy"
            onError={(e) => {
              e.target.src = '/placeholder-movie.png'
            }}
          />
          
          {/* Overlay au hover */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: isHovered ? 1 : 0 }}
            className="absolute inset-0 bg-gradient-to-t from-dark-bg via-dark-bg/80 to-transparent flex flex-col justify-end p-4"
          >
            {/* Genres */}
            {movie.genres && movie.genres.length > 0 && (
              <div className="flex flex-wrap gap-1 mb-2">
                {movie.genres.slice(0, 2).map((genre) => (
                  <span
                    key={genre.id}
                    className="badge badge-primary text-xs"
                  >
                    {genre.name}
                  </span>
                ))}
              </div>
            )}

            {/* Rating Button */}
            <button
              onClick={() => setShowRating(!showRating)}
              className="btn btn-primary w-full text-sm py-2"
            >
              {userRating ? `Votre note: ${userRating}⭐` : 'Noter ce film'}
            </button>
          </motion.div>

          {/* Note TMDB */}
          {movie.vote_average && (
            <div className="absolute top-2 right-2 bg-dark-card/90 backdrop-blur-sm px-2 py-1 rounded-lg flex items-center space-x-1">
              <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
              <span className="text-sm font-semibold text-white">
                {movie.vote_average.toFixed(1)}
              </span>
            </div>
          )}
        </div>

        {/* Info */}
        <div className="p-4">
          <h3 className="font-semibold text-white mb-1 line-clamp-2 group-hover:text-primary-400 transition-colors">
            {movie.title}
          </h3>
          
          <div className="flex items-center justify-between text-xs text-gray-400">
            <div className="flex items-center space-x-1">
              <Calendar className="w-3 h-3" />
              <span>{releaseYear}</span>
            </div>
            
            {movie.popularity && (
              <div className="flex items-center space-x-1">
                <TrendingUp className="w-3 h-3" />
                <span>{Math.round(movie.popularity)}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Rating Modal */}
      {showRating && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="absolute inset-0 z-10 flex items-center justify-center bg-dark-bg/95 backdrop-blur-sm rounded-xl"
        >
          <div className="text-center p-6">
            <h4 className="text-white font-semibold mb-4">
              Noter "{movie.title}"
            </h4>
            <RatingStars
              movieId={movie.id}
              initialRating={userRating}
              onRate={(rating) => {
                onRate(movie.id, rating)
                setShowRating(false)
              }}
            />
            <button
              onClick={() => setShowRating(false)}
              className="mt-4 text-sm text-gray-400 hover:text-white transition-colors"
            >
              Annuler
            </button>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}

export default MovieCard