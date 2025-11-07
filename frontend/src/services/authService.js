import api from './api'

const authService = {
  // Inscription
  register: async (username, email, password) => {
    const response = await api.post('/auth/register', {
      username,
      email,
      password,
    })
    return response.data
  },

  // Connexion
  login: async (email, password) => {
    const response = await api.post('/auth/login', {
      email,
      password,
    })
    
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token)
    }
    
    return response.data
  },

  // Déconnexion
  logout: () => {
    localStorage.removeItem('token')
  },

  // Récupérer l'utilisateur connecté
  getCurrentUser: async () => {
    const response = await api.get('/auth/me')
    return response.data
  },

  // Vérifier si l'utilisateur est connecté
  isAuthenticated: () => {
    return !!localStorage.getItem('token')
  },

  // Récupérer le token
  getToken: () => {
    return localStorage.getItem('token')
  },
}

export default authService