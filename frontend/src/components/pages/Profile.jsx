import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { User, Mail, Calendar, Star, Film, Sparkles, LogOut } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import ratingService from '../services/ratingService'
import Loading from '../components/Common/Loading'

const Profile = () => {
  const { user, logout } = useAuth()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const statsData = await ratingService.getUserRatingStats()
      setStats(statsData)
    } catch (error) {
      console.error('Failed to load stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <Loading fullscreen message="Chargement du profil..." />
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
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
          Mon Profil
        </h1>
        <p className="text-gray-400">
          Gérez vos informations et consultez vos statistiques
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* User Info Card */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="lg:col-span-1"
        >
          <div className="card p-8">
            {/* Avatar */}
            <div className="flex justify-center mb-6">
              <div className="w-24 h-24 bg-gradient-to-br from-primary-500 to-accent-purple rounded-full flex items-center justify-center text-3xl font-bold text-white">
                {user?.username?.charAt(0).toUpperCase()}
              </div>
            </div>

            {/* User Details */}
            <div className="space-y-4">
              <div>
                <div className="flex items-center space-x-2 text-gray-400 text-sm mb-1">
                  <User className="w-4 h-4" />
                  <span>Nom d'utilisateur</span>
                </div>
                <p className="text-white font-semibold">{user?.username}</p>
              </div>

              <div>
                <div className="flex items-center space-x-2 text-gray-400 text-sm mb-1">
                  <Mail className="w-4 h-4" />
                  <span>Email</span>
                </div>
                <p className="text-white font-semibold">{user?.email}</p>
              </div>

              <div>
                <div className="flex items-center space-x-2 text-gray-400 text-sm mb-1">
                  <Calendar className="w-4 h-4" />
                  <span>Membre depuis</span>
                </div>
                <p className="text-white font-semibold">
                  {user?.created_at && formatDate(user.created_at)}
                </p>
              </div>
            </div>

            {/* Logout Button */}
            <button
              onClick={logout}
              className="btn btn-secondary w-full mt-6 flex items-center justify-center space-x-2 hover:bg-red-500/20 hover:text-red-400 hover:border-red-500/50 transition-all"
            >
              <LogOut className="w-5 h-5" />
              <span>Déconnexion</span>
            </button>
          </div>
        </motion.div>

        {/* Stats Cards */}
        <div className="lg:col-span-2 space-y-8">
          {/* Quick Stats */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h2 className="text-2xl font-bold text-white mb-4">
              Statistiques
            </h2>
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="card p-6">
                <div className="flex items-center justify-between mb-2">
                  <Film className="w-8 h-8 text-primary-400" />
                  <span className="text-3xl font-bold text-white">
                    {stats?.total_ratings || 0}
                  </span>
                </div>
                <p className="text-gray-400 text-sm">Films notés</p>
              </div>

              <div className="card p-6">
                <div className="flex items-center justify-between mb-2">
                  <Star className="w-8 h-8 text-yellow-400" />
                  <span className="text-3xl font-bold text-white">
                    {stats?.average_rating?.toFixed(1) || '0.0'}
                  </span>
                </div>
                <p className="text-gray-400 text-sm">Note moyenne</p>
              </div>

              <div className="card p-6">
                <div className="flex items-center justify-between mb-2">
                  <Sparkles className="w-8 h-8 text-accent-purple" />
                  <span className="text-3xl font-bold text-white">
                    {stats?.highly_rated_count || 0}
                  </span>
                </div>
                <p className="text-gray-400 text-sm">Films adorés</p>
              </div>
            </div>
          </motion.div>

          {/* Favorite Genres */}
          {stats?.favorite_genres && Object.keys(stats.favorite_genres).length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <h2 className="text-2xl font-bold text-white mb-4">
                Genres préférés
              </h2>
              
              <div className="card p-6">
                <div className="flex flex-wrap gap-2">
                  {Object.entries(stats.favorite_genres)
                    .slice(0, 10)
                    .map(([genre, count], index) => (
                      <motion.div
                        key={genre}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.1 * index }}
                        className="badge badge-primary px-4 py-2 text-sm"
                      >
                        {genre} ({count})
                      </motion.div>
                    ))}
                </div>
              </div>
            </motion.div>
          )}

          {/* Rating Distribution */}
          {stats?.rating_distribution && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <h2 className="text-2xl font-bold text-white mb-4">
                Distribution des notes
              </h2>
              
              <div className="card p-6">
                <div className="space-y-4">
                  {[5, 4, 3, 2, 1].map((star) => {
                    const count = stats.rating_distribution[star] || 0
                    const percentage = stats.total_ratings > 0
                      ? (count / stats.total_ratings) * 100
                      : 0

                    return (
                      <div key={star} className="flex items-center space-x-4">
                        <div className="flex items-center space-x-1 w-16">
                          <span className="text-white font-medium">{star}</span>
                          <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                        </div>
                        
                        <div className="flex-1 h-6 bg-dark-hover rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${percentage}%` }}
                            transition={{ duration: 0.5, delay: 0.1 * (6 - star) }}
                            className="h-full bg-gradient-to-r from-primary-500 to-accent-cyan"
                          />
                        </div>
                        
                        <span className="text-gray-400 text-sm w-20 text-right">
                          {count} ({percentage.toFixed(0)}%)
                        </span>
                      </div>
                    )
                  })}
                </div>
              </div>
            </motion.div>
          )}

          {/* Last Activity */}
          {stats?.last_rating_date && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="card p-6"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm mb-1">Dernière activité</p>
                  <p className="text-white font-semibold">
                    {formatDate(stats.last_rating_date)}
                  </p>
                </div>
                <Calendar className="w-8 h-8 text-gray-600" />
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Profile