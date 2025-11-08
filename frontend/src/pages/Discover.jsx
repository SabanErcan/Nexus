import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Filter } from 'lucide-react'
import movieService from '../services/movieService'
import ratingService from '../services/ratingService'
import MovieGrid from '../components/Movies/MovieGrid'
import SearchBar from '../components/Common/SearchBar'
import Loading from '../components/Common/Loading'
import toast from 'react-hot-toast'

const Discover = () => {
  const [movies, setMovies] = useState([])
  const [genres, setGenres] = useState([])
  const [selectedGenres, setSelectedGenres] = useState([])
  const [userRatings, setUserRatings] = useState({})
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
    try {
      setLoading(true)
      const [popularMovies, genresList, ratings] = await Promise.all([
        movieService.getPopularMovies(),
        movieService.getGenres(),
        ratingService.getUserRatings(0, 100),
      ])

      setMovies(popularMovies.results || [])
      setGenres(genresList || [])

      const ratingsMap = {}
      ratings.forEach((r) => {
        ratingsMap[r.movie_id] = r.rating
      })
      setUserRatings(ratingsMap)
    } catch (error) {
      console.error('Failed to load data:', error)
      toast.error(`Erreur: ${error.response?.data?.detail || error.message || 'Impossible de charger les films'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (query) => {
    setSearchQuery(query)
    
    if (!query) {
      loadInitialData()
      return
    }

    try {
      setLoading(true)
      const results = await movieService.searchMovies(query)
      setMovies(results.results || [])
    } catch (error) {
      console.error('Search failed:', error)
      toast.error('Erreur lors de la recherche')
    } finally {
      setLoading(false)
    }
  }

  const handleGenreToggle = (genreId) => {
    setSelectedGenres((prev) =>
      prev.includes(genreId)
        ? prev.filter((id) => id !== genreId)
        : [...prev, genreId]
    )
  }

  const applyFilters = async () => {
    if (selectedGenres.length === 0) {
      loadInitialData()
      return
    }

    try {
      setLoading(true)
      const results = await movieService.discoverMovies({
        genre_ids: selectedGenres.join(','),
        sort_by: 'popularity.desc',
      })
      setMovies(results.results || [])
      toast.success('Filtres appliqués')
    } catch (error) {
      console.error('Filter failed:', error)
      toast.error('Erreur lors du filtrage')
    } finally {
      setLoading(false)
    }
  }

  const clearFilters = () => {
    setSelectedGenres([])
    setSearchQuery('')
    loadInitialData()
  }

  const handleRate = async (movieId, rating) => {
    try {
      await ratingService.rateMovie(movieId, rating)
      setUserRatings({ ...userRatings, [movieId]: rating })
      toast.success('Note enregistrée !')
    } catch (error) {
      console.error('Failed to rate movie:', error)
      toast.error('Erreur lors de la notation')
    }
  }

  return (
    <div className="container-custom py-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-4xl font-bold text-gradient mb-4">
          Découvrir des films
        </h1>
        <p className="text-gray-400">
          Recherchez et filtrez des milliers de films
        </p>
      </motion.div>

      {/* Search and Filters */}
      <div className="space-y-4 mb-8">
        {/* Search Bar */}
        <SearchBar onSearch={handleSearch} />

        {/* Filter Toggle */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <Filter className="w-5 h-5" />
            <span>Filtres</span>
            {selectedGenres.length > 0 && (
              <span className="badge badge-primary">
                {selectedGenres.length}
              </span>
            )}
          </button>

          {(selectedGenres.length > 0 || searchQuery) && (
            <button
              onClick={clearFilters}
              className="text-sm text-gray-400 hover:text-white transition-colors"
            >
              Réinitialiser
            </button>
          )}
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="card p-6"
          >
            <h3 className="text-lg font-semibold text-white mb-4">Genres</h3>
            
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2 mb-4">
              {genres.map((genre) => (
                <button
                  key={genre.id}
                  onClick={() => handleGenreToggle(genre.id)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    selectedGenres.includes(genre.id)
                      ? 'bg-primary-600 text-white'
                      : 'bg-dark-hover text-gray-400 hover:text-white hover:bg-dark-border'
                  }`}
                >
                  {genre.name}
                </button>
              ))}
            </div>

            <button
              onClick={applyFilters}
              disabled={selectedGenres.length === 0}
              className="btn btn-primary w-full"
            >
              Appliquer les filtres
            </button>
          </motion.div>
        )}
      </div>

      {/* Results */}
      {loading ? (
        <Loading message="Recherche en cours..." />
      ) : movies.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-xl text-gray-400 mb-2">Aucun film trouvé</p>
          <p className="text-sm text-gray-500">
            Essayez de modifier vos filtres ou votre recherche
          </p>
        </div>
      ) : (
        <>
          <div className="mb-4">
            <p className="text-gray-400">
              {movies.length} film{movies.length > 1 ? 's' : ''} trouvé{movies.length > 1 ? 's' : ''}
            </p>
          </div>
          
          <MovieGrid
            movies={movies}
            onRate={handleRate}
            userRatings={userRatings}
          />
        </>
      )}
    </div>
  )
}

export default Discover