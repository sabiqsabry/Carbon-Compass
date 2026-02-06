import { FileText, AlertTriangle } from 'lucide-react'

type Report = {
  filename: string
  size_bytes?: number
}

type ReportSelectorProps = {
  reports: Report[]
  selectedReport: string | null
  onSelect: (filename: string) => void
}

export function ReportSelector({ reports, selectedReport, onSelect }: ReportSelectorProps) {
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
              <FileText className={`h-5 w-5 flex-shrink-0 ${selectedReport === report.filename ? 'text-emerald-400' : 'text-slate-500'}`} />
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium truncate ${selectedReport === report.filename ? 'text-emerald-300' : 'text-slate-200'}`}>
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
    </div>
  )
}
