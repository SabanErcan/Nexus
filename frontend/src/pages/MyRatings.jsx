import { useState, useEffect } from 'react'
import { toast } from 'react-hot-toast'
import MovieGrid from '../components/Movies/MovieGrid'
import Loading from '../components/Common/Loading'
import ratingService from '../services/ratingService'

const MyRatings = () => {
  const [movies, setMovies] = useState([])
  const [userRatings, setUserRatings] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadRatings()
  }, [])

  const loadRatings = async () => {
    try {
      const data = await ratingService.getUserRatings()
      const ratings = {}
      const ratedMovies = data.map(rating => {
        ratings[rating.movie.id] = rating.rating
        return rating.movie
      })
      setMovies(ratedMovies)
      setUserRatings(ratings)
    } catch (error) {
      toast.error('Erreur lors du chargement de vos notes')
      console.error('Error loading ratings:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRate = async (movieId, rating) => {
    try {
      await ratingService.updateRating(movieId, rating)
      setUserRatings(prev => ({ ...prev, [movieId]: rating }))
      toast.success('Note mise à jour !')
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
      <h1 className="text-3xl font-bold mb-8">Mes Notes</h1>
      
      {movies.length > 0 ? (
        <MovieGrid
          movies={movies}
          onRate={handleRate}
          userRatings={userRatings}
        />
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-400">
            Vous n'avez pas encore noté de films.
            <br />
            Découvrez des films et commencez à les noter !
          </p>
        </div>
      )}
    </div>
  )
}

export default MyRatings
