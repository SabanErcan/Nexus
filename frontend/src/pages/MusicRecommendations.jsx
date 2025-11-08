import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Sparkles, Music } from 'lucide-react'
import { toast } from 'react-hot-toast'
import MusicGrid from '../components/Music/MusicGrid'
import Loading from '../components/Common/Loading'
import { musicService } from '../services/musicService'

const MusicRecommendations = () => {
  const [recommendations, setRecommendations] = useState([])
  const [userRatings, setUserRatings] = useState({})
  const [loading, setLoading] = useState(true)
  const [hasRatings, setHasRatings] = useState(false)

  useEffect(() => {
    loadRecommendations()
  }, [])

  const loadRecommendations = async () => {
    try {
      setLoading(true)
      console.log('🎵 [MusicRecommendations] Loading recommendations...')
      
      // Charger les notes de l'utilisateur
      const ratings = await musicService.getUserRatings()
      console.log('[MusicRecommendations] User ratings:', ratings)
      
      if (ratings.length === 0) {
        console.log('[MusicRecommendations] No ratings found')
        setHasRatings(false)
        setLoading(false)
        return
      }

      setHasRatings(true)
      
      const ratingsMap = {}
      ratings.forEach((r) => {
        ratingsMap[r.track.id] = { ratingId: r.id, rating: r.rating }
      })
      setUserRatings(ratingsMap)

      // Utiliser les pistes les mieux notées comme seeds
      const topRated = ratings
        .sort((a, b) => b.rating - a.rating)
        .slice(0, 5)
        .map(r => r.track.spotify_id)

      console.log('[MusicRecommendations] Top rated tracks (seeds):', topRated)

      // Charger les recommandations basées sur ces pistes
      const recs = await musicService.getRecommendations({
        seedTracks: topRated,
        limit: 20
      })
      
      console.log('[MusicRecommendations] Recommendations received:', recs)
      setRecommendations(recs || [])
    } catch (error) {
      console.error('[MusicRecommendations] Failed to load recommendations:', error)
      console.error('[MusicRecommendations] Error details:', error.response?.data)
      toast.error(`Erreur: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleRate = async (trackId, rating) => {
    try {
      const existingRating = userRatings[trackId]
      
      if (existingRating) {
        await musicService.updateRating(existingRating.ratingId, rating)
        setUserRatings({ ...userRatings, [trackId]: { ratingId: existingRating.ratingId, rating } })
      } else {
        const newRating = await musicService.rateTrack(trackId, rating)
        setUserRatings({ ...userRatings, [trackId]: { ratingId: newRating.id, rating } })
      }
      
      toast.success('Note enregistrée !')
    } catch (error) {
      console.error('Failed to rate track:', error)
      toast.error('Erreur lors de la notation')
    }
  }

  if (loading) {
    return <Loading message="Génération de recommandations..." />
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
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-bold text-gradient">Recommandations Musicales</h1>
            <p className="text-gray-400">
              {hasRatings 
                ? 'Basées sur vos goûts musicaux'
                : 'Notez quelques pistes pour recevoir des recommandations'}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Content */}
      {!hasRatings ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-dark-card border border-dark-border rounded-xl p-8 text-center"
        >
          <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <Music className="w-10 h-10 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Commencez à noter de la musique</h2>
          <p className="text-gray-400 max-w-md mx-auto mb-6">
            Le système de recommandations sera activé dès que vous aurez noté quelques pistes. 
            Plus vous notez, meilleures seront les recommandations !
          </p>
          <a
            href="/music"
            className="btn btn-primary inline-block"
          >
            Découvrir de la musique
          </a>
        </motion.div>
      ) : recommendations.length === 0 ? (
        <div className="text-center py-12">
          <Music className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-xl text-gray-400 mb-2">Aucune recommandation disponible</p>
          <p className="text-sm text-gray-500">
            Notez plus de pistes pour obtenir de meilleures recommandations
          </p>
        </div>
      ) : (
        <>
          <div className="mb-6">
            <p className="text-gray-400">
              {recommendations.length} piste{recommendations.length > 1 ? 's' : ''} recommandée{recommendations.length > 1 ? 's' : ''}
            </p>
          </div>
          
          <MusicGrid
            tracks={recommendations}
            onRatingChange={handleRate}
            userRatings={userRatings}
          />
        </>
      )}
    </div>
  )
}

export default MusicRecommendations
