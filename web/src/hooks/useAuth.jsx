import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { api } from '../api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      setLoading(false)
      return
    }
    api.me()
      .then((data) => setUser(data))
      .catch(() => {
        localStorage.removeItem('token')
      })
      .finally(() => setLoading(false))
  }, [])

  const login = useCallback(async (email, password) => {
    const { token } = await api.login(email, password)
    localStorage.setItem('token', token)
    const data = await api.me()
    setUser(data)
  }, [])

  const logout = useCallback(async () => {
    try {
      await api.logout()
    } catch {}
    localStorage.removeItem('token')
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be inside AuthProvider')
  return ctx
}
