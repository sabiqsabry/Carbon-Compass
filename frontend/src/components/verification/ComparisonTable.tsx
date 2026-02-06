import { CheckCircle, AlertTriangle, XCircle, HelpCircle } from 'lucide-react'

type VerifiedMetric = {
  metric_type: string
  reported_value: number
  calculated_value: number | null
  status: string
  confidence: number
}

type ComparisonTableProps = {
  metrics: VerifiedMetric[]
}

const STATUS_CONFIG: Record<string, { icon: typeof CheckCircle; color: string; label: string }> = {
  verified: { icon: CheckCircle, color: 'text-emerald-400', label: 'Match' },
  discrepancy: { icon: AlertTriangle, color: 'text-amber-400', label: 'Discrepancy' },
  unverified: { icon: HelpCircle, color: 'text-slate-500', label: 'Unverified' },
  not_calculated: { icon: XCircle, color: 'text-slate-600', label: 'No Data' },
}

export function ComparisonTable({ metrics }: ComparisonTableProps) {
  if (metrics.length === 0) return null

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
      <h2 className="text-lg font-semibold text-slate-50 mb-4">Metric Comparison</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700">
              <th className="text-left py-3 px-3 text-slate-400 font-medium">Metric</th>
              <th className="text-right py-3 px-3 text-slate-400 font-medium">Reported</th>
              <th className="text-right py-3 px-3 text-slate-400 font-medium">Calculated</th>
              <th className="text-center py-3 px-3 text-slate-400 font-medium">Status</th>
              <th className="text-right py-3 px-3 text-slate-400 font-medium">Confidence</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((m, idx) => {
              const config = STATUS_CONFIG[m.status] || STATUS_CONFIG.unverified
              const Icon = config.icon
              return (
                <tr key={idx} className="border-b border-slate-800/50">
                  <td className="py-3 px-3 text-slate-200">{m.metric_type}</td>
                  <td className="py-3 px-3 text-right text-slate-300">
                    {m.reported_value.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                  <td className="py-3 px-3 text-right text-slate-300">
                    {m.calculated_value != null
                      ? m.calculated_value.toLocaleString(undefined, { maximumFractionDigits: 0 })
                      : '—'}
                  </td>
                  <td className="py-3 px-3 text-center">
                    <div className="flex items-center justify-center gap-1.5">
                      <Icon className={`h-4 w-4 ${config.color}`} />
                      <span className={`text-xs ${config.color}`}>{config.label}</span>
                    </div>
                  </td>
                  <td className="py-3 px-3 text-right text-slate-400">
                    {(m.confidence * 100).toFixed(0)}%
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
