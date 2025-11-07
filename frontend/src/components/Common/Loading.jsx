import { motion } from 'framer-motion'
import { Film } from 'lucide-react'

const Loading = ({ fullscreen = false, message = 'Chargement...' }) => {
  const containerClass = fullscreen
    ? 'fixed inset-0 flex items-center justify-center bg-dark-bg z-50'
    : 'flex items-center justify-center py-12'

  return (
    <div className={containerClass}>
      <div className="flex flex-col items-center space-y-4">
        <motion.div
          animate={{
            rotate: 360,
            scale: [1, 1.1, 1],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'linear',
          }}
          className="w-16 h-16 bg-gradient-to-br from-primary-500 to-accent-purple rounded-xl flex items-center justify-center"
        >
          <Film className="w-8 h-8 text-white" />
        </motion.div>
        
        <motion.p
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="text-gray-400 text-sm"
        >
          {message}
        </motion.p>
      </div>
    </div>
  )
}

export default Loading