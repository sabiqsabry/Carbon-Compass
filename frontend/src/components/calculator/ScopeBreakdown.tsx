import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'

type ScopeBreakdownProps = {
  data: {
    by_scope: Record<string, number>
    total_kg_co2e: number
  }
}

const SCOPE_COLORS = {
  scope_1: '#ef4444',
  scope_2: '#f59e0b',
  scope_3: '#3b82f6',
}

const SCOPE_LABELS: Record<string, string> = {
  scope_1: 'Scope 1 (Direct)',
  scope_2: 'Scope 2 (Energy)',
  scope_3: 'Scope 3 (Value Chain)',
}

export function ScopeBreakdown({ data }: ScopeBreakdownProps) {
  const chartData = Object.entries(data.by_scope)
    .filter(([, value]) => value > 0)
    .map(([key, value]) => ({
      name: SCOPE_LABELS[key] || key,
      value: Math.round(value * 100) / 100,
      color: SCOPE_COLORS[key as keyof typeof SCOPE_COLORS] || '#64748b',
      percentage: data.total_kg_co2e > 0 ? ((value / data.total_kg_co2e) * 100).toFixed(1) : '0',
    }))

  if (chartData.length === 0) {
    return null
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
      <h2 className="text-lg font-semibold text-slate-50 mb-4">Scope Breakdown</h2>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={90}
              paddingAngle={3}
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={index} fill={entry.color} stroke="transparent" />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #334155',
                borderRadius: '8px',
                color: '#f1f5f9',
              }}
              formatter={(value: number) => [`${value.toLocaleString()} kg CO2e`, '']}
            />
            <Legend
              formatter={(value) => <span className="text-sm text-slate-300">{value}</span>}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Scope Summary */}
      <div className="mt-4 space-y-2">
        {chartData.map((item) => (
          <div key={item.name} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <div className="h-3 w-3 rounded-full" style={{ backgroundColor: item.color }} />
              <span className="text-slate-300">{item.name}</span>
            </div>
            <div className="text-slate-50 font-medium">
              {(item.value / 1000).toFixed(2)} t ({item.percentage}%)
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
