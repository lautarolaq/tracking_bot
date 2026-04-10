import { api } from '../api'
import { useData } from '../hooks/useData'
import StatCard from '../components/StatCard'
import BarChart from '../components/BarChart'

export default function Gym({ days }) {
  const { data, loading } = useData(() => api.getGym(days), [days])

  if (loading) return <div className="text-slate-400 text-center py-12">Cargando...</div>

  const porDia = data?.por_dia || []
  const porEjercicio = data?.por_ejercicio || []
  const totalDias = porDia.length
  const volTotal = porDia.reduce((s, d) => s + d.volumen_total, 0)

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-white">Gym</h1>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        <StatCard label="Días de gym" value={totalDias} />
        <StatCard label="Volumen total" value={Math.round(volTotal).toLocaleString()} unit="kg" />
        <StatCard label="Ejercicios distintos" value={porEjercicio.length} />
      </div>

      <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
        <h2 className="text-sm font-medium text-slate-400 mb-4">Volumen por día</h2>
        <BarChart data={porDia} dataKey="volumen_total" color="#f59e0b" />
      </div>

      {/* PRs / Exercise summary */}
      {porEjercicio.length > 0 && (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <h2 className="text-sm font-medium text-slate-400 mb-4">Por ejercicio</h2>
          <div className="space-y-2">
            {porEjercicio
              .sort((a, b) => b.max_peso - a.max_peso)
              .map((ex) => (
                <div key={ex.ejercicio} className="flex items-center justify-between py-2 border-b border-slate-700 last:border-0">
                  <span className="text-white text-sm">{ex.ejercicio}</span>
                  <div className="flex gap-4 text-sm">
                    <span className="text-blue-400">Max: {ex.max_peso}kg</span>
                    <span className="text-slate-400">{ex.total_sets} sets</span>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  )
}
