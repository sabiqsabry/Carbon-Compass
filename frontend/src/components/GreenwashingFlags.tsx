import { useState } from 'react'
import { AlertTriangle, AlertCircle, Info, ChevronDown, ChevronUp } from 'lucide-react'

type GreenwashingData = {
  risk_score: number
  flags: Array<{
    indicator_type: string
    text: string
    explanation: string
    severity: string
    confidence: number
  }>
}

type GreenwashingFlagsProps = {
  greenwashing: GreenwashingData
}

export function GreenwashingFlags({ greenwashing }: GreenwashingFlagsProps) {
  const [expandedFlags, setExpandedFlags] = useState<Set<number>>(new Set())

  const toggleExpand = (idx: number) => {
    const newSet = new Set(expandedFlags)
    if (newSet.has(idx)) {
      newSet.delete(idx)
    } else {
      newSet.add(idx)
    }
    setExpandedFlags(newSet)
  }

  const getSeverityColor = (severity: string) => {
    if (severity === 'high') return 'bg-red-500/20 text-red-300 border-red-500/30'
    if (severity === 'medium') return 'bg-amber-500/20 text-amber-300 border-amber-500/30'
    return 'bg-slate-700/50 text-slate-300 border-slate-600'
  }

  const getSeverityIcon = (severity: string) => {
    if (severity === 'high') return <AlertTriangle className="h-4 w-4" />
    if (severity === 'medium') return <AlertCircle className="h-4 w-4" />
    return <Info className="h-4 w-4" />
  }

  const sortedFlags = [...greenwashing.flags].sort((a, b) => {
    const severityOrder = { high: 3, medium: 2, low: 1 }
    return (severityOrder[b.severity as keyof typeof severityOrder] || 0) -
           (severityOrder[a.severity as keyof typeof severityOrder] || 0)
  })

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-slate-50 mb-1">Greenwashing Detection</h2>
          <p className="text-sm text-slate-400">{greenwashing.flags.length} flags detected</p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-amber-400">{greenwashing.risk_score.toFixed(0)}</div>
          <div className="text-xs text-slate-400">Risk Score</div>
        </div>
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {sortedFlags.length === 0 ? (
          <p className="text-sm text-slate-500 text-center py-8">No greenwashing flags detected</p>
        ) : (
          sortedFlags.map((flag, idx) => {
            const isExpanded = expandedFlags.has(idx)
            return (
              <div
                key={idx}
                className={`rounded-lg border p-3 ${getSeverityColor(flag.severity)}`}
              >
                <div className="flex items-start gap-2">
                  <div className="shrink-0 mt-0.5">
                    {getSeverityIcon(flag.severity)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-medium uppercase tracking-wide">
                        {flag.indicator_type.replace(/_/g, ' ')}
                      </span>
                      <button
                        onClick={() => toggleExpand(idx)}
                        className="shrink-0 ml-2 text-current"
                      >
                        {isExpanded ? (
                          <ChevronUp className="h-4 w-4" />
                        ) : (
                          <ChevronDown className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                    <p className="text-sm mb-2 line-clamp-2">{flag.text}</p>
                    {isExpanded && (
                      <div className="mt-2 pt-2 border-t border-current/20">
                        <p className="text-xs opacity-90">{flag.explanation}</p>
                        <p className="text-xs mt-2 opacity-75">
                          Confidence: {(flag.confidence * 100).toFixed(0)}%
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
