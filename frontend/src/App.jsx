import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/Auth/ProtectedRoute'

// Pages
import Login from './pages/Login'
import Register from './pages/Register'
import Home from './pages/Home'
import Discover from './pages/Discover'
import MyRatings from './pages/MyRatings'
import Recommendations from './pages/Recommendations'
import Profile from './pages/Profile'

// Layout
import Navbar from './components/Common/Navbar'

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
              <Route element={<><Navbar /><div className="pt-16"><Routes><Route path="/" element={<Home />} /><Route path="/discover" element={<Discover />} /><Route path="/my-ratings" element={<MyRatings />} /><Route path="/recommendations" element={<Recommendations />} /><Route path="/profile" element={<Profile />} /></Routes></div></>}>
                <Route path="/" element={<Home />} />
                <Route path="/discover" element={<Discover />} />
                <Route path="/my-ratings" element={<MyRatings />} />
                <Route path="/recommendations" element={<Recommendations />} />
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