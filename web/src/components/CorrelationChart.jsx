import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts'

export default function CorrelationChart({ data, xKey, yKey, xLabel, yLabel, color = '#3b82f6', height = 300 }) {
  if (!data || data.length === 0) {
    return <div className="text-slate-500 text-center py-8">Sin datos suficientes</div>
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <ScatterChart margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis
          dataKey={xKey}
          name={xLabel}
          stroke="#64748b"
          tick={{ fill: '#64748b', fontSize: 12 }}
          label={{ value: xLabel, fill: '#94a3b8', position: 'bottom' }}
        />
        <YAxis
          dataKey={yKey}
          name={yLabel}
          stroke="#64748b"
          tick={{ fill: '#64748b', fontSize: 12 }}
          label={{ value: yLabel, fill: '#94a3b8', angle: -90, position: 'insideLeft' }}
        />
        <Tooltip
          contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
          labelStyle={{ color: '#e2e8f0' }}
        />
        <Scatter data={data} fill={color} />
      </ScatterChart>
    </ResponsiveContainer>
  )
}
