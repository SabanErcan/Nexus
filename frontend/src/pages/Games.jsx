import { Gamepad2, Construction } from 'lucide-react'
import { motion } from 'framer-motion'

const Games = () => {
  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="max-w-2xl mx-auto text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="space-y-8"
        >
          {/* Icon */}
          <div className="flex justify-center">
            <div className="relative">
              <div className="w-32 h-32 bg-gradient-to-br from-green-500 to-emerald-600 rounded-3xl flex items-center justify-center">
                <Gamepad2 className="w-16 h-16 text-white" />
              </div>
              <div className="absolute -top-2 -right-2 w-12 h-12 bg-lime-500 rounded-full flex items-center justify-center animate-bounce">
                <Construction className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          {/* Title */}
          <div className="space-y-4">
            <h1 className="text-4xl md:text-5xl font-bold text-gradient">
              Jeux Vidéo
            </h1>
            <p className="text-xl text-gray-400">
              Level up, c'est pour bientôt !
            </p>
          </div>

          {/* Description */}
          <div className="bg-dark-card border border-dark-border rounded-xl p-8 space-y-4">
            <h2 className="text-2xl font-semibold text-white">
              Bientôt disponible 🎮
            </h2>
            <p className="text-gray-400 leading-relaxed">
              La section Jeux Vidéo est en cours de développement. Vous pourrez bientôt découvrir, 
              noter et recevoir des recommandations de jeux basées sur vos préférences gaming.
            </p>
            
            <div className="pt-4 space-y-2 text-left">
              <p className="text-sm text-gray-500 flex items-center gap-2">
                <span className="text-primary-400">✓</span> Recherche de jeux
              </p>
              <p className="text-sm text-gray-500 flex items-center gap-2">
                <span className="text-primary-400">✓</span> Notes et avis
              </p>
              <p className="text-sm text-gray-500 flex items-center gap-2">
                <span className="text-primary-400">✓</span> Recommandations personnalisées
              </p>
              <p className="text-sm text-gray-500 flex items-center gap-2">
                <span className="text-primary-400">✓</span> Plateformes et genres favoris
              </p>
            </div>
          </div>

          {/* Back Button */}
          <motion.a
            href="/"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="inline-block px-8 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-semibold rounded-lg hover:shadow-lg hover:shadow-green-500/50 transition-all"
          >
            Retour à l'accueil
          </motion.a>
        </motion.div>
      </div>
    </div>
  )
}

export default Games
