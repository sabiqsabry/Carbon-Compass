import { useState } from 'react'
import { ChevronDown, ChevronRight, AlertTriangle, Lightbulb } from 'lucide-react'

type Discrepancy = {
  metric_type: string
  reported_value: number
  reported_unit: string
  calculated_value: number
  calculated_unit: string
  difference_absolute: number
  difference_percentage: number
  severity: string
  possible_explanations: string[]
}

type DiscrepancyListProps = {
  discrepancies: Discrepancy[]
  recommendations: string[]
}

const SEVERITY_STYLES: Record<string, string> = {
  minor: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  moderate: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
  major: 'bg-red-500/10 text-red-400 border-red-500/20',
}

export function DiscrepancyList({ discrepancies, recommendations }: DiscrepancyListProps) {
  const [expanded, setExpanded] = useState<Set<number>>(new Set())

  const toggle = (idx: number) => {
    const next = new Set(expanded)
    if (next.has(idx)) next.delete(idx)
    else next.add(idx)
    setExpanded(next)
  }

  return (
    <div className="space-y-6">
      {/* Discrepancies */}
      {discrepancies.length > 0 && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
          <h2 className="text-lg font-semibold text-slate-50 mb-4 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-400" />
            Discrepancies ({discrepancies.length})
          </h2>
          <div className="space-y-3">
            {discrepancies.map((d, idx) => {
              const isOpen = expanded.has(idx)
              const styles = SEVERITY_STYLES[d.severity] || SEVERITY_STYLES.minor
              return (
                <div key={idx} className={`rounded-lg border p-4 ${styles}`}>
                  <button
                    onClick={() => toggle(idx)}
                    className="flex items-center justify-between w-full text-left"
                  >
                    <div className="flex items-center gap-3">
                      {isOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                      <span className="font-medium text-sm">{d.metric_type}</span>
                      <span className="text-xs uppercase tracking-wide opacity-70 border rounded px-1.5 py-0.5 border-current">
                        {d.severity}
                      </span>
                    </div>
                    <span className="text-sm font-mono">
                      {d.difference_percentage > 0 ? '+' : ''}{d.difference_percentage.toFixed(1)}%
                    </span>
                  </button>
                  {isOpen && (
                    <div className="mt-3 ml-7 space-y-2 text-sm">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-xs opacity-70 mb-0.5">Reported</p>
                          <p className="font-medium">{d.reported_value.toLocaleString()} {d.reported_unit}</p>
                        </div>
                        <div>
                          <p className="text-xs opacity-70 mb-0.5">Calculated</p>
                          <p className="font-medium">{d.calculated_value.toLocaleString()} {d.calculated_unit}</p>
                        </div>
                      </div>
                      {d.possible_explanations.length > 0 && (
                        <div className="pt-2">
                          <p className="text-xs opacity-70 mb-1">Possible explanations:</p>
                          <ul className="space-y-1">
                            {d.possible_explanations.map((exp, i) => (
                              <li key={i} className="text-xs opacity-80 flex items-start gap-1.5">
                                <span className="mt-0.5">•</span>
                                <span>{exp}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
          <h2 className="text-lg font-semibold text-slate-50 mb-4 flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-emerald-400" />
            Recommendations
          </h2>
          <ul className="space-y-2">
            {recommendations.map((rec, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm text-slate-300">
                <span className="text-emerald-400 mt-0.5 flex-shrink-0">•</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
