import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useSearchParams } from 'react-router-dom'
import { Music, TrendingUp } from 'lucide-react'
import { toast } from 'react-hot-toast'
import SearchBar from '../components/Common/SearchBar'
import MusicGrid from '../components/Music/MusicGrid'
import Loading from '../components/Common/Loading'
import { musicService } from '../services/musicService'

/**
 * Page de recherche musicale - Page principale musique
 */
const MusicSearch = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [tracks, setTracks] = useState([])
  const [loading, setLoading] = useState(false)
  const [userRatings, setUserRatings] = useState({})
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [initialLoad, setInitialLoad] = useState(true)

  const query = searchParams.get('q') || ''
  const limit = 20

  useEffect(() => {
    loadUserRatings()
    if (!query) {
      loadPopularTracks()
    }
  }, [])

  useEffect(() => {
    if (query) {
      searchTracks()
    }
  }, [query, page])

  const loadUserRatings = async () => {
    try {
      const ratings = await musicService.getUserRatings()
      const ratingsMap = {}
      ratings.forEach((r) => {
        ratingsMap[r.track_id] = { ratingId: r.id, rating: r.rating }
      })
      setUserRatings(ratingsMap)
    } catch (error) {
      console.error('Error loading user ratings:', error)
    }
  }

  const loadPopularTracks = async () => {
    try {
      console.log('🎵 [MusicSearch] Loading popular tracks...')
      setLoading(true)
      const results = await musicService.getNewReleases(limit)
      console.log('[MusicSearch] Popular tracks received:', results)
      setTracks(results || [])
      setTotal(results?.length || 0)
    } catch (error) {
      console.error('[MusicSearch] Error loading popular tracks:', error)
      console.error('[MusicSearch] Error details:', error.response?.data)
      toast.error('Erreur lors du chargement')
    } finally {
      setLoading(false)
      setInitialLoad(false)
    }
  }

  const searchTracks = async () => {
    if (!query) {
      setTracks([])
      setTotal(0)
      return
    }

    setLoading(true)
    try {
      const offset = (page - 1) * limit
      const results = await musicService.searchTracks(query, limit, offset)
      setTracks(results.items || [])
      setTotal(results.total || 0)
    } catch (error) {
      console.error('Error searching tracks:', error)
      toast.error('Erreur lors de la recherche')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (searchQuery) => {
    setPage(1)
    setSearchParams(searchQuery ? { q: searchQuery } : {})
    if (!searchQuery) {
      loadPopularTracks()
    }
  }

  const handleRate = async (trackId, rating) => {
    try {
      console.log('🎵 [MusicSearch] Rating track:', trackId, 'with rating:', rating)
      const existingRating = userRatings[trackId]
      console.log('[MusicSearch] Existing rating:', existingRating)
      
      if (existingRating) {
        console.log('[MusicSearch] Updating existing rating:', existingRating.ratingId)
        const result = await musicService.updateRating(existingRating.ratingId, rating)
        console.log('[MusicSearch] Update result:', result)
        setUserRatings({ ...userRatings, [trackId]: { ratingId: existingRating.ratingId, rating } })
      } else {
        console.log('[MusicSearch] Creating new rating for track:', trackId)
        const newRating = await musicService.rateTrack(trackId, rating)
        console.log('[MusicSearch] New rating created:', newRating)
        setUserRatings({ ...userRatings, [trackId]: { ratingId: newRating.id, rating } })
      }
      
      toast.success('Note enregistrée !')
    } catch (error) {
      console.error('[MusicSearch] Failed to rate track:', error)
      console.error('[MusicSearch] Error details:', error.response?.data)
      toast.error(`Erreur: ${error.response?.data?.detail || error.message}`)
    }
  }

  const totalPages = Math.ceil(total / limit)

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
              {query ? 'Résultats de recherche' : 'Musique'}
            </h1>
            <p className="text-gray-400">
              {query 
                ? `Recherche : "${query}"`
                : 'Explorez et découvrez de nouvelles pistes'}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Search Bar */}
      <div className="mb-8">
        <SearchBar
          initialValue={query}
          onSearch={handleSearch}
          placeholder="Rechercher des artistes, titres ou albums..."
        />
      </div>

      {/* Results */}
      {loading && initialLoad ? (
        <Loading message="Chargement..." />
      ) : tracks.length === 0 && !loading ? (
        <div className="text-center py-12">
          <Music className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-xl text-gray-400 mb-2">
            {query ? 'Aucune piste trouvée' : 'Commencez votre recherche'}
          </p>
          <p className="text-sm text-gray-500">
            {query 
              ? 'Essayez avec d\'autres mots-clés'
              : 'Recherchez vos artistes ou titres préférés'}
          </p>
        </div>
      ) : (
        <>
          {!query && (
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5 text-primary-400" />
              <p className="text-gray-400">Nouveautés populaires</p>
            </div>
          )}

          {loading && !initialLoad ? (
            <Loading message="Recherche en cours..." />
          ) : (
            <>
              <div className="mb-4">
                <p className="text-gray-400">
                  {total > 0 && `${total} piste${total > 1 ? 's' : ''} trouvée${total > 1 ? 's' : ''}`}
                </p>
              </div>

              <MusicGrid
                tracks={tracks}
                onRatingChange={handleRate}
                userRatings={userRatings}
              />

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex justify-center items-center mt-8 gap-4">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="btn btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Précédent
                  </button>
                  <span className="text-gray-400">
                    Page <span className="text-white font-semibold">{page}</span> sur {totalPages}
                  </span>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="btn btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Suivant
                  </button>
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  )
}

export default MusicSearch