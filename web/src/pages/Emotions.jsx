import { format, parseISO } from 'date-fns'
import { api } from '../api'
import { useData } from '../hooks/useData'
import StatCard from '../components/StatCard'

export default function Emotions({ days }) {
  const { data, loading } = useData(() => api.getEmotions(days), [days])

  if (loading) return <div className="text-slate-400 text-center py-12">Cargando...</div>

  const total = data?.length || 0
  const avgIntensidad = total
    ? (data.reduce((s, d) => s + d.intensidad, 0) / total).toFixed(1)
    : '—'

  // Find recurring situations
  const situationCounts = {}
  data?.forEach((d) => {
    const sit = d.situacion?.toLowerCase().trim()
    if (sit) situationCounts[sit] = (situationCounts[sit] || 0) + 1
  })
  const recurring = Object.entries(situationCounts)
    .filter(([, count]) => count > 1)
    .sort((a, b) => b[1] - a[1])

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-white">Emociones</h1>

      <div className="grid grid-cols-2 gap-4">
        <StatCard label="Total activaciones" value={total} />
        <StatCard label="Intensidad promedio" value={avgIntensidad} unit="/10" />
      </div>

      {/* Timeline */}
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
        <h2 className="text-sm font-medium text-slate-400 mb-4">Timeline</h2>
        {data?.length === 0 && <p className="text-slate-500 text-center py-4">Sin registros</p>}
        <div className="space-y-3">
          {data?.map((item, i) => {
            const intensityColor =
              item.intensidad >= 8 ? 'bg-red-500' :
              item.intensidad >= 5 ? 'bg-yellow-500' : 'bg-green-500'

            return (
              <div key={i} className="flex gap-3 items-start">
                <div className="flex flex-col items-center">
                  <div className={`w-3 h-3 rounded-full ${intensityColor}`} />
                  {i < data.length - 1 && <div className="w-px h-8 bg-slate-700" />}
                </div>
                <div className="flex-1 pb-2">
                  <p className="text-white text-sm">{item.situacion || 'Sin detalle'}</p>
                  <div className="flex gap-3 text-xs text-slate-500 mt-1">
                    <span>Intensidad: {item.intensidad}/10</span>
                    {item.senal_fisica && <span>Señal: {item.senal_fisica}</span>}
                    <span>
                      {(() => {
                        try { return format(parseISO(item.timestamp), 'dd/MM HH:mm') }
                        catch { return '' }
                      })()}
                    </span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Recurring */}
      {recurring.length > 0 && (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <h2 className="text-sm font-medium text-slate-400 mb-4">Situaciones recurrentes</h2>
          <div className="space-y-2">
            {recurring.map(([situation, count]) => (
              <div key={situation} className="flex justify-between items-center py-1">
                <span className="text-white text-sm capitalize">{situation}</span>
                <span className="text-slate-400 text-sm">{count}x</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
