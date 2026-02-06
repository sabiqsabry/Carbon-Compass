import { Download, Leaf } from 'lucide-react'

type EmissionItem = {
  activity_type: string
  activity_amount: number
  activity_unit: string
  emissions_kg_co2e: number
  emissions_tonnes_co2e: number
  scope: number
  calculation_details: string
}

type EmissionsResultProps = {
  data: {
    total_kg_co2e: number
    total_tonnes_co2e: number
    breakdown: EmissionItem[]
    activity_count: number
    warnings: string[]
  }
}

export function EmissionsResult({ data }: EmissionsResultProps) {
  const flightEquivalent = (data.total_tonnes_co2e / 1.6).toFixed(1)

  const downloadCSV = () => {
    const headers = ['Activity', 'Amount', 'Unit', 'Emissions (kg CO2e)', 'Emissions (tonnes CO2e)', 'Scope']
    const rows = data.breakdown.map((item) => [
      item.activity_type,
      item.activity_amount,
      item.activity_unit,
      item.emissions_kg_co2e.toFixed(2),
      item.emissions_tonnes_co2e.toFixed(6),
      `Scope ${item.scope}`,
    ])
    const csv = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'emissions_breakdown.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-5">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-50">Emissions Results</h2>
          <p className="text-sm text-slate-400 mt-1">
            Based on {data.activity_count} activities
          </p>
        </div>
        <button
          onClick={downloadCSV}
          className="flex items-center gap-2 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 hover:bg-slate-800 transition-colors"
        >
          <Download className="h-4 w-4" />
          CSV
        </button>
      </div>

      {/* Total */}
      <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-5">
        <div className="flex items-center gap-3 mb-2">
          <Leaf className="h-6 w-6 text-emerald-400" />
          <span className="text-sm font-medium text-emerald-300">Total Carbon Footprint</span>
        </div>
        <p className="text-3xl font-bold text-slate-50">
          {data.total_tonnes_co2e.toFixed(2)} <span className="text-lg font-normal text-slate-400">tonnes CO2e</span>
        </p>
        <p className="text-sm text-slate-400 mt-1">
          Equivalent to ~{flightEquivalent} return flights London - New York
        </p>
      </div>

      {/* Breakdown Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-800">
              <th className="text-left py-3 px-2 text-slate-400 font-medium">Activity</th>
              <th className="text-right py-3 px-2 text-slate-400 font-medium">Amount</th>
              <th className="text-right py-3 px-2 text-slate-400 font-medium">Emissions</th>
              <th className="text-center py-3 px-2 text-slate-400 font-medium">Scope</th>
            </tr>
          </thead>
          <tbody>
            {data.breakdown.map((item, idx) => (
              <tr key={idx} className="border-b border-slate-800/50">
                <td className="py-3 px-2 text-slate-200 capitalize">{item.activity_type}</td>
                <td className="py-3 px-2 text-right text-slate-300">
                  {item.activity_amount.toLocaleString()} {item.activity_unit}
                </td>
                <td className="py-3 px-2 text-right text-slate-50 font-medium">
                  {item.emissions_kg_co2e.toLocaleString(undefined, { maximumFractionDigits: 1 })} kg
                </td>
                <td className="py-3 px-2 text-center">
                  <span
                    className={[
                      'inline-block rounded-full px-2 py-0.5 text-xs font-medium',
                      item.scope === 1
                        ? 'bg-red-500/10 text-red-400'
                        : item.scope === 2
                          ? 'bg-amber-500/10 text-amber-400'
                          : 'bg-blue-500/10 text-blue-400',
                    ].join(' ')}
                  >
                    {item.scope}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Warnings */}
      {data.warnings.length > 0 && (
        <div className="rounded-lg bg-amber-500/10 border border-amber-500/20 p-4">
          <p className="text-sm font-medium text-amber-300 mb-2">Warnings</p>
          <ul className="space-y-1">
            {data.warnings.map((w, i) => (
              <li key={i} className="text-xs text-amber-200/70">{w}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
