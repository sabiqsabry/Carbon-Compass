import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Download } from 'lucide-react'
import { api } from '../services/api'
import { MetricsCard } from '../components/MetricsCard'
import { GreenwashingFlags } from '../components/GreenwashingFlags'
import { RiskScoreGauge } from '../components/RiskScoreGauge'
import { ReportSummary } from '../components/ReportSummary'
import { CommitmentsList } from '../components/CommitmentsList'

type AnalysisData = {
  pdf: {
    pages_count: number
    metadata: {
      title?: string
      author?: string
    }
  }
  metrics: Array<{
    metric_type: string
    value: number
    unit: string
    year?: number
    scope?: string
    context: string
  }>
  greenwashing: {
    risk_score: number
    flags: Array<{
      indicator_type: string
      text: string
      explanation: string
      severity: string
      confidence: number
    }>
  }
  summary: {
    executive_summary: string
    section_summaries: Array<{
      section_name: string
      summary: string
    }>
    commitments: string[]
  }
  risk: {
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
}

export function AnalysisPage(): JSX.Element {
  const { filename } = useParams<{ filename: string }>()

  const { data: analysis, isLoading, error } = useQuery<AnalysisData>({
    queryKey: ['analysis', filename],
    queryFn: async () => {
      if (!filename) throw new Error('No filename provided')
      const res = await api.get(`/analysis/${encodeURIComponent(filename)}`)
      return res.data
    },
    enabled: !!filename,
  })

  const formatFilename = (filename?: string) => {
    if (!filename) return 'Report'
    return filename.replace(/\.pdf$/i, '').replace(/[_-]/g, ' ').trim()
  }

  const downloadJSON = () => {
    if (!analysis || !filename) return
    const dataStr = JSON.stringify(analysis, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${filename.replace(/\.pdf$/i, '')}_analysis.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-slate-400">Loading analysis...</div>
      </div>
    )
  }

  if (error || !analysis) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-400 mb-4">Analysis not found or failed to load.</p>
        <Link to="/reports" className="text-emerald-400 hover:text-emerald-300 underline">
          Back to Reports
        </Link>
      </div>
    )
  }

  return (
    <section className="space-y-6">
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            to="/reports"
            className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-semibold text-slate-50">{formatFilename(filename)}</h1>
            <p className="text-sm text-slate-400 mt-1">
              Environmental Analysis • {analysis.pdf.pages_count} pages
            </p>
          </div>
        </div>
        <button
          onClick={downloadJSON}
          className="flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-700 bg-slate-900/60 text-slate-200 hover:bg-slate-800 transition-colors"
        >
          <Download className="h-4 w-4" />
          Download JSON
        </button>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="lg:col-span-2">
          <RiskScoreGauge risk={analysis.risk} />
        </div>

        <MetricsCard metrics={analysis.metrics} />

        <GreenwashingFlags greenwashing={analysis.greenwashing} />

        <div className="lg:col-span-2">
          <ReportSummary summary={analysis.summary} />
        </div>

        <div className="lg:col-span-2">
          <CommitmentsList commitments={analysis.summary.commitments} />
        </div>
      </div>
    </section>
  )
}
