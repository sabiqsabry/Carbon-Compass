import { AlertTriangle, CheckCircle, XCircle, Info } from 'lucide-react'

type RiskData = {
  overall_score: number
  risk_level: string
  components: {
    transparency: number
    commitment: number
    credibility: number
    data_quality: number
    verification: number
  }
  recommendations: string[]
}

type RiskScoreGaugeProps = {
  risk: RiskData
}

export function RiskScoreGauge({ risk }: RiskScoreGaugeProps) {
  const getRiskColor = (score: number) => {
    if (score <= 25) return 'text-emerald-400'
    if (score <= 50) return 'text-amber-400'
    if (score <= 75) return 'text-orange-400'
    return 'text-red-400'
  }

  const getRiskBgColor = (score: number) => {
    if (score <= 25) return 'bg-emerald-500/10 border-emerald-500/20'
    if (score <= 50) return 'bg-amber-500/10 border-amber-500/20'
    if (score <= 75) return 'bg-orange-500/10 border-orange-500/20'
    return 'bg-red-500/10 border-red-500/20'
  }

  const getRiskIcon = (level: string) => {
    if (level === 'LOW') return <CheckCircle className="h-6 w-6 text-emerald-400" />
    if (level === 'MEDIUM') return <Info className="h-6 w-6 text-amber-400" />
    if (level === 'HIGH') return <AlertTriangle className="h-6 w-6 text-orange-400" />
    return <XCircle className="h-6 w-6 text-red-400" />
  }

  const circumference = 2 * Math.PI * 90
  const offset = circumference - (risk.overall_score / 100) * circumference

  return (
    <div className={`rounded-xl border p-6 ${getRiskBgColor(risk.overall_score)}`}>
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-slate-50 mb-1">Environmental Risk Score</h2>
          <p className="text-sm text-slate-400">Overall transparency and credibility assessment</p>
        </div>
        {getRiskIcon(risk.risk_level)}
      </div>

      <div className="flex items-center gap-8">
        <div className="relative flex-shrink-0">
          <svg className="transform -rotate-90" width="200" height="200">
            <circle
              cx="100"
              cy="100"
              r="90"
              stroke="currentColor"
              strokeWidth="12"
              fill="none"
              className="text-slate-800"
            />
            <circle
              cx="100"
              cy="100"
              r="90"
              stroke="currentColor"
              strokeWidth="12"
              fill="none"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              className={`transition-all ${getRiskColor(risk.overall_score)}`}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div className={`text-4xl font-bold ${getRiskColor(risk.overall_score)}`}>
              {risk.overall_score.toFixed(0)}
            </div>
            <div className="text-sm text-slate-400 mt-1">{risk.risk_level}</div>
          </div>
        </div>

        <div className="flex-1 space-y-3">
          <div>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-slate-300">Transparency</span>
              <span className="text-slate-400">{risk.components.transparency.toFixed(0)}%</span>
            </div>
            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-emerald-500 transition-all"
                style={{ width: `${risk.components.transparency}%` }}
              />
            </div>
          </div>
          <div>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-slate-300">Commitment</span>
              <span className="text-slate-400">{risk.components.commitment.toFixed(0)}%</span>
            </div>
            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-emerald-500 transition-all"
                style={{ width: `${risk.components.commitment}%` }}
              />
            </div>
          </div>
          <div>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-slate-300">Credibility</span>
              <span className="text-slate-400">{risk.components.credibility.toFixed(0)}%</span>
            </div>
            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-emerald-500 transition-all"
                style={{ width: `${risk.components.credibility}%` }}
              />
            </div>
          </div>
          <div>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-slate-300">Data Quality</span>
              <span className="text-slate-400">{risk.components.data_quality.toFixed(0)}%</span>
            </div>
            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-emerald-500 transition-all"
                style={{ width: `${risk.components.data_quality}%` }}
              />
            </div>
          </div>
          <div>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-slate-300">Verification</span>
              <span className="text-slate-400">{risk.components.verification.toFixed(0)}%</span>
            </div>
            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-emerald-500 transition-all"
                style={{ width: `${risk.components.verification}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {risk.recommendations.length > 0 && (
        <div className="mt-6 pt-6 border-t border-slate-700">
          <h3 className="text-sm font-semibold text-slate-200 mb-3">Recommendations</h3>
          <ul className="space-y-2">
            {risk.recommendations.map((rec, idx) => (
              <li key={idx} className="text-sm text-slate-300 flex items-start gap-2">
                <span className="text-emerald-400 mt-0.5">•</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
