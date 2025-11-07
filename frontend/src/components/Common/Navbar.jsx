import { Link, useLocation } from 'react-router-dom'
import { Film, Compass, Star, Sparkles, User, LogOut } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { motion } from 'framer-motion'

const Navbar = () => {
  const location = useLocation()
  const { user, logout } = useAuth()

  const navItems = [
    { path: '/', label: 'Accueil', icon: Film },
    { path: '/discover', label: 'Découvrir', icon: Compass },
    { path: '/my-ratings', label: 'Mes Notes', icon: Star },
    { path: '/recommendations', label: 'Recommandations', icon: Sparkles },
  ]

  const isActive = (path) => location.pathname === path

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-dark-card/80 backdrop-blur-xl border-b border-dark-border">
      <div className="container-custom">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-purple rounded-lg flex items-center justify-center">
              <Film className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-gradient">Nexus</span>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const active = isActive(item.path)
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className="relative px-4 py-2 rounded-lg transition-colors"
                >
                  <div className={`flex items-center space-x-2 ${
                    active ? 'text-primary-400' : 'text-gray-400 hover:text-gray-200'
                  }`}>
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </div>
                  
                  {active && (
                    <motion.div
                      layoutId="navbar-indicator"
                      className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500"
                      initial={false}
                      transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                    />
                  )}
                </Link>
              )
            })}
          </div>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            <Link
              to="/profile"
              className="flex items-center space-x-2 px-4 py-2 rounded-lg hover:bg-dark-hover transition-colors"
            >
              <User className="w-5 h-5 text-gray-400" />
              <span className="hidden md:block text-sm text-gray-300">
                {user?.username}
              </span>
            </Link>

            <button
              onClick={logout}
              className="p-2 rounded-lg hover:bg-dark-hover text-gray-400 hover:text-red-400 transition-colors"
              title="Déconnexion"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation (optionnel) */}
      <div className="md:hidden border-t border-dark-border">
        <div className="flex justify-around py-2">
          {navItems.map((item) => {
            const Icon = item.icon
            const active = isActive(item.path)
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex flex-col items-center space-y-1 px-3 py-2 ${
                  active ? 'text-primary-400' : 'text-gray-500'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="text-xs">{item.label}</span>
              </Link>
            )
          })}
        </div>
      </div>
    </nav>
  )
}

export default Navbar