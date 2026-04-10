export default function StatCard({ label, value, delta, unit = '', invertColor = false }) {
  const deltaNum = parseFloat(delta)
  const hasDelta = delta !== undefined && delta !== null && !isNaN(deltaNum)

  let deltaColor = 'text-slate-400'
  if (hasDelta && deltaNum !== 0) {
    const isPositiveGood = !invertColor
    const isPositive = deltaNum > 0
    deltaColor = (isPositive === isPositiveGood) ? 'text-green-400' : 'text-red-400'
  }

  const arrow = hasDelta && deltaNum !== 0 ? (deltaNum > 0 ? '↑' : '↓') : ''
  const sign = hasDelta && deltaNum > 0 ? '+' : ''

  return (
    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
      <p className="text-slate-400 text-sm mb-1">{label}</p>
      <p className="text-2xl font-bold text-white">
        {value}{unit && <span className="text-lg text-slate-400 ml-1">{unit}</span>}
      </p>
      {hasDelta && (
        <p className={`text-sm mt-1 ${deltaColor}`}>
          {arrow} {sign}{delta}{unit}
        </p>
      )}
    </div>
  )
}
