import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import Loading from '../Common/Loading'

const ProtectedRoute = () => {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return <Loading fullscreen message="Vérification de l'authentification..." />
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}

export default ProtectedRoute