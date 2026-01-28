import { X } from 'lucide-react'

type CompanySelectorProps = {
  reports: string[]
  selected: string[]
  onChange: (selected: string[]) => void
  onCompare: () => void
  isLoading: boolean
}

export function CompanySelector({
  reports,
  selected,
  onChange,
  onCompare,
  isLoading,
}: CompanySelectorProps) {
  const toggleReport = (filename: string) => {
    if (selected.includes(filename)) {
      onChange(selected.filter((f) => f !== filename))
    } else {
      if (selected.length < 4) {
        onChange([...selected, filename])
      }
    }
  }

  const removeReport = (filename: string) => {
    onChange(selected.filter((f) => f !== filename))
  }

  const formatName = (filename: string) => {
    return filename.replace(/\.pdf$/i, '').replace(/[_-]/g, ' ')
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
      <div className="space-y-4">
        <div>
          <label className="text-sm font-medium text-slate-300 mb-2 block">
            Select Reports to Compare (2-4)
          </label>
          <div className="flex flex-wrap gap-2 mb-4">
            {selected.map((filename) => (
              <div
                key={filename}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 text-sm"
              >
                <span>{formatName(filename)}</span>
                <button
                  onClick={() => removeReport(filename)}
                  className="hover:text-emerald-200"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 max-h-48 overflow-y-auto">
          {reports.map((filename) => {
            const isSelected = selected.includes(filename)
            return (
              <button
                key={filename}
                onClick={() => toggleReport(filename)}
                disabled={!isSelected && selected.length >= 4}
                className={`p-3 rounded-lg border text-left text-sm transition-colors ${
                  isSelected
                    ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300'
                    : 'bg-slate-800/50 border-slate-700 text-slate-300 hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed'
                }`}
              >
                {formatName(filename)}
              </button>
            )
          })}
        </div>

        <button
          onClick={onCompare}
          disabled={selected.length < 2 || isLoading}
          className="w-full px-4 py-3 rounded-lg bg-emerald-500 text-emerald-950 font-semibold hover:bg-emerald-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? 'Comparing...' : `Compare ${selected.length} Report${selected.length !== 1 ? 's' : ''}`}
        </button>
      </div>
    </div>
  )
}
