import {
  ResponsiveContainer,
  LineChart as RLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts'

const COLORS = ['#3b82f6', '#f59e0b', '#22c55e', '#8b5cf6', '#ef4444']

export default function LineChart({ data, lines, xKey = 'date', height = 300, formatX }) {
  if (!data || data.length === 0) {
    return <div className="text-slate-500 text-center py-8">Sin datos</div>
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RLineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis
          dataKey={xKey}
          stroke="#64748b"
          tick={{ fill: '#64748b', fontSize: 12 }}
          tickFormatter={formatX || ((v) => v.slice(5))}
        />
        <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 12 }} domain={['auto', 'auto']} />
        <Tooltip
          contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
          labelStyle={{ color: '#e2e8f0' }}
          itemStyle={{ color: '#e2e8f0' }}
          formatter={(v) => typeof v === 'number' ? Math.round(v * 10) / 10 : v}
        />
        {lines.map((line, i) => (
          <Line
            key={line.key}
            type="monotone"
            dataKey={line.key}
            name={line.label || line.key}
            stroke={line.color || COLORS[i % COLORS.length]}
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
        ))}
      </RLineChart>
    </ResponsiveContainer>
  )
}
