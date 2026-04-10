import {
  ResponsiveContainer,
  BarChart as RBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
} from 'recharts'

export default function BarChart({
  data,
  dataKey,
  xKey = 'date',
  color = '#3b82f6',
  height = 300,
  referenceLine,
  referenceLabel,
  formatX,
}) {
  if (!data || data.length === 0) {
    return <div className="text-slate-500 text-center py-8">Sin datos</div>
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RBarChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
        <XAxis
          dataKey={xKey}
          stroke="#64748b"
          tick={{ fill: '#64748b', fontSize: 12 }}
          tickFormatter={formatX || ((v) => v.slice(5))}
        />
        <YAxis stroke="#64748b" tick={{ fill: '#64748b', fontSize: 12 }} />
        <Tooltip
          contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
          labelStyle={{ color: '#e2e8f0' }}
          itemStyle={{ color: '#e2e8f0' }}
          formatter={(v) => typeof v === 'number' ? Math.round(v) : v}
        />
        <Bar dataKey={dataKey} fill={color} radius={[4, 4, 0, 0]} />
        {referenceLine && (
          <ReferenceLine
            y={referenceLine}
            stroke="#f59e0b"
            strokeDasharray="5 5"
            label={{ value: referenceLabel || '', fill: '#f59e0b', position: 'right' }}
          />
        )}
      </RBarChart>
    </ResponsiveContainer>
  )
}
