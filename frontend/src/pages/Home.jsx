import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { TrendingUp, Star, Sparkles, ArrowRight } from 'lucide-react'
import movieService from '../services/movieService'
import ratingService from '../services/ratingService'
import MovieGrid from '../components/Movies/MovieGrid'
import Loading from '../components/Common/Loading'
import toast from 'react-hot-toast'

const Home = () => {
  const [popularMovies, setPopularMovies] = useState([])
  const [topRatedMovies, setTopRatedMovies] = useState([])
  const [userRatings, setUserRatings] = useState({})
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('popular')

  useEffect(() => {
    loadMovies()
  }, [])

  const loadMovies = async () => {
    try {
      setLoading(true)

      // Charger films populaires et top rated en parallèle
      const [popular, topRated, ratings] = await Promise.all([
        movieService.getPopularMovies(),
        movieService.getTopRatedMovies(),
        ratingService.getUserRatings(0, 100),
      ])

      setPopularMovies(popular.results || [])
      setTopRatedMovies(topRated.results || [])

      // Créer un map des notes utilisateur
      const ratingsMap = {}
      ratings.forEach((r) => {
        ratingsMap[r.movie_id] = r.rating
      })
      setUserRatings(ratingsMap)
    } catch (error) {
      console.error('Failed to load movies:', error)
      toast.error('Erreur lors du chargement des films')
    } finally {
      setLoading(false)
    }
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

  if (loading) {
    return <Loading fullscreen message="Chargement des films..." />
  }

  const displayedMovies = activeTab === 'popular' ? popularMovies : topRatedMovies

  return (
    <div className="container-custom py-8">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-12 text-center"
      >
        <h1 className="text-4xl md:text-5xl font-bold text-gradient mb-4">
          Découvrez votre prochain film préféré
        </h1>
        <p className="text-gray-400 text-lg max-w-2xl mx-auto">
          Explorez des milliers de films et recevez des recommandations personnalisées
          basées sur vos goûts
        </p>
      </motion.div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
        <Link to="/discover" className="card card-hover p-6 group">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-primary-500/20 rounded-xl flex items-center justify-center group-hover:bg-primary-500/30 transition-colors">
              <TrendingUp className="w-6 h-6 text-primary-400" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-white mb-1">Découvrir</h3>
              <p className="text-sm text-gray-400">Explorez les films populaires</p>
            </div>
            <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-primary-400 transition-colors" />
          </div>
        </Link>

        <Link to="/my-ratings" className="card card-hover p-6 group">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-yellow-500/20 rounded-xl flex items-center justify-center group-hover:bg-yellow-500/30 transition-colors">
              <Star className="w-6 h-6 text-yellow-400" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-white mb-1">Mes Notes</h3>
              <p className="text-sm text-gray-400">Gérez vos évaluations</p>
            </div>
            <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-yellow-400 transition-colors" />
          </div>
        </Link>

        <Link to="/recommendations" className="card card-hover p-6 group">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-accent-purple/20 rounded-xl flex items-center justify-center group-hover:bg-accent-purple/30 transition-colors">
              <Sparkles className="w-6 h-6 text-accent-purple" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-white mb-1">Recommandations</h3>
              <p className="text-sm text-gray-400">Films suggérés pour vous</p>
            </div>
            <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-accent-purple transition-colors" />
          </div>
        </Link>
      </div>

      {/* Tabs */}
      <div className="flex items-center space-x-4 mb-6">
        <button
          onClick={() => setActiveTab('popular')}
          className={`px-6 py-3 rounded-lg font-semibold transition-all ${
            activeTab === 'popular'
              ? 'bg-primary-600 text-white'
              : 'bg-dark-card text-gray-400 hover:text-white'
          }`}
        >
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-5 h-5" />
            <span>Populaires</span>
          </div>
        </button>

        <button
          onClick={() => setActiveTab('topRated')}
          className={`px-6 py-3 rounded-lg font-semibold transition-all ${
            activeTab === 'topRated'
              ? 'bg-primary-600 text-white'
              : 'bg-dark-card text-gray-400 hover:text-white'
          }`}
        >
          <div className="flex items-center space-x-2">
            <Star className="w-5 h-5" />
            <span>Mieux notés</span>
          </div>
        </button>
      </div>

      {/* Movies Grid */}
      <MovieGrid
        movies={displayedMovies}
        onRate={handleRate}
        userRatings={userRatings}
      />
    </div>
  )
}

export default Home