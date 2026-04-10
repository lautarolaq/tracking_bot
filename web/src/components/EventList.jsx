import { format, parseISO } from 'date-fns'

const CATEGORY_ICONS = {
  comida: '🍽️',
  gym: '💪',
  sueno: '😴',
  peso: '⚖️',
  emocion: '🧠',
  laburo: '💼',
  energia: '⚡',
}

function eventSummary(event) {
  const { category, data } = event
  switch (category) {
    case 'comida':
      if (data.kcal) return `${data.kcal} kcal — ${data.descripcion || ''}`
      return data.descripcion || '?'
    case 'gym': {
      const parts = [data.ejercicio || '?']
      if (data.peso_kg) parts.push(`${data.peso_kg}kg`)
      if (data.reps && data.sets) parts.push(`${data.reps}x${data.sets}`)
      if (data.distancia_km) parts.push(`${data.distancia_km}km`)
      return parts.join(' ')
    }
    case 'sueno':
      return `${data.horas || '?'}h — calidad ${data.calidad || '?'}/10`
    case 'peso':
      return `${data.kg || '?'} kg`
    case 'emocion':
      return `${data.situacion || '?'} — intensidad ${data.intensidad || '?'}/10`
    case 'laburo':
      return `${data.proyecto || '?'} — estrés ${data.estres || '?'}/10`
    case 'energia':
      return `Nivel ${data.nivel || '?'}/10`
    default:
      return JSON.stringify(data)
  }
}

export default function EventList({ events }) {
  if (!events || events.length === 0) {
    return <div className="text-slate-500 text-center py-4">Sin eventos</div>
  }

  return (
    <div className="space-y-2">
      {events.map((event) => (
        <div
          key={event.id}
          className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 flex items-start gap-3"
        >
          <span className="text-xl">{CATEGORY_ICONS[event.category] || '📝'}</span>
          <div className="flex-1 min-w-0">
            <p className="text-sm text-white truncate">{eventSummary(event)}</p>
            <p className="text-xs text-slate-500 mt-1">
              {(() => {
                try {
                  return format(parseISO(event.timestamp), 'dd/MM HH:mm')
                } catch {
                  return event.timestamp
                }
              })()}
            </p>
          </div>
        </div>
      ))}
    </div>
  )
}
