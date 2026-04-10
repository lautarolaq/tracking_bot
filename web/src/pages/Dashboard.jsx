import { api } from '../api'
import { useData } from '../hooks/useData'
import StatCard from '../components/StatCard'
import LineChart from '../components/LineChart'
import EventList from '../components/EventList'

export default function Dashboard({ days }) {
  const { data: overview, loading: l1 } = useData(() => api.getOverview(days), [days])
  const { data: weight, loading: l2 } = useData(() => api.getWeight(days), [days])
  const { data: events, loading: l3 } = useData(() => api.getEvents({ days, limit: 10 }), [days])

  if (l1 || l2 || l3) return <div className="text-slate-400 text-center py-12">Cargando...</div>

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-white">Dashboard</h1>

      {/* Stats cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Peso"
          value={overview?.peso?.actual ?? '—'}
          delta={overview?.peso?.delta}
          unit="kg"
          invertColor
        />
        <StatCard
          label="Kcal promedio"
          value={overview?.nutricion?.promedio_kcal ?? '—'}
          unit="kcal"
        />
        <StatCard
          label="Días gym"
          value={overview?.gym?.dias ?? '—'}
        />
        <StatCard
          label="Sueño promedio"
          value={overview?.sueno?.promedio_horas ?? '—'}
          unit="h"
        />
      </div>

      {/* Weight chart */}
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
        <h2 className="text-sm font-medium text-slate-400 mb-4">Peso — últimos {days} días</h2>
        <LineChart
          data={weight}
          lines={[{ key: 'kg', label: 'Peso (kg)', color: '#3b82f6' }]}
        />
      </div>

      {/* Recent events */}
      <div>
        <h2 className="text-sm font-medium text-slate-400 mb-3">Últimos eventos</h2>
        <EventList events={events} />
      </div>
    </div>
  )
}
