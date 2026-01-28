import { Target, Calendar } from 'lucide-react'

type CommitmentsListProps = {
  commitments: string[]
}

export function CommitmentsList({ commitments }: CommitmentsListProps) {
  const extractYear = (text: string): number | null => {
    const match = text.match(/\b(20\d{2})\b/)
    return match ? parseInt(match[1]) : null
  }

  const sortedCommitments = [...commitments].sort((a, b) => {
    const yearA = extractYear(a)
    const yearB = extractYear(b)
    if (yearA && yearB) return yearA - yearB
    if (yearA) return -1
    if (yearB) return 1
    return 0
  })

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
      <h2 className="text-lg font-semibold text-slate-50 mb-4">Environmental Commitments</h2>

      <div className="space-y-3">
        {sortedCommitments.length === 0 ? (
          <p className="text-sm text-slate-500 text-center py-8">No commitments extracted</p>
        ) : (
          sortedCommitments.map((commitment, idx) => {
            const year = extractYear(commitment)
            return (
              <div
                key={idx}
                className="flex items-start gap-3 p-3 rounded-lg border border-slate-800 bg-slate-900/40 hover:bg-slate-900/60 transition-colors"
              >
                <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 shrink-0">
                  <Target className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-slate-200">{commitment}</p>
                  {year && (
                    <div className="flex items-center gap-1 mt-2 text-xs text-slate-400">
                      <Calendar className="h-3 w-3" />
                      <span>Target year: {year}</span>
                    </div>
                  )}
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
