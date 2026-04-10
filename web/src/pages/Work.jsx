import { format, parseISO } from 'date-fns'
import { api } from '../api'
import { useData } from '../hooks/useData'
import StatCard from '../components/StatCard'

export default function Work({ days }) {
  const { data, loading } = useData(() => api.getWork(days), [days])

  if (loading) return <div className="text-slate-400 text-center py-12">Cargando...</div>

  // Aggregate by project
  const byProject = {}
  data?.forEach((d) => {
    const proj = d.proyecto || 'General'
    if (!byProject[proj]) byProject[proj] = { total: 0, maxStress: 0, sumStress: 0 }
    byProject[proj].total += 1
    byProject[proj].maxStress = Math.max(byProject[proj].maxStress, d.estres)
    byProject[proj].sumStress += d.estres
  })
  const projects = Object.entries(byProject)
    .map(([name, stats]) => ({
      name,
      ...stats,
      avgStress: (stats.sumStress / stats.total).toFixed(1),
    }))
    .sort((a, b) => b.maxStress - a.maxStress)

  const avgStress = data?.length
    ? (data.reduce((s, d) => s + d.estres, 0) / data.length).toFixed(1)
    : '—'

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-white">Laburo</h1>

      <div className="grid grid-cols-2 gap-4">
        <StatCard label="Registros" value={data?.length || 0} />
        <StatCard label="Estrés promedio" value={avgStress} unit="/10" />
      </div>

      {/* Projects with high stress */}
      {projects.length > 0 && (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <h2 className="text-sm font-medium text-slate-400 mb-4">Proyectos</h2>
          <div className="space-y-2">
            {projects.map((proj) => {
              const barWidth = (proj.maxStress / 10) * 100
              const barColor =
                proj.maxStress >= 8 ? 'bg-red-500' :
                proj.maxStress >= 5 ? 'bg-yellow-500' : 'bg-green-500'
              return (
                <div key={proj.name} className="py-2">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-white">{proj.name}</span>
                    <span className="text-slate-400">
                      max {proj.maxStress}/10 · prom {proj.avgStress}/10 · {proj.total} registros
                    </span>
                  </div>
                  <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div className={`h-full ${barColor} rounded-full`} style={{ width: `${barWidth}%` }} />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Timeline */}
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
        <h2 className="text-sm font-medium text-slate-400 mb-4">Timeline</h2>
        {(!data || data.length === 0) && <p className="text-slate-500 text-center py-4">Sin registros</p>}
        <div className="space-y-2">
          {data?.map((item, i) => (
            <div key={i} className="flex items-start gap-3 py-2 border-b border-slate-700 last:border-0">
              <div className="text-xs text-slate-500 w-20 flex-shrink-0">
                {(() => {
                  try { return format(parseISO(item.timestamp), 'dd/MM HH:mm') }
                  catch { return '' }
                })()}
              </div>
              <div className="flex-1">
                <span className="text-white text-sm">{item.proyecto || 'General'}</span>
                {item.contexto && (
                  <p className="text-slate-400 text-xs mt-0.5">{item.contexto}</p>
                )}
              </div>
              <span className={`text-sm font-medium ${item.estres >= 7 ? 'text-red-400' : item.estres >= 4 ? 'text-yellow-400' : 'text-green-400'}`}>
                {item.estres}/10
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
