import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import SimulationPage from './pages/SimulationPage'
import ModelPage from './pages/ModelPage'
import UsersPage from './pages/UsersPage'
import OverridesPage from './pages/OverridesPage'
import LogsPage from './pages/LogsPage'

function ProtectedRoute({ children, adminOnly = false }) {
  const { user, isAdmin } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  if (adminOnly && !isAdmin) return <Navigate to="/" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index element={<DashboardPage />} />
        <Route path="simulation" element={<SimulationPage />} />
        <Route path="model" element={<ModelPage />} />
        <Route path="users" element={<ProtectedRoute adminOnly><UsersPage /></ProtectedRoute>} />
        <Route path="overrides" element={<ProtectedRoute adminOnly><OverridesPage /></ProtectedRoute>} />
        <Route path="logs" element={<ProtectedRoute adminOnly><LogsPage /></ProtectedRoute>} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
