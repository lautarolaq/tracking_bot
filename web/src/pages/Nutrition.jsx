import { format, parseISO } from 'date-fns'
import { api } from '../api'
import { useData } from '../hooks/useData'
import StatCard from '../components/StatCard'
import BarChart from '../components/BarChart'

export default function Nutrition({ days }) {
  const { data, loading } = useData(() => api.getNutrition(days), [days])
  const { data: events } = useData(() => api.getEvents({ category: 'comida', days, limit: 500 }), [days])

  if (loading) return <div className="text-slate-400 text-center py-12">Cargando...</div>

  const withKcal = data?.filter((d) => d.kcal > 0) || []
  const hasKcalData = withKcal.length > 0

  const avgKcal = hasKcalData
    ? Math.round(withKcal.reduce((s, d) => s + d.kcal, 0) / withKcal.length)
    : 0
  const daysInDeficit = withKcal.filter((d) => d.kcal < 2000).length
  const totalDays = data?.length || 0

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-white">Nutrición</h1>

      <div className="grid grid-cols-3 gap-4">
        {hasKcalData ? (
          <>
            <StatCard label="Promedio diario" value={avgKcal} unit="kcal" />
            <StatCard label="Días en déficit" value={daysInDeficit} />
            <StatCard label="Días registrados" value={totalDays} />
          </>
        ) : (
          <>
            <StatCard label="Días registrados" value={totalDays} />
            <StatCard label="Comidas totales" value={events?.length || 0} />
            <StatCard label="Sin datos de kcal" value="—" />
          </>
        )}
      </div>

      {/* Chart only if there's kcal data */}
      {hasKcalData && (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <h2 className="text-sm font-medium text-slate-400 mb-4">Calorías por día</h2>
          <BarChart
            data={withKcal}
            dataKey="kcal"
            color="#22c55e"
            referenceLine={2000}
            referenceLabel="Target"
          />
        </div>
      )}

      {/* Meal log - always show */}
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
        <h2 className="text-sm font-medium text-slate-400 mb-4">Registro de comidas</h2>
        <div className="space-y-3">
          {events?.slice(0, 30).map((event, i) => (
            <div key={event.id || i} className="border-b border-slate-700 last:border-0 pb-2">
              <div className="flex justify-between items-start">
                <p className="text-sm text-white flex-1">
                  {event.data?.descripcion || event.raw_input || '—'}
                </p>
                <div className="flex gap-3 ml-4 flex-shrink-0">
                  {event.data?.kcal > 0 && (
                    <span className="text-green-400 text-sm">{event.data.kcal} kcal</span>
                  )}
                  <span className="text-slate-500 text-xs">
                    {(() => {
                      try { return format(parseISO(event.timestamp), 'dd/MM') }
                      catch { return '' }
                    })()}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
