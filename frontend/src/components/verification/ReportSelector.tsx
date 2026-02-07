import { useQuery } from '@tanstack/react-query'
import { FileText, AlertTriangle, Loader2 } from 'lucide-react'
import { api } from '../../services/api'

type Report = {
  filename: string
  size_bytes?: number
}

type MetricSummary = {
  metric_type: string
  value: number
  unit: string
  scope: string | null
  confidence: number
}

type ReportSummary = {
  report: string
  has_analysis: boolean
  metrics_count?: number
  metrics?: MetricSummary[]
}

type ReportSelectorProps = {
  reports: Report[]
  selectedReport: string | null
  onSelect: (filename: string) => void
}

export function ReportSelector({ reports, selectedReport, onSelect }: ReportSelectorProps) {
  const { data: summary, isLoading: loadingSummary } = useQuery<ReportSummary>({
    queryKey: ['report-summary', selectedReport],
    queryFn: async () => {
      const res = await api.get(`/verify/${encodeURIComponent(selectedReport!)}/summary`)
      return res.data
    },
    enabled: !!selectedReport,
  })

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
      <h2 className="text-lg font-semibold text-slate-50 mb-4">Select Report to Verify</h2>

      {reports.length === 0 ? (
        <div className="flex items-center gap-3 rounded-lg bg-amber-500/10 border border-amber-500/20 p-4">
          <AlertTriangle className="h-5 w-5 text-amber-400 flex-shrink-0" />
          <div>
            <p className="text-sm text-amber-300">No analysed reports found</p>
            <p className="text-xs text-amber-200/60 mt-1">
              Upload and analyse a sustainability report first, then come back to verify it.
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-2">
          {reports.map((report) => (
            <button
              key={report.filename}
              onClick={() => onSelect(report.filename)}
              className={[
                'flex items-center gap-3 w-full rounded-lg border p-3 text-left transition-colors',
                selectedReport === report.filename
                  ? 'border-emerald-500/30 bg-emerald-500/10'
                  : 'border-slate-700 bg-slate-800/30 hover:bg-slate-800/60',
              ].join(' ')}
            >
              <FileText
                className={`h-5 w-5 flex-shrink-0 ${selectedReport === report.filename ? 'text-emerald-400' : 'text-slate-500'}`}
              />
              <div className="flex-1 min-w-0">
                <p
                  className={`text-sm font-medium truncate ${selectedReport === report.filename ? 'text-emerald-300' : 'text-slate-200'}`}
                >
                  {report.filename}
                </p>
                {report.size_bytes && (
                  <p className="text-xs text-slate-500">{(report.size_bytes / 1024).toFixed(0)} KB</p>
                )}
              </div>
            </button>
          ))}
        </div>
      )}

      {/* Metrics Summary */}
      {selectedReport && (
        <div className="mt-4 pt-4 border-t border-slate-800">
          {loadingSummary ? (
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading report metrics...
            </div>
          ) : summary?.has_analysis ? (
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Report Claims ({summary.metrics_count} metrics extracted)
              </p>
              {summary.metrics && summary.metrics.length > 0 ? (
                <div className="space-y-1.5">
                  {summary.metrics
                    .filter((m) => m.metric_type === 'carbon_emissions')
                    .map((m, i) => (
                      <div
                        key={i}
                        className="flex items-center justify-between rounded-md bg-slate-800/50 px-3 py-2 text-xs"
                      >
                        <span className="text-slate-300">
                          {m.scope ? `Scope ${m.scope}` : 'Total'} Emissions
                        </span>
                        <span className="text-slate-100 font-medium">
                          {m.value.toLocaleString()} {m.unit}
                        </span>
                      </div>
                    ))}
                  {summary.metrics.filter((m) => m.metric_type === 'carbon_emissions').length === 0 && (
                    <p className="text-xs text-slate-500">No carbon emission metrics found in report</p>
                  )}
                </div>
              ) : (
                <p className="text-xs text-slate-500">No metrics extracted from this report</p>
              )}
            </div>
          ) : summary ? (
            <p className="text-xs text-amber-400">This report has not been analysed yet</p>
          ) : null}
        </div>
      )}
    </div>
  )
}
