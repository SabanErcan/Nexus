import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/Auth/ProtectedRoute'

// Pages
import Login from './pages/Login'
import Register from './pages/Register'
import QuickLaunch from './pages/QuickLaunch'
import Home from './pages/Home'
import Discover from './pages/Discover'
import MyRatings from './pages/MyRatings'
import Recommendations from './pages/Recommendations'
import Profile from './pages/Profile'
import MusicSearch from './pages/MusicSearch'
import MusicDiscover from './pages/MusicDiscover'
import MusicRatings from './pages/MusicRatings'
import MusicRecommendations from './pages/MusicRecommendations'
import BookSearch from './pages/BookSearch'
import BookRatings from './pages/BookRatings'
import BookRecommendations from './pages/BookRecommendations'
import Books from './pages/Books'

// Layout
import Sidebar from './components/Common/Sidebar'

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="min-h-screen bg-dark-bg">
          <Toaster 
            position="top-right"
            toastOptions={{
              style: {
                background: '#13131a',
                color: '#fff',
                border: '1px solid #2a2a35',
              },
              success: {
                iconTheme: {
                  primary: '#0ea5e9',
                  secondary: '#fff',
                },
              },
            }}
          />
          
          <Routes>
            {/* Routes publiques */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
            {/* Routes protégées */}
            <Route element={<ProtectedRoute />}>
              {/* QuickLaunch - Page d'accueil principale */}
              <Route path="/" element={<QuickLaunch />} />
              
              <Route
                element={
                  <>
                    <Sidebar />
                    <div className="lg:pl-72">
                      <Outlet />
                    </div>
                  </>
                }
              >
                <Route path="/home" element={<Home />} />
                <Route path="/movies" element={<Discover />} />
                <Route path="/movies/discover" element={<Discover />} />
                <Route path="/movies/ratings" element={<MyRatings />} />
                <Route path="/movies/recommendations" element={<Recommendations />} />
                
                <Route path="/music" element={<MusicSearch />} />
                <Route path="/music/discover" element={<MusicDiscover />} />
                <Route path="/music/ratings" element={<MusicRatings />} />
                <Route path="/music/recommendations" element={<MusicRecommendations />} />
                
                <Route path="/books" element={<BookSearch />} />
                <Route path="/books/discover" element={<BookSearch />} />
                <Route path="/books/ratings" element={<BookRatings />} />
                <Route path="/books/recommendations" element={<BookRecommendations />} />
                
                <Route path="/profile" element={<Profile />} />
              </Route>
            </Route>
            
            {/* Redirect par défaut */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </AuthProvider>
    </Router>
  )
}

export default App