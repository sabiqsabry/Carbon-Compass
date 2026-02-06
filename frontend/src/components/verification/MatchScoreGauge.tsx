type MatchScoreGaugeProps = {
  score: number
  completeness: number
  summary: string
}

export function MatchScoreGauge({ score, completeness, summary }: MatchScoreGaugeProps) {
  const getColor = (s: number) => {
    if (s >= 80) return { text: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20', stroke: '#34d399' }
    if (s >= 50) return { text: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20', stroke: '#fbbf24' }
    return { text: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/20', stroke: '#f87171' }
  }

  const colors = getColor(score)
  const circumference = 2 * Math.PI * 70
  const offset = circumference - (score / 100) * circumference

  const label = score >= 80 ? 'Strong Match' : score >= 50 ? 'Needs Review' : 'Major Issues'

  return (
    <div className={`rounded-xl border p-6 ${colors.bg} ${colors.border}`}>
      <h2 className="text-lg font-semibold text-slate-50 mb-4">Verification Score</h2>

      <div className="flex items-center gap-6">
        <div className="relative flex-shrink-0">
          <svg className="transform -rotate-90" width="160" height="160">
            <circle cx="80" cy="80" r="70" stroke="currentColor" strokeWidth="10" fill="none" className="text-slate-800" />
            <circle
              cx="80" cy="80" r="70"
              stroke={colors.stroke}
              strokeWidth="10"
              fill="none"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              className="transition-all duration-700"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-3xl font-bold ${colors.text}`}>{score.toFixed(0)}%</span>
            <span className="text-xs text-slate-400 mt-1">{label}</span>
          </div>
        </div>

        <div className="flex-1 space-y-3">
          <p className="text-sm text-slate-300">{summary}</p>
          <div>
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-slate-400">Data Completeness</span>
              <span className="text-slate-300">{completeness.toFixed(0)}%</span>
            </div>
            <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-emerald-500 rounded-full transition-all"
                style={{ width: `${completeness}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
