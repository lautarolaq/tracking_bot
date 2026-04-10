import { api } from '../api'
import { useData } from '../hooks/useData'
import StatCard from '../components/StatCard'
import LineChart from '../components/LineChart'

export default function Sleep({ days }) {
  const { data, loading } = useData(() => api.getSleep(days), [days])

  if (loading) return <div className="text-slate-400 text-center py-12">Cargando...</div>

  const avgHoras = data?.length
    ? (data.reduce((s, d) => s + d.horas, 0) / data.length).toFixed(1)
    : '—'
  const avgCalidad = data?.length
    ? (data.reduce((s, d) => s + d.calidad, 0) / data.length).toFixed(1)
    : '—'

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-white">Sueño</h1>

      <div className="grid grid-cols-2 gap-4">
        <StatCard label="Horas promedio" value={avgHoras} unit="h" />
        <StatCard label="Calidad promedio" value={avgCalidad} unit="/10" />
      </div>

      <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
        <h2 className="text-sm font-medium text-slate-400 mb-4">Horas por noche</h2>
        <LineChart
          data={data}
          lines={[
            { key: 'horas', label: 'Horas', color: '#8b5cf6' },
          ]}
        />
      </div>

      <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
        <h2 className="text-sm font-medium text-slate-400 mb-4">Calidad</h2>
        <LineChart
          data={data}
          lines={[
            { key: 'calidad', label: 'Calidad', color: '#22c55e' },
          ]}
        />
      </div>
    </div>
  )
}
