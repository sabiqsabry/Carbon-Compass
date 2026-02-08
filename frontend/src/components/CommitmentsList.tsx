import { useState, useEffect, useRef } from 'react'
import { Target, Calendar, Loader2, Clock } from 'lucide-react'

type CommitmentsListProps = {
  commitments: string[]
  isLoading?: boolean
  needsGeneration?: boolean
}

function ElapsedTimer() {
  const startRef = useRef(0)
  const [elapsed, setElapsed] = useState(0)

  useEffect(() => {
    const now = Date.now()
    startRef.current = now
    const interval = setInterval(() => {
      setElapsed(Math.floor((Date.now() - now) / 1000))
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  const mins = Math.floor(elapsed / 60)
  const secs = elapsed % 60

  return (
    <div className="flex items-center gap-1.5 text-xs text-slate-500">
      <Clock className="h-3 w-3" />
      <span className="tabular-nums">
        {mins > 0 ? `${mins}m ${secs.toString().padStart(2, '0')}s` : `${secs}s`}
      </span>
    </div>
  )
}

export function CommitmentsList({ commitments, isLoading, needsGeneration }: CommitmentsListProps) {
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

      {isLoading ? (
        <div className="flex items-center gap-3 py-8 justify-center">
          <Loader2 className="h-5 w-5 text-emerald-400 animate-spin" />
          <p className="text-sm text-slate-400">Extracting commitments...</p>
          <ElapsedTimer />
        </div>
      ) : needsGeneration ? (
        <p className="text-sm text-slate-500 text-center py-8">
          Commitments will be extracted when you generate the summary above
        </p>
      ) : (
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
      )}
    </div>
  )
}
