import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Music, Filter, Search } from 'lucide-react'
import { musicService } from '../services/musicService'
import MusicGrid from '../components/Music/MusicGrid'
import SearchBar from '../components/Common/SearchBar'
import Loading from '../components/Common/Loading'
import toast from 'react-hot-toast'

/**
 * Page de découverte musicale - Style similaire aux films
 */
const MusicDiscover = () => {
  const [tracks, setTracks] = useState([])
  const [genres, setGenres] = useState([
    'pop', 'rock', 'hip-hop', 'electronic', 'jazz', 'classical',
    'r-n-b', 'country', 'metal', 'indie', 'folk', 'reggae'
  ])
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
      
      // Charger les notes de l'utilisateur
      const ratings = await musicService.getUserRatings()
      const ratingsMap = {}
      ratings.forEach((r) => {
        ratingsMap[r.track_id] = { ratingId: r.id, rating: r.rating }
      })
      setUserRatings(ratingsMap)

      // Charger les nouvelles sorties
      const releases = await musicService.getNewReleases(20)
      setTracks(releases || [])
    } catch (error) {
      console.error('Failed to load data:', error)
      toast.error(`Erreur: ${error.response?.data?.detail || error.message || 'Impossible de charger la musique'}`)
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
      const results = await musicService.searchTracks(query, 20, 0)
      setTracks(results.items || [])
    } catch (error) {
      console.error('Search failed:', error)
      toast.error('Erreur lors de la recherche')
    } finally {
      setLoading(false)
    }
  }

  const handleGenreToggle = (genre) => {
    setSelectedGenres((prev) =>
      prev.includes(genre)
        ? prev.filter((g) => g !== genre)
        : [...prev, genre]
    )
  }

  const applyFilters = async () => {
    if (selectedGenres.length === 0) {
      loadInitialData()
      return
    }

    try {
      setLoading(true)
      const results = await musicService.getRecommendations({
        seedGenres: selectedGenres,
        limit: 20
      })
      setTracks(results || [])
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

  const handleRate = async (trackId, rating) => {
    try {
      console.log('🎵 Rating track:', trackId, 'with rating:', rating)
      const existingRating = userRatings[trackId]
      console.log('Existing rating:', existingRating)
      
      if (existingRating) {
        console.log('Updating existing rating:', existingRating.ratingId)
        const result = await musicService.updateRating(existingRating.ratingId, rating)
        console.log('Update result:', result)
        setUserRatings({ ...userRatings, [trackId]: { ratingId: existingRating.ratingId, rating } })
      } else {
        console.log('Creating new rating for track:', trackId)
        const newRating = await musicService.rateTrack(trackId, rating)
        console.log('New rating created:', newRating)
        setUserRatings({ ...userRatings, [trackId]: { ratingId: newRating.id, rating } })
      }
      
      toast.success('Note enregistrée !')
    } catch (error) {
      console.error('Failed to rate track:', error)
      console.error('Error details:', error.response?.data)
      toast.error(`Erreur: ${error.response?.data?.detail || error.message}`)
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
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
            <Music className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-bold text-gradient">
              Découvrir de la musique
            </h1>
            <p className="text-gray-400">
              Explorez des milliers de pistes musicales
            </p>
          </div>
        </div>
      </motion.div>

      {/* Search and Filters */}
      <div className="space-y-4 mb-8">
        {/* Search Bar */}
        <SearchBar onSearch={handleSearch} placeholder="Rechercher des artistes ou des pistes..." />

        {/* Filter Toggle */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <Filter className="w-5 h-5" />
            <span>Genres</span>
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
            <h3 className="text-lg font-semibold text-white mb-4">Genres Musicaux</h3>
            
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2 mb-4">
              {genres.map((genre) => (
                <button
                  key={genre}
                  onClick={() => handleGenreToggle(genre)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all capitalize ${
                    selectedGenres.includes(genre)
                      ? 'bg-primary-600 text-white'
                      : 'bg-dark-hover text-gray-400 hover:text-white hover:bg-dark-border'
                  }`}
                >
                  {genre}
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
      ) : tracks.length === 0 ? (
        <div className="text-center py-12">
          <Music className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-xl text-gray-400 mb-2">Aucune piste trouvée</p>
          <p className="text-sm text-gray-500">
            Essayez de modifier vos filtres ou votre recherche
          </p>
        </div>
      ) : (
        <>
          <div className="mb-4">
            <p className="text-gray-400">
              {tracks.length} piste{tracks.length > 1 ? 's' : ''} trouvée{tracks.length > 1 ? 's' : ''}
            </p>
          </div>
          
          <MusicGrid
            tracks={tracks}
            onRatingChange={handleRate}
            userRatings={userRatings}
          />
        </>
      )}
    </div>
  )
}

export default MusicDiscover