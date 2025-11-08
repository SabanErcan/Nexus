import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Star, Music } from 'lucide-react'
import { toast } from 'react-hot-toast'
import MusicGrid from '../components/Music/MusicGrid'
import Loading from '../components/Common/Loading'
import { musicService } from '../services/musicService'

const MusicRatings = () => {
  const [tracks, setTracks] = useState([])
  const [userRatings, setUserRatings] = useState({})
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    total: 0,
    average: 0,
    topRated: 0
  })

  useEffect(() => {
    loadRatings()
  }, [])

  const loadRatings = async () => {
    try {
      console.log('🎵 Loading music ratings...')
      const data = await musicService.getUserRatings()
      console.log('Ratings received from API:', data)
      
      const ratings = {}
      const ratedTracks = data.map(rating => {
        console.log('Processing rating:', rating)
        ratings[rating.track.id] = { ratingId: rating.id, rating: rating.rating }
        return rating.track
      })
      
      console.log('Processed ratings map:', ratings)
      console.log('Rated tracks:', ratedTracks)
      
      setTracks(ratedTracks)
      setUserRatings(ratings)

      // Calculer les statistiques
      const ratingsValues = data.map(r => r.rating)
      const average = ratingsValues.length > 0 
        ? (ratingsValues.reduce((a, b) => a + b, 0) / ratingsValues.length).toFixed(1)
        : 0
      const topRated = ratingsValues.filter(r => r >= 4).length

      setStats({
        total: ratingsValues.length,
        average,
        topRated
      })
    } catch (error) {
      toast.error('Erreur lors du chargement de vos notes')
      console.error('Error loading ratings:', error)
      console.error('Error details:', error.response?.data)
    } finally {
      setLoading(false)
    }
  }

  const handleRate = async (trackId, rating) => {
    try {
      const existingRating = userRatings[trackId]
      
      if (existingRating) {
        await musicService.updateRating(existingRating.ratingId, rating)
        const updatedRatings = { ...userRatings, [trackId]: { ratingId: existingRating.ratingId, rating } }
        setUserRatings(updatedRatings)
        
        // Recalculer les stats
        const ratingsValues = Object.values(updatedRatings).map(r => r.rating)
        const average = (ratingsValues.reduce((a, b) => a + b, 0) / ratingsValues.length).toFixed(1)
        const topRated = ratingsValues.filter(r => r >= 4).length
        
        setStats({
          total: ratingsValues.length,
          average,
          topRated
        })
        
        toast.success('Note mise à jour !')
      }
    } catch (error) {
      toast.error('Erreur lors de la mise à jour de la note')
      console.error('Error updating rating:', error)
    }
  }

  if (loading) {
    return <Loading />
  }

  return (
    <div className="container-custom py-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
            <Star className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-bold text-gradient">Mes Notes Musicales</h1>
            <p className="text-gray-400">Toutes vos pistes notées</p>
          </div>
        </div>

        {/* Stats Cards */}
        {tracks.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="card p-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400 mb-1">Total</p>
                  <p className="text-3xl font-bold text-white">{stats.total}</p>
                </div>
                <Music className="w-10 h-10 text-primary-400 opacity-50" />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="card p-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400 mb-1">Note moyenne</p>
                  <p className="text-3xl font-bold text-white">{stats.average}/5</p>
                </div>
                <Star className="w-10 h-10 text-yellow-400 opacity-50" />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="card p-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400 mb-1">Coups de cœur</p>
                  <p className="text-3xl font-bold text-white">{stats.topRated}</p>
                </div>
                <div className="flex">
                  <Star className="w-6 h-6 text-yellow-400 fill-current" />
                  <Star className="w-6 h-6 text-yellow-400 fill-current -ml-1" />
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </motion.div>
      
      {tracks.length > 0 ? (
        <MusicGrid
          tracks={tracks}
          onRatingChange={handleRate}
          userRatings={userRatings}
        />
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <Music className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-xl text-gray-400 mb-2">
            Vous n'avez pas encore noté de musique
          </p>
          <p className="text-sm text-gray-500">
            Découvrez de la musique et commencez à noter vos pistes préférées !
          </p>
        </motion.div>
      )}
    </div>
  )
}

export default MusicRatings
