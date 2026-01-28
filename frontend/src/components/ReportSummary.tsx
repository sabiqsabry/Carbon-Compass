import { useState } from 'react'
import { ChevronDown, ChevronUp, FileText } from 'lucide-react'

type SummaryData = {
  executive_summary: string
  section_summaries: Array<{
    section_name: string
    summary: string
  }>
  commitments: string[]
}

type ReportSummaryProps = {
  summary: SummaryData
}

export function ReportSummary({ summary }: ReportSummaryProps) {
  const [expandedSections, setExpandedSections] = useState<Set<number>>(new Set([0]))

  const toggleSection = (idx: number) => {
    const newSet = new Set(expandedSections)
    if (newSet.has(idx)) {
      newSet.delete(idx)
    } else {
      newSet.add(idx)
    }
    setExpandedSections(newSet)
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
      <h2 className="text-lg font-semibold text-slate-50 mb-4">Report Summary</h2>

      {summary.executive_summary && (
        <div className="mb-6 p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
          <h3 className="text-sm font-semibold text-emerald-300 mb-2">Executive Summary</h3>
          <p className="text-sm text-slate-300 leading-relaxed">{summary.executive_summary}</p>
        </div>
      )}

      <div className="space-y-2">
        {summary.section_summaries.length === 0 ? (
          <p className="text-sm text-slate-500 text-center py-8">No section summaries available</p>
        ) : (
          summary.section_summaries.map((section, idx) => {
            const isExpanded = expandedSections.has(idx)
            return (
              <div
                key={idx}
                className="rounded-lg border border-slate-800 bg-slate-900/40 overflow-hidden"
              >
                <button
                  onClick={() => toggleSection(idx)}
                  className="w-full flex items-center justify-between p-4 hover:bg-slate-900/60 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <FileText className="h-4 w-4 text-slate-400" />
                    <span className="text-sm font-medium text-slate-200">{section.section_name}</span>
                  </div>
                  {isExpanded ? (
                    <ChevronUp className="h-4 w-4 text-slate-400" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-slate-400" />
                  )}
                </button>
                {isExpanded && (
                  <div className="px-4 pb-4">
                    <p className="text-sm text-slate-300 leading-relaxed">{section.summary}</p>
                  </div>
                )}
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
