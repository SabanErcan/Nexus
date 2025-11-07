import { createContext, useContext, useState, useEffect } from 'react'
import authService from '../services/authService'
import toast from 'react-hot-toast'

const AuthContext = createContext({})

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  // Charger l'utilisateur au démarrage
  useEffect(() => {
    const loadUser = async () => {
      try {
        if (authService.isAuthenticated()) {
          const userData = await authService.getCurrentUser()
          setUser(userData)
          setIsAuthenticated(true)
        }
      } catch (error) {
        console.error('Failed to load user:', error)
        authService.logout()
      } finally {
        setLoading(false)
      }
    }

    loadUser()
  }, [])

  // Connexion
  const login = async (email, password) => {
    try {
      await authService.login(email, password)
      const userData = await authService.getCurrentUser()
      setUser(userData)
      setIsAuthenticated(true)
      toast.success('Connexion réussie !')
      return true
    } catch (error) {
      console.error('Login failed:', error)
      toast.error(error.response?.data?.detail || 'Erreur de connexion')
      return false
    }
  }

  // Inscription
  const register = async (username, email, password) => {
    try {
      await authService.register(username, email, password)
      toast.success('Compte créé ! Connectez-vous maintenant.')
      return true
    } catch (error) {
      console.error('Registration failed:', error)
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'inscription')
      return false
    }
  }

  // Déconnexion
  const logout = () => {
    authService.logout()
    setUser(null)
    setIsAuthenticated(false)
    toast.success('Déconnexion réussie')
  }

  // Rafraîchir les données utilisateur
  const refreshUser = async () => {
    try {
      const userData = await authService.getCurrentUser()
      setUser(userData)
    } catch (error) {
      console.error('Failed to refresh user:', error)
    }
  }

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    refreshUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}