const BASE_URL = import.meta.env.VITE_API_URL || ''

async function request(endpoint, options = {}) {
  const token = localStorage.getItem('token')
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${BASE_URL}${endpoint}`, { ...options, headers })

  if (res.status === 401) {
    localStorage.removeItem('token')
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Error ${res.status}`)
  }

  return res.json()
}

export const api = {
  login: (email, password) =>
    request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  me: () => request('/auth/me'),

  logout: () =>
    request('/auth/logout', { method: 'POST' }),

  getEvents: (params = {}) => {
    const qs = new URLSearchParams()
    if (params.category) qs.set('category', params.category)
    if (params.days) qs.set('days', params.days)
    if (params.limit) qs.set('limit', params.limit)
    return request(`/api/events?${qs}`)
  },

  getOverview: (days = 30) => request(`/api/stats/overview?days=${days}`),
  getWeight: (days = 30) => request(`/api/stats/weight?days=${days}`),
  getNutrition: (days = 30) => request(`/api/stats/nutrition?days=${days}`),
  getGym: (days = 30) => request(`/api/stats/gym?days=${days}`),
  getSleep: (days = 30) => request(`/api/stats/sleep?days=${days}`),
  getEmotions: (days = 30) => request(`/api/stats/emotions?days=${days}`),
  getWork: (days = 30) => request(`/api/stats/work?days=${days}`),
  getCorrelations: (days = 30) => request(`/api/correlations?days=${days}`),
}
