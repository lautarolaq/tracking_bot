import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import Navbar from './Navbar'

export default function Layout({ children, days, onDaysChange }) {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-slate-400 text-lg">Cargando...</div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <Navbar days={days} onDaysChange={onDaysChange} />
      <main className="max-w-7xl mx-auto px-4 py-6">
        {children}
      </main>
    </div>
  )
}
