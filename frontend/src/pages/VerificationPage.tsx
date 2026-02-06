import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ShieldCheck } from 'lucide-react'
import { api } from '../services/api'
import { ReportSelector } from '../components/verification/ReportSelector'
import { VerificationInput } from '../components/verification/VerificationInput'
import { MatchScoreGauge } from '../components/verification/MatchScoreGauge'
import { DiscrepancyList } from '../components/verification/DiscrepancyList'
import { ComparisonTable } from '../components/verification/ComparisonTable'

type VerificationData = {
  report: string
  verification: {
    match_score: number
    discrepancies: Array<{
      metric_type: string
      reported_value: number
      reported_unit: string
      calculated_value: number
      calculated_unit: string
      difference_absolute: number
      difference_percentage: number
      severity: string
      possible_explanations: string[]
    }>
    verified_metrics: Array<{
      metric_type: string
      reported_value: number
      calculated_value: number | null
      status: string
      confidence: number
    }>
    summary: string
    recommendations: string[]
    data_completeness: number
  }
  calculated_emissions: {
    total_kg_co2e: number
    total_tonnes_co2e: number
    by_scope: Record<string, number>
    by_category: Record<string, number>
    breakdown: Record<string, unknown>[]
    activity_count: number
  }
}

export function VerificationPage(): JSX.Element {
  const [selectedReport, setSelectedReport] = useState<string | null>(null)
  const [verificationResult, setVerificationResult] = useState<VerificationData | null>(null)

  const { data: reports = [] } = useQuery({
    queryKey: ['reports'],
    queryFn: async () => {
      const res = await api.get('/reports')
      return res.data ?? []
    },
  })

  return (
    <section className="space-y-6">
      <header className="space-y-1">
        <div className="flex items-center gap-3">
          <ShieldCheck className="h-7 w-7 text-emerald-400" />
          <h1 className="text-2xl font-semibold text-slate-50">Verify Report Claims</h1>
        </div>
        <p className="text-sm text-slate-400">
          Compare what's reported in sustainability documents vs. what the activity data shows
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Input */}
        <div className="space-y-6">
          <ReportSelector
            reports={reports}
            selectedReport={selectedReport}
            onSelect={setSelectedReport}
          />
          {selectedReport && (
            <VerificationInput
              reportFilename={selectedReport}
              onResult={setVerificationResult}
            />
          )}
        </div>

        {/* Right: Results */}
        <div className="space-y-6">
          {verificationResult && (
            <>
              <MatchScoreGauge
                score={verificationResult.verification.match_score}
                completeness={verificationResult.verification.data_completeness}
                summary={verificationResult.verification.summary}
              />
            </>
          )}
        </div>
      </div>

      {/* Full-width results */}
      {verificationResult && (
        <div className="space-y-6">
          <ComparisonTable metrics={verificationResult.verification.verified_metrics} />
          <DiscrepancyList
            discrepancies={verificationResult.verification.discrepancies}
            recommendations={verificationResult.verification.recommendations}
          />
        </div>
      )}
    </section>
  )
}
