import { useState } from 'react'
import { Star } from 'lucide-react'
import { motion } from 'framer-motion'

const RatingStars = ({ movieId, initialRating = 0, onRate }) => {
  const [rating, setRating] = useState(initialRating)
  const [hoverRating, setHoverRating] = useState(0)

  const handleClick = (value) => {
    setRating(value)
    if (onRate) {
      onRate(value)
    }
  }

  return (
    <div className="flex items-center justify-center space-x-2">
      {[1, 2, 3, 4, 5].map((value) => {
        const isFilled = value <= (hoverRating || rating)
        
        return (
          <motion.button
            key={value}
            whileHover={{ scale: 1.2 }}
            whileTap={{ scale: 0.9 }}
            onMouseEnter={() => setHoverRating(value)}
            onMouseLeave={() => setHoverRating(0)}
            onClick={() => handleClick(value)}
            className="focus:outline-none"
          >
            <Star
              className={`w-8 h-8 transition-all duration-200 ${
                isFilled
                  ? 'text-yellow-400 fill-yellow-400'
                  : 'text-gray-600 hover:text-yellow-400'
              }`}
            />
          </motion.button>
        )
      })}
    </div>
  )
}

export default RatingStars