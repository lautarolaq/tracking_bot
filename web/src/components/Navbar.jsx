import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

const NAV_ITEMS = [
  { path: '/', label: 'Dashboard' },
  { path: '/nutrition', label: 'Nutrición' },
  { path: '/gym', label: 'Gym' },
  { path: '/sleep', label: 'Sueño' },
  { path: '/weight', label: 'Peso' },
  { path: '/emotions', label: 'Emociones' },
  { path: '/work', label: 'Laburo' },
]

const PERIOD_OPTIONS = [
  { value: 7, label: '7d' },
  { value: 30, label: '30d' },
  { value: 90, label: '90d' },
]

export default function Navbar({ days, onDaysChange }) {
  const { logout } = useAuth()
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <nav className="bg-slate-800 border-b border-slate-700">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-14">
          {/* Logo */}
          <Link to="/" className="text-blue-500 font-bold text-lg">
            Tracker
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-1">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`px-3 py-2 rounded text-sm transition-colors ${
                  location.pathname === item.path
                    ? 'bg-slate-700 text-white'
                    : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </div>

          {/* Period selector + logout */}
          <div className="flex items-center gap-2">
            <div className="flex bg-slate-700 rounded overflow-hidden">
              {PERIOD_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => onDaysChange(opt.value)}
                  className={`px-2 py-1 text-xs transition-colors ${
                    days === opt.value
                      ? 'bg-blue-500 text-white'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
            <button
              onClick={logout}
              className="text-slate-400 hover:text-white text-sm px-2 py-1"
            >
              Salir
            </button>
            {/* Mobile hamburger */}
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="md:hidden text-slate-400 hover:text-white p-1"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {menuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden pb-3 border-t border-slate-700 pt-2">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setMenuOpen(false)}
                className={`block px-3 py-2 rounded text-sm ${
                  location.pathname === item.path
                    ? 'bg-slate-700 text-white'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </div>
        )}
      </div>
    </nav>
  )
}
