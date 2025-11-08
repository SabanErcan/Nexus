import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Sparkles, RefreshCw, AlertCircle, Zap } from 'lucide-react'
import recommendationService from '../services/recommendationService'
import ratingService from '../services/ratingService'
import MovieGrid from '../components/Movies/MovieGrid'
import MovieCard from '../components/Movies/MovieCard'
import Loading from '../components/Common/Loading'
import toast from 'react-hot-toast'

const Recommendations = () => {
  const [recommendations, setRecommendations] = useState([])
  const [userRatings, setUserRatings] = useState({})
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    loadRecommendations()
  }, [])

  const loadRecommendations = async () => {
    try {
      setLoading(true)
      
      const [recs, ratings] = await Promise.all([
        recommendationService.getRecommendations(20),
        ratingService.getUserRatings(0, 100),
      ])

      setRecommendations(recs)

      const ratingsMap = {}
      ratings.forEach((r) => {
        ratingsMap[r.movie_id] = r.rating
      })
      setUserRatings(ratingsMap)
    } catch (error) {
      console.error('Failed to load recommendations:', error)
      
      if (error.response?.status === 404) {
        // Pas de recommandations, ne rien faire
        setRecommendations([])
      } else {
        toast.error('Erreur lors du chargement des recommandations')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    try {
      setGenerating(true)
      
      const result = await recommendationService.generateRecommendations()
      
      toast.success(`${result.count} recommandations générées !`)
      
      // Recharger les recommandations
      await loadRecommendations()
    } catch (error) {
      console.error('Failed to generate recommendations:', error)
      toast.error(
        error.response?.data?.detail || 
        'Erreur lors de la génération. Notez plus de films (minimum 3) pour obtenir des recommandations personnalisées.'
      )
    } finally {
      setGenerating(false)
    }
  }

  const handleRate = async (movieId, rating) => {
    try {
      await ratingService.rateMovie(movieId, rating)
      setUserRatings({ ...userRatings, [movieId]: rating })
      toast.success('Note enregistrée !')
      
      // Optionnel: regénérer les recommandations après une note
      // await handleGenerate()
    } catch (error) {
      console.error('Failed to rate movie:', error)
      toast.error('Erreur lors de la notation')
    }
  }

  if (loading) {
    return <Loading fullscreen message="Chargement des recommandations..." />
  }

  return (
    <div className="container-custom py-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-4xl font-bold text-gradient flex items-center space-x-3">
            <Sparkles className="w-10 h-10 text-accent-purple" />
            <span>Recommandations</span>
          </h1>

          <button
            onClick={handleGenerate}
            disabled={generating}
            className="btn btn-primary flex items-center space-x-2"
          >
            {generating ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                >
                  <RefreshCw className="w-5 h-5" />
                </motion.div>
                <span>Génération...</span>
              </>
            ) : (
              <>
                <RefreshCw className="w-5 h-5" />
                <span>Générer</span>
              </>
            )}
          </button>
        </div>

        <p className="text-gray-400">
          Films recommandés par notre algorithme hybride basé sur vos goûts
        </p>
      </motion.div>

      {/* Info Banner */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card p-6 mb-8 bg-gradient-to-r from-primary-500/10 to-accent-purple/10 border-primary-500/20"
      >
        <div className="flex items-start space-x-4">
          <div className="w-12 h-12 bg-primary-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
            <Zap className="w-6 h-6 text-primary-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white mb-2">
              Algorithme Hybride
            </h3>
            <p className="text-gray-300 text-sm leading-relaxed">
              Nos recommandations combinent le <span className="text-primary-400 font-semibold">filtrage collaboratif</span> (utilisateurs similaires) 
              et le <span className="text-accent-purple font-semibold">filtrage basé sur le contenu</span> (films similaires) 
              pour vous proposer les meilleurs films adaptés à vos goûts.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Recommendations */}
      {recommendations.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-12 text-center"
        >
          <AlertCircle className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">
            Aucune recommandation disponible
          </h3>
          <p className="text-gray-400 mb-6 max-w-md mx-auto">
            Pour obtenir des recommandations personnalisées, notez au moins 3 films 
            puis cliquez sur "Générer"
          </p>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="btn btn-primary inline-flex items-center space-x-2"
          >
            <Sparkles className="w-5 h-5" />
            <span>Générer des recommandations</span>
          </button>
        </motion.div>
      ) : (
        <>
          {/* Algorithm Type Badge */}
          {recommendations[0] && (
            <div className="mb-6 flex items-center space-x-2">
              <span className="badge badge-primary">
                {recommendations[0].algorithm_type === 'hybrid' && '🎯 Hybride'}
                {recommendations[0].algorithm_type === 'collaborative' && '👥 Collaboratif'}
                {recommendations[0].algorithm_type === 'content_based' && '🎬 Basé contenu'}
                {recommendations[0].algorithm_type === 'popular' && '🔥 Populaire'}
              </span>
              <span className="text-sm text-gray-400">
                {recommendations.length} recommandation{recommendations.length > 1 ? 's' : ''}
              </span>
            </div>
          )}

          {/* Movies Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 md:gap-6">
            {recommendations.map((rec, index) => (
              <motion.div
                key={rec.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <div className="relative">
                  {/* Score Badge */}
                  <div className="absolute top-2 left-2 z-10 bg-gradient-to-r from-primary-500 to-accent-purple px-3 py-1 rounded-lg">
                    <span className="text-white font-bold text-sm">
                      {(rec.score * 100).toFixed(0)}%
                    </span>
                  </div>

                  <MovieCard
                    movie={rec.movie}
                    onRate={handleRate}
                    userRating={userRatings[rec.movie_id]}
                    key={rec.movie_id}
                  />

                  {/* Explanation */}
                  {rec.explanation && (
                    <div className="mt-2 text-xs text-gray-400 line-clamp-2">
                      {rec.explanation}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

export default Recommendations