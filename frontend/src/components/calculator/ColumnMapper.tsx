import { ArrowRight, ArrowLeft } from 'lucide-react'

const REQUIRED_FIELDS = [
  { key: 'category', label: 'Category', required: true },
  { key: 'amount', label: 'Amount', required: true },
  { key: 'unit', label: 'Unit', required: true },
  { key: 'sub_category', label: 'Sub-category', required: false },
  { key: 'country', label: 'Country', required: false },
  { key: 'date', label: 'Date', required: false },
  { key: 'description', label: 'Description', required: false },
]

type ColumnMapperProps = {
  columns: string[]
  rows: Record<string, unknown>[]
  mapping: Record<string, string | null>
  onMappingChange: (mapping: Record<string, string | null>) => void
  onConfirm: () => void
  onBack: () => void
}

export function ColumnMapper({ columns, rows, mapping, onMappingChange, onConfirm, onBack }: ColumnMapperProps) {
  const updateMapping = (field: string, col: string | null) => {
    onMappingChange({ ...mapping, [field]: col || null })
  }

  const requiredMapped = REQUIRED_FIELDS
    .filter((f) => f.required)
    .every((f) => mapping[f.key])

  return (
    <div className="space-y-6">
      {/* Column Mapping */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
        <h2 className="text-lg font-semibold text-slate-50 mb-1">Step 2: Map Columns</h2>
        <p className="text-xs text-slate-400 mb-5">
          We auto-detected the mapping below. Adjust if needed.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {REQUIRED_FIELDS.map((field) => (
            <div key={field.key}>
              <label className="flex items-center gap-1.5 text-sm font-medium text-slate-300 mb-1.5">
                {field.label}
                {field.required && <span className="text-red-400 text-xs">*</span>}
              </label>
              <select
                value={mapping[field.key] || ''}
                onChange={(e) => updateMapping(field.key, e.target.value || null)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-50 focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500"
              >
                <option value="">— Not mapped —</option>
                {columns.map((col) => (
                  <option key={col} value={col}>{col}</option>
                ))}
              </select>
            </div>
          ))}
        </div>
      </div>

      {/* Data Preview */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
        <h3 className="text-sm font-semibold text-slate-200 mb-3">Data Preview (first {rows.length} rows)</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-slate-700">
                {columns.map((col) => (
                  <th key={col} className="text-left py-2 px-2 text-slate-400 font-medium whitespace-nowrap">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, idx) => (
                <tr key={idx} className="border-b border-slate-800/50">
                  {columns.map((col) => (
                    <td key={col} className="py-2 px-2 text-slate-300 whitespace-nowrap">
                      {String(row[col] ?? '')}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

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
          onClick={onConfirm}
          disabled={!requiredMapped}
          className="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Continue
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}
