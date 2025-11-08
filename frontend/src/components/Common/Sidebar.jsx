import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { 
  Film, Music, Book,
  Compass, Star, Sparkles, User, LogOut,
  ChevronDown, ChevronRight, Menu, X
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import { motion, AnimatePresence } from 'framer-motion'

const Sidebar = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [expandedCategory, setExpandedCategory] = useState(null)
  const [isMobileOpen, setIsMobileOpen] = useState(false)

  const categories = [
    {
      id: 'movies',
      label: 'Films',
      icon: Film,
      color: 'from-blue-500 to-cyan-500',
      routes: {
        main: '/movies',
        discover: '/movies/discover',
        ratings: '/movies/ratings',
        recommendations: '/movies/recommendations'
      }
    },
    {
      id: 'music',
      label: 'Musique',
      icon: Music,
      color: 'from-purple-500 to-pink-500',
      routes: {
        main: '/music',
        discover: '/music/discover',
        ratings: '/music/ratings',
        recommendations: '/music/recommendations'
      }
    },
    {
      id: 'books',
      label: 'Livres',
      icon: Book,
      color: 'from-amber-500 to-orange-500',
      routes: {
        main: '/books',
        discover: '/books/discover',
        ratings: '/books/ratings',
        recommendations: '/books/recommendations'
      }
    }
  ]

  const subMenuItems = [
    { key: 'discover', label: 'Découvrir', icon: Compass },
    { key: 'ratings', label: 'Mes Notes', icon: Star },
    { key: 'recommendations', label: 'Recommandations', icon: Sparkles }
  ]

  const isRouteActive = (route) => location.pathname === route
  
  const isCategoryActive = (category) => {
    return Object.values(category.routes).some(route => location.pathname.startsWith(route))
  }

  const toggleCategory = (categoryId) => {
    setExpandedCategory(expandedCategory === categoryId ? null : categoryId)
  }

  const handleCategoryClick = (category) => {
    if (expandedCategory === category.id) {
      navigate(category.routes.main)
      setIsMobileOpen(false)
    } else {
      setExpandedCategory(category.id)
    }
  }

  const SidebarContent = () => (
    <>
      {/* Logo */}
      <div className="p-6 border-b border-dark-border">
        <Link to="/" className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-purple rounded-xl flex items-center justify-center">
            <Film className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-bold text-gradient">Nexus</span>
        </Link>
      </div>

      {/* Categories */}
      <div className="flex-1 overflow-y-auto py-4 px-3">
        {categories.map((category) => {
          const Icon = category.icon
          const isActive = isCategoryActive(category)
          const isExpanded = expandedCategory === category.id

          return (
            <div key={category.id} className="mb-2">
              {/* Category Button */}
              <button
                onClick={() => handleCategoryClick(category)}
                className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all ${
                  isActive 
                    ? 'bg-gradient-to-r ' + category.color + ' text-white shadow-lg' 
                    : 'text-gray-400 hover:bg-dark-hover hover:text-gray-200'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{category.label}</span>
                </div>
                {isExpanded ? (
                  <ChevronDown className="w-4 h-4" />
                ) : (
                  <ChevronRight className="w-4 h-4" />
                )}
              </button>

              {/* Submenu */}
              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="ml-4 mt-2 space-y-1 border-l-2 border-dark-border pl-4">
                      {subMenuItems.map((item) => {
                        const SubIcon = item.icon
                        const route = category.routes[item.key]
                        const isSubActive = isRouteActive(route)

                        return (
                          <Link
                            key={item.key}
                            to={route}
                            onClick={() => setIsMobileOpen(false)}
                            className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                              isSubActive
                                ? 'bg-primary-500/20 text-primary-400'
                                : 'text-gray-500 hover:text-gray-300 hover:bg-dark-hover'
                            }`}
                          >
                            <SubIcon className="w-4 h-4" />
                            <span className="text-sm">{item.label}</span>
                          </Link>
                        )
                      })}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )
        })}
      </div>

      {/* User Section */}
      <div className="border-t border-dark-border p-4 space-y-2">
        <Link
          to="/profile"
          onClick={() => setIsMobileOpen(false)}
          className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-dark-hover transition-colors"
        >
          <User className="w-5 h-5 text-gray-400" />
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-300">{user?.username}</p>
            <p className="text-xs text-gray-500">Mon profil</p>
          </div>
        </Link>

        <button
          onClick={() => {
            logout()
            setIsMobileOpen(false)
          }}
          className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-red-500/10 text-gray-400 hover:text-red-400 transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span className="text-sm font-medium">Déconnexion</span>
        </button>
      </div>
    </>
  )

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsMobileOpen(!isMobileOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-dark-card rounded-lg border border-dark-border"
      >
        {isMobileOpen ? (
          <X className="w-6 h-6 text-gray-300" />
        ) : (
          <Menu className="w-6 h-6 text-gray-300" />
        )}
      </button>

      {/* Mobile Overlay */}
      <AnimatePresence>
        {isMobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="lg:hidden fixed inset-0 bg-black/50 z-40"
            onClick={() => setIsMobileOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex lg:flex-col lg:fixed lg:inset-y-0 lg:w-72 bg-dark-card border-r border-dark-border z-30">
        <SidebarContent />
      </aside>

      {/* Mobile Sidebar */}
      <AnimatePresence>
        {isMobileOpen && (
          <motion.aside
            initial={{ x: -288 }}
            animate={{ x: 0 }}
            exit={{ x: -288 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="lg:hidden fixed inset-y-0 left-0 w-72 bg-dark-card border-r border-dark-border z-40 flex flex-col"
          >
            <SidebarContent />
          </motion.aside>
        )}
      </AnimatePresence>
    </>
  )
}

export default Sidebar
