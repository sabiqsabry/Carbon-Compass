import { ArrowLeft, Calculator, Loader2, AlertCircle, CheckCircle } from 'lucide-react'

type FilePreview = {
  columns: string[]
  rows: Record<string, unknown>[]
  total_columns: number
  detected_mapping: Record<string, string | null>
}

type ValidationErrorsProps = {
  preview: FilePreview
  mapping: Record<string, string | null>
  loading: boolean
  error: string | null
  onCalculate: () => void
  onBack: () => void
}

export function ValidationErrors({ preview, mapping, loading, error, onCalculate, onBack }: ValidationErrorsProps) {
  const mappedFields = Object.entries(mapping).filter(([, v]) => v !== null)
  const requiredMapped = ['category', 'amount', 'unit'].every(
    (f) => mapping[f] !== null && mapping[f] !== undefined
  )

  return (
    <div className="space-y-6">
      {/* Review Summary */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
        <h2 className="text-lg font-semibold text-slate-50 mb-4">Step 3: Review & Calculate</h2>

        <div className="space-y-3">
          {/* File Info */}
          <div className="flex items-center gap-2 text-sm">
            <CheckCircle className="h-4 w-4 text-emerald-400" />
            <span className="text-slate-300">
              File loaded with <span className="text-emerald-400 font-medium">{preview.columns.length}</span> columns
              and <span className="text-emerald-400 font-medium">{preview.rows.length}+</span> rows
            </span>
          </div>

          {/* Mapped Columns */}
          <div className="flex items-center gap-2 text-sm">
            <CheckCircle className="h-4 w-4 text-emerald-400" />
            <span className="text-slate-300">
              <span className="text-emerald-400 font-medium">{mappedFields.length}</span> columns mapped
            </span>
          </div>

          {/* Mapping Details */}
          <div className="rounded-lg bg-slate-800/50 border border-slate-700 p-4">
            <p className="text-xs font-medium text-slate-400 mb-2">Column Mapping</p>
            <div className="grid grid-cols-2 gap-2">
              {mappedFields.map(([field, col]) => (
                <div key={field} className="flex items-center gap-2 text-xs">
                  <span className="text-slate-500 capitalize">{field.replace('_', ' ')}:</span>
                  <span className="text-slate-200">{col}</span>
                </div>
              ))}
            </div>
          </div>

          {!requiredMapped && (
            <div className="flex items-start gap-2 rounded-lg bg-amber-500/10 border border-amber-500/20 p-3">
              <AlertCircle className="h-4 w-4 text-amber-400 mt-0.5 flex-shrink-0" />
              <p className="text-xs text-amber-300">
                Required columns (Category, Amount, Unit) must be mapped before calculating.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-start gap-2 rounded-lg bg-red-500/10 border border-red-500/20 p-4">
          <AlertCircle className="h-4 w-4 text-red-400 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm font-medium text-red-300">Calculation failed</p>
            <p className="text-xs text-red-200/70 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="flex items-center gap-2 rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </button>
        <button
          onClick={onCalculate}
          disabled={loading || !requiredMapped}
          className="flex items-center gap-2 rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-emerald-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Calculator className="h-4 w-4" />
          )}
          {loading ? 'Calculating...' : 'Calculate Emissions'}
        </button>
      </div>
    </div>
  )
}
