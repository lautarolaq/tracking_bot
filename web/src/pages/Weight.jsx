import { useMemo } from 'react'
import { api } from '../api'
import { useData } from '../hooks/useData'
import StatCard from '../components/StatCard'
import LineChart from '../components/LineChart'

export default function Weight({ days }) {
  const { data, loading } = useData(() => api.getWeight(days), [days])

  const chartData = useMemo(() => {
    if (!data || data.length === 0) return []
    return data.map((d, i) => {
      const start = Math.max(0, i - 6)
      const slice = data.slice(start, i + 1)
      const ma = slice.reduce((s, x) => s + x.kg, 0) / slice.length
      return { ...d, media_7d: parseFloat(ma.toFixed(1)) }
    })
  }, [data])

  if (loading) return <div className="text-slate-400 text-center py-12">Cargando...</div>

  const current = data?.length ? data[data.length - 1].kg : '—'
  const first = data?.length ? data[0].kg : null
  const deltaPeriod = current !== '—' && first ? (current - first).toFixed(1) : null

  // Weekly delta (last 7 entries or less)
  const recent7 = data?.slice(-7)
  const deltaWeek = recent7?.length >= 2
    ? (recent7[recent7.length - 1].kg - recent7[0].kg).toFixed(1)
    : null

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-white">Peso</h1>

      <div className="grid grid-cols-3 gap-4">
        <StatCard label="Actual" value={current} unit="kg" />
        <StatCard label={`Delta ${days}d`} value={deltaPeriod ?? '—'} unit="kg" invertColor />
        <StatCard label="Delta 7d" value={deltaWeek ?? '—'} unit="kg" invertColor />
      </div>

      <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
        <h2 className="text-sm font-medium text-slate-400 mb-4">Progresión</h2>
        <LineChart
          data={chartData}
          lines={[
            { key: 'kg', label: 'Peso', color: '#3b82f6' },
            { key: 'media_7d', label: 'Media 7d', color: '#f59e0b' },
          ]}
        />
      </div>
    </div>
  )
}
